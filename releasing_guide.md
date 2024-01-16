# Releasing a new eXSpy version

To publish a new eXSpy release do the following steps:

## Preparation

- In a pull request, prepare the release by running the `prepare_release.py` python script (e.g. `python prepare_release.py 0.2`) , which will do the following:
  - update the release notes in `CHANGES.rst` by running `towncrier`,
  - update the `setuptools_scm` fallback version in `pyproject.toml` (for a patch release, this will stay the same).
- Check release notes
- Let that PR collect comments for a day to ensure that other maintainers are comfortable
  with releasing
- Set correct date and version number in `CHANGES.rst`

## Tag and Release

- Create a tag e.g. `git tag -a v0.1.1 -m "eXSpy version 0.1.1"`
- Push tag to user fork for a test run `git push origin v0.1.1`. Will run the release
  workflow without uploading to PyPi
- Push tag to eXSpy repository to trigger release `git push upstream v0.1.1`
  (this triggers the GitHub action to create the sdist and wheel and upload to
  PyPi automatically). :warning: this is a point of no return :warning:

## Post-release action

- Merge the PR

## Follow-up

- Tidy up and close corresponding milestone or project
- A PR to the conda-forge feedstock will be created by the conda-forge bot
