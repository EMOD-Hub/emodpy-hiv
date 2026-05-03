# Setup

The tutorials are Python scripts in the `tutorials/` directory of the emodpy-hiv repository. Before running them, prepare your environment using one of the two options below.

=== "Local"

    ### Prerequisites

    - Python 3.13 — see [Installation](../installation.md) for instructions
    - [Docker Desktop](https://www.docker.com/products/docker-desktop) — required by the Container platform used in the tutorials to run EMOD locally

    ### Steps

    1. Clone the emodpy-hiv repository:

        ```
        git clone https://github.com/EMOD-Hub/emodpy-hiv.git
        cd emodpy-hiv
        ```

    2. Create a virtual environment and install emodpy-hiv — follow the [Installation](../installation.md) page.

    3. Start Docker Desktop.

    4. Navigate to the `tutorials/` directory:

        ```
        cd tutorials
        ```

    5. Run a tutorial:

        ```
        python tutorial_1_intro.py
        ```

    The first time you run a tutorial, `emod_hiv.bootstrap.setup()` downloads the EMOD executable
    and schema to the `tutorials/executables/` directory. This may take a few minutes.

=== "Codespaces"

    GitHub Codespaces provides a browser-based development environment with Docker and all
    dependencies pre-configured by the `.devcontainer` setup in this repository.

    !!! warning "Codespaces can cost money"
        GitHub gives each user 120 core-hours per month for free. Beyond that, charges apply.
        See the [GitHub billing documentation](https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-codespaces/about-billing-for-github-codespaces)
        for details. Closing the browser tab does **not** stop your Codespace — make sure to
        stop or delete it when you are done to avoid unnecessary charges.

    ### Steps

    1. Open the [emodpy-hiv repository](https://github.com/EMOD-Hub/emodpy-hiv) on GitHub.

    2. Click the **Code** button, select the **Codespaces** tab, and click **+** to create a
       new codespace on `main`.

    3. Wait for the container to build and for the post-creation `setup.sh` script to finish
       installing dependencies. To check if setup is complete, open a terminal and run
       `pip freeze` — if no packages appear, setup is still running.

    4. In the terminal, navigate to the `tutorials/` directory:

        ```
        cd tutorials
        ```

    5. Run a tutorial:

        ```
        python tutorial_1_intro.py
        ```

    The first time you run a tutorial, `emod_hiv.bootstrap.setup()` downloads the EMOD
    executable and schema to the `tutorials/executables/` directory.

    ### Stopping and deleting a Codespace

    To avoid charges, stop or delete your Codespace when you are done:

    1. Go to the repository page on GitHub.
    2. Click **Code** → **Codespaces** tab.
    3. Find your Codespace, click the **...** ellipsis, and select **Stop Codespace** or **Delete**.
