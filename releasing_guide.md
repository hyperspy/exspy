# Releasing a new exSpy version

To publish a new exSpy release do the following steps:

## Preparation

- Create a new PR to the 'main' branch for the release process, e.g. `release_v0.1.1`
- Make sure to have the code ready, including changelog
- Let that PR collect comments for a day to ensure that other maintainers are comfortable
  with releasing
- Set correct date and version number in `CHANGES.rst`

## Tag and Release

- Create a tag e.g. `git tag -a v0.1.1 -m "exSpy version 0.1.1"`
- Push tag to user fork for a test run `git push origin v0.1.1`. Will run the release
  workflow without uploading to PyPi
- Push tag to exSpy repository to trigger release `git push upstream v0.1.1`
  (this triggers the GitHub action to create the sdist and wheel and upload to
  PyPi automatically). :warning: this is a point of no return :warning:

## Post-release action

- Update version in other branches if necessary
- Prepare `CHANGES.rst` for development by adding `UNRELEASED` headline
- Merge the PR

## Follow-up

- Tidy up and close corresponding milestone or project
- A PR to the conda-forge feedstock will be created by the conda-forge bot
