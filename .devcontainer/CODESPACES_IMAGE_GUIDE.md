# Choosing a Base Image for Codespaces (and How to Test & Deploy It)

This doc explains how to pick a GitHub Codespaces **base image** for our dev container, how to **test** candidates, and how to **deploy** the chosen image.

---

## 1) Goals & constraints

- **Python version:** Must include **Python 3.9** (current supported version for our package).
- **Features needed (Dev Container):**
  ```json
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {},
    "ghcr.io/devcontainers/features/node:1": { "version": "20" }
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.debugpy",
        "esbenp.prettier-vscode",
        "redhat.vscode-yaml"
      ]
    }
  }
  ```
- **Storage:** Free GitHub accounts have **32 GB** total storage; prefer a **smaller image** to keep Codespaces startup/setup time and storage usage low. The *universal* image is too large.
- **Functionality we care about:**
  - Docker-in-Docker (DinD) works (i.e., you can run containers inside the Codespace).
  - Python debugging (debugpy) works in VS Code.
  - Plotting works and you can **view** plots (e.g., matplotlib in notebooks or interactive windows).
  - JSON/YAML authoring (formatting, schema help) works via VS Code extensions.
- **Compatibility note:** Do **not** use `mcr.microsoft.com/devcontainers/python:3.9` based on Debian **“trixie”**; it no longer supports the `moby` packages required by the Docker feature (DinD). We need an image where the Docker feature can install moby successfully.

---

## 2) Where to look for images

Start here (review tags and their Dockerfiles to see what’s included):
- Microsoft Dev Containers Python images:  
  https://mcr.microsoft.com/en-us/artifact/mar/devcontainers/python/about
- Official Python images (various distros):  
  https://hub.docker.com/_/python

**Tip:** Prefer images whose base distro and repos support the `moby` packages used by Dev Containers’ `docker-in-docker` feature.

---

## 3) Selection criteria (ranked)

1. **DinD compatibility** (must): can the `docker-in-docker:2` feature install and run Docker/moby?
2. **Python 3.9 present** (must) with a healthy scientific/plotting path (we can install `matplotlib`, `plotly`, etc.).
3. **Image size** (smaller is better). Target ≲ **~1.05 GB** (around our current image size) if possible.
4. **Setup time** (shorter is better). Prefer images that already include common tooling to reduce post-create installs.
5. **Node 20** via devcontainer feature works.
6. **VS Code experience**: Python debugging, JSON/YAML formatting, and Jupyter/plot viewing run smoothly.

---

## 4) Identify a few candidates

Pick **2–4** images that:
- Are Linux-based,
- Have **Python 3.9** built-in,
- Are **not** on Debian “trixie” (or otherwise incompatible with moby),
- Look reasonably sized (check tags like `-slim`, `-bookworm`, `-bullseye`, `-jammy`, etc., as appropriate).

Record them in a short table:

| Candidate | Base distro | Python | Tag | Approx. size (local) | Notes |
|---|---|---|---|---:|---|
| e.g., `python:3.9-slim-bullseye` | Debian bullseye | 3.9 | slim |  |  |
| e.g., `mcr.microsoft.com/devcontainers/base:ubuntu-22.04` + py 3.9 | Ubuntu 22.04 | via apt/pyenv |  |  | May need Python install step |
| … | … | … | … | … | … |

---

## 5) Local quick checks (optional but recommended)

You can sanity check image **size** and **basic run** locally before touching Codespaces:

```bash
# Pull the image
docker pull <image:tag>

# Check size
docker images | grep <image>

# Start a container and poke around
docker run -it --rm <image:tag> bash

# Inside the container:
python3 --version
pip --version
```

If Python 3.9 isn’t present on an otherwise good candidate, consider how costly it is to add (and whether that hurts setup time).

---

## 6) Codespaces test plan

Create a temporary **testing branch** and wire the candidate into `devcontainer.json`. Example:

```json
{
  "name": "Our Codespace",
  "image": "<CANDIDATE_IMAGE:TAG>",
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {},
    "ghcr.io/devcontainers/features/node:1": { "version": "20" }
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.debugpy",
        "esbenp.prettier-vscode",
        "redhat.vscode-yaml"
      ]
    }
  },
  "postCreateCommand": "bash ./.devcontainer/setup.sh"
}
```

Then **create a Codespace** from your testing branch and run through this **checklist**:

### Startup & environment
1. **Codespace starts successfully?** No build errors, no feature install failures.
2. `python -V` shows **3.9.x**.
3. **Docker feature running?**
   ```bash
   docker --version
   docker info
   docker run --rm hello-world
   ```
   - If `docker info` fails or moby packages can’t be installed, this image is a **NO**.

### Python & dependencies
4. `pip freeze` shows `emodpy` (and related internal dependencies) after setup. If not, confirm our normal bootstrap scripts run as expected.
5. **Debugging** works:
   - Set a breakpoint in a simple Python file and start the **Python: Current File** debug config.

### Plotting & notebooks
6. Install and test plotting (if not present):
   ```bash
   pip install matplotlib
   ```
   ```PY
   import matplotlib.pyplot as plt
   plt.plot([0,1,2],[0,1,4])
   plt.title("Sanity Plot")
   plt.savefig("sanity.png")
   ```
   - Verify you can **view** `sanity.png` in VS Code.
   - If using notebooks, create a quick `.ipynb`, run a simple plot cell, confirm inline output.


### JSON/YAML authoring
7. Open a `.json` and `.yaml` file:
   - Confirm **formatting** (Prettier for JSON, Red Hat YAML extension working).
   - Confirm basic schema/hover works where applicable.

### Storage & size
8. Check image footprint and container storage usage (look at `docker images`, examine the Codespace disk usage if needed). Watch for **storage warnings** in Codespaces.

### DinD deeper check (optional)
9. Try running a small containerized task used by our examples/tutorials to ensure Docker-in-Docker behaves similarly to our current setup.

### Anything else
10. Note **any other problems** (networking, permissions, locale, missing build tools, etc.).

Capture results in a short matrix:

| Check | Pass/Fail | Notes |
|---|---|---|
| Start success |  |  |
| Docker DinD |  |  |
| Python 3.9 |  |  |
| pip freeze (emodpy deps) |  |  |
| Debugpy works |  |  |
| Plotting works |  |  |
| JSON/YAML formatting |  |  |
| Storage OK |  |  |
| Other issues |  |  |

---

## 7) Troubleshooting tips

- **Docker feature fails on moby:** Your base distro may not provide supported `moby` packages (e.g., Debian **trixie**). Pick a different base (e.g., Debian **bullseye/bookworm** or Ubuntu **20.04/22.04**) where moby installs cleanly.
- **Plot viewing doesn’t work:** Ensure you save plots to files (e.g., `plt.savefig(...)`) and open them in VS Code, or use Jupyter notebooks in the Codespace for inline output.
- **Setup time too long:** Prefer images with more essentials pre-installed (but still small). Consider adding a lightweight `postCreateCommand` rather than heavy installs.
- **Disk warnings:** Remove unneeded packages/layers or choose a slimmer tag (e.g., `-slim`). Avoid the universal image.

---

## 8) Decide & document

From your tested candidates, pick the best **balance** of:
- DinD reliability,
- Python 3.9 availability,
- Small image size and fast startup,
- Smooth VS Code experience.

---

## 9) Deploy the chosen image

1. **Update** `devcontainer.json` on a feature branch with the selected `"image": "<final image:tag>"`.
2. **Push** the branch and create a **PR** with your test notes.
3. After approval, **merge** to default branch.
4. (Optional) **Tag/release** if our workflow depends on versioning the dev environment.
5. **Announce** in the team channel with quick tips and any breaking changes.

---

## 10) Appendix

### A. `devcontainer.json` template (drop-in)

```json
{
  "name": "Our Codespace",
  "image": "<FINAL_IMAGE:TAG>",
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {},
    "ghcr.io/devcontainers/features/node:1": { "version": "20" }
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.debugpy",
        "esbenp.prettier-vscode",
        "redhat.vscode-yaml"
      ]
    }
  },
  "postCreateCommand": "bash ./.devcontainer/setup.sh"
}
```

### B. Handy commands

```bash
# Size check (local)
docker images | sort

# Quick plot check (inside Codespace)
python - << 'PY'
import matplotlib.pyplot as plt
plt.plot([0,1,2],[0,1,4]); plt.title("Sanity Plot"); plt.savefig("sanity.png")
PY
```

---

## 11) Summary

- Avoid Debian **trixie**–based Python 3.9 devcontainer images due to **moby**/Docker incompatibility.
- Target an image ≲ **~1.05 GB**, with **Python 3.9**, and seamless **DinD**, **debugging**, **plotting**, and **JSON/YAML** workflows.
- Test candidates in a dedicated branch via Codespaces using the **checklist**, then document your decision and **deploy** via PR.
