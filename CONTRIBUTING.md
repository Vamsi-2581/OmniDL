# Contributing to OmniDL

Thanks for helping!

## Report a bug

Open an issue with the **Bug report** template: OmniDL version, Windows version, the URL's site (not a
private link), what you expected, and what happened. A crash log, if there is one, is in
`%USERPROFILE%\.omni_downloader\crash.log`.

## Site not working?

Most site support comes from [yt-dlp](https://github.com/yt-dlp/yt-dlp). First try updating it
(`pip install -U yt-dlp`). If yt-dlp itself cannot download the link, please report it to yt-dlp.

## Pull requests

1. Fork and create a branch.
2. `pip install -r requirements.txt pytest`
3. Make your change and add a test where it makes sense.
4. `python -m pytest tests -q` must pass.
5. Open the PR with a short description of what and why.

Good first issues are labelled [`good first issue`](https://github.com/noormdgolam/OmniDL/labels/good%20first%20issue).

By contributing you agree your code is released under the GPL-3.0 licence of this project.
