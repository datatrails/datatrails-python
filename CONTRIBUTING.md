# Contributing to jitsuin-archivist #

Thanks for taking the time to contribute to jitsuin-archivist!

Contributing is not limited to writing code and submitting a PR. Feel free to submit an
[issue](https://github.com/jitsuin-inc/archivist-python/issues/new/choose) or comment on an existing one
to report a bug, provide feedback, or suggest a new feature.

Of course, contributing code is more than welcome! To keep things simple, if you're fixing a small issue,
you can simply submit a PR and we will pick it up. However, if you're planning to submit a bigger PR to implement
a new feature or fix a relatively complex bug, please open an issue that explains the change and the motivation for it.
If you're addressing a bug, please explain how to reproduce it.

## Pull request and git commit guidance

### Opening PRs and organizing commits
PRs should generally address only 1 issue at a time. If you need to fix two bugs, open two separate PRs.
This will keep the scope of your pull requests smaller and allow them to be reviewed and merged more quickly.

When possible, fill out as much detail in the pull request template as is reasonable.
Most important is to reference the GitHub issue that you are addressing with the PR.

**NOTE:** GitHub has
[a feature](https://docs.github.com/en/github/managing-your-work-on-github/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword)
that will automatically close issues referenced with a keyword (such as "Fixes") by a PR or commit once the PR/commit is merged.
Don't use these keywords. We don't want issues to be automatically closed. We want our testers to independently verify and close them.

Generally, pull requests should consist of a single logical commit.
However, if your PR is for a large feature, you may need a more logical breakdown of commits.
This is fine as long as each commit is a single logical unit.

### Writing good commit messages
Git commit messages should explain the how and why of your change and be separated into a brief subject line
followed by a more detailed body. When in doubt, follow this guide for good commit messages and
you can’t go wrong: https://chris.beams.io/posts/git-commit/.

One particularly useful point made in the above guide is regarding commit subject lines:

> A properly formed Git commit subject line should always be able to complete the following sentence:
> 
> - If applied, this commit will <ins>your subject line here</ins>

A simple but effective convention to follow for commits is the “problem / solution” pattern. It looks like this:
```
<Subject>

Problem: <Statement of problem>

Solution: <Statement of solution>
```

As an example, here is a commit taken from the rancher/rancher repo:
```
commit b71ce2892eecb7c87a5212e3486f1de899a694aa
Author: Dan Ramich <danold215@gmail.com>
Date:   Tue Jun 19 11:56:52 2018 -0700

    Add Validator for RoleTemplate

    Problem:
    Builtin RoleTemplates can be updated through the API

    Solution:
    Add a Validator to ensure the only field that can be changed on a
    builtin RoleTemplate is 'locked'
```

### Reviewing, addressing feedback, and merging
Generally, pull requests need two approvals from maintainers to be merged.

When addressing review feedback, it is helpful to the reviewer if additional changes are made in new commits.
This allows the reviewer to easily see the delta between what they previously reviewed and the changes you added
to address their feedback.

Once a PR has the necessary approvals, it can be merged.
Here’s how the merge should be handled:
- All PR's should use the “Squash and merge” option.
- Commits and their messages should be consistent - each commit in the PR should form a logical unit with working code. 
- The first change requested by a Jitsuin reviewer will be to reorganise the commits into a clean logical structure.
- The smaller a PR the more likely and more easily that the change will be approved.
- Any changes requested by a reviewer should be committed as a 'fixup' commit against the original commit in the PR.
- Once approval is granted any 'fixup' commits should be merged into their respective commits using 'git rebase -i --autosquash'.

## Developer Certificate Of Origin ##

To contribute to this project, you must agree to the Developer Certificate of Origin (DCO) for each commit you make.
The DCO is a simple statement that you, as a contributor, have the legal right to make the contribution.

See the [DCO](DCO) file for the full text of what you must agree to.

To signify that you agree to the DCO for a commit, you add a line to the git
commit message:

```txt
Signed-off-by: Jane Smith <jane.smith@example.com>
```

In most cases, you can add this signoff to your commit automatically with the
`-s` flag to `git commit`. Please use your real name and a reachable email address.
