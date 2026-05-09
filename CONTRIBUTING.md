# Contributing to emodpy-hiv

Welcome! We are thrilled you are interested in contributing to emodpy-hiv.
This document will help you get started.

Please see the guidelines below to provide feedback or contribute to emodpy-hiv
code. Note that we make no representations that the code works as intended or
that we will provide support, address issues that are found, or accept pull
requests.

## Getting started

Contributions to this project are
[released](https://help.github.com/articles/github-terms-of-service/#6-contributions-under-repository-license)
to the public under the project's open source [license](https://github.com/EMOD-Hub/emodpy-hiv/blob/main/LICENSE).

Review the [documentation](https://emod.idmod.org/emodpy-hiv) before you begin.
Additionally, this content is also included in the following README files:

- [Project README](https://github.com/EMOD-Hub/emodpy-hiv/blob/main/README.md): Setup and project overview.

## Discussions

Have a comment or a question? Check out our [Discussions](https://github.com/orgs/EMOD-Hub/discussions) space.

## Contribution types

We welcome the following types of contributions:

1. [Issues](https://github.com/EMOD-Hub/issues-and-discussions/issues):
   - Bug reports.
   - Feature requests.

2. Pull requests:
   - Tests reproducing an issue.
   - Bug fixes.
   - Code to resolve an issue.
   - Documentation improvements in the [docs](https://github.com/EMOD-Hub/emodpy-hiv/tree/main/docs) folder.

All external communication about these contribution efforts is currently
occurring on GitHub.

## Request new features or report bugs

If you notice unexpected behavior or a limitation in emodpy-hiv, follow the
steps below before requesting a new feature or reporting a bug.

1. First, review the [emodpy-hiv documentation](https://emod.idmod.org/emodpy-hiv)
   to see if there is already functionality that supports what you want to do.
2. Search the [existing issues](https://github.com/EMOD-Hub/issues-and-discussions/issues)
   to see if there is already one that contains your feedback. If there is,
   **add a thumbs up reaction** to convey your interest in the issue being addressed.
   This helps the team gauge interest without the noise of comments, which trigger
   notifications to all watchers. Comments should be used only if you have new and
   useful information to share.

### Open a feature request

When opening an issue to request a new feature, do the following:

1. Provide a clear and descriptive title for the issue.
2. Include as many details as possible in the body. Fully explain your use case,
   the problems you're hitting, and the solutions you'd like to see to address
   those problems.

### Report a bug

When opening an issue to report a bug, explain the problem and include additional
details to help us reproduce the problem:

1. Describe the specific steps that led to the problem you encountered with as
   many details as possible. Don't just say what you did, but explain how you did it.
2. Provide specific examples to demonstrate the steps, such as links to files or
   projects, code snippets, or screenshots. Please use Markdown code blocks for
   code snippets.
3. Describe the behavior you observed after following the steps and point out
   exactly what the problem with that behavior is, including explaining what you
   expected to see instead and why.

## Submit a pull request

To contribute directly to emodpy-hiv code, do the following:

1. Fork and clone the emodpy-hiv repository.
2. Install emodpy-hiv on your machine (see [Developer installation](#developer-installation) below).
3. Create a new branch:

   ```
   git checkout -b my-branch-name
   ```

4. Make your code changes, including a descriptive commit message.
5. Push to your fork and submit a pull request.

Although we make no guarantees that a submitted pull request will be accepted, PRs
that meet the following criteria are more likely to be merged:

- Up-to-date with main with no merge conflicts
- Self-contained
- Fix a demonstrable limitation or bug
- Follow the current code style
- If the PR introduces a new feature, it has complete
  [Google style docstrings](https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html)
  and comments, and a test demonstrating its functionality
- Otherwise, sample code demonstrating old and new behavior (this can be in the PR
  comment on GitHub, not necessarily committed in the repo)

If you have additional questions or comments, contact idmsupport@gatesfoundation.org.

## Developer installation

First, fork and clone the repository, then navigate into it:

```
git clone https://github.com/EMOD-Hub/emodpy-hiv.git
cd emodpy-hiv
```

**Option 1** — editable install (changes take effect immediately):

```
pip install -e .
```

**Option 2** — build a wheel (required if testing packaging):

```
pip install build
python -m build
pip install dist\emodpy_hiv-XXXX.whl
```

## Resources

- [Using pull requests](https://help.github.com/articles/about-pull-requests/)
- [GitHub help](https://help.github.com)
