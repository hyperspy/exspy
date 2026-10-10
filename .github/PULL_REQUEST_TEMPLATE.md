### Requirements
* Read the [contributing guidelines](https://github.com/hyperspy/exspy/blob/main/CONTRIBUTING.rst).
* Fill out the template; it helps the review process and it is useful to summarise the PR.
* This template can be updated during the progression of the PR to summarise its status. 

*You can delete this section after you read it.*

### Description of the change
A few sentences and/or a bulleted list to describe and motivate the change:
- Change A.
- Change B.
- etc.

### AI-assisted contribution?
- [ ] Is this an AI-assisted contribution? If yes, and non-trivial, link to the accepted proposal:
      - [ ] N/A (human-only contribution or trivial change)
      - [ ] Proposal accepted: <link to PR in hyperspy/hyperspy-proposals>

### Progress of the PR
- [ ] if AI-assisted, ``Assisted-by: <tool>:<model>`` in every commit and no AI ``Co-authored-by:`` trailer,
- [ ] Change implemented (can be split into several points),
- [ ] docstring updated (if appropriate),
- [ ] update user guide (if appropriate),
- [ ] added tests,
- [ ] add a changelog entry in the `upcoming_changes` folder (see [`upcoming_changes/README.rst`](https://github.com/hyperspy/exspy/blob/main/upcoming_changes/README.rst)),
- [ ] Check formatting of the changelog entry (and eventual user guide changes) in the `docs/readthedocs.org:exspy` build of this PR (link in github checks)
- [ ] ready for review.

### Minimal example of the bug fix or the new feature
```python
import exspy
import numpy as np

s = exspy.signals.EELSSpectrum(np.arange(100).reshape(10, 10))
# Your new feature...
```


