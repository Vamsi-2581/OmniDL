# OmniDL Browser Extension (video grabber)

Detects the media stream a page is playing (HLS `.m3u8`, DASH `.mpd`, direct `.mp4`) together with the
`Referer` / `Origin` / `User-Agent` headers the server expects, and hands it to the OmniDL desktop app
over `http://127.0.0.1:48911` (local only, nothing leaves your PC).

It does **not** break DRM. Encrypted streams (Widevine/PlayReady) are not downloadable.

## Install

**Microsoft Edge, one click:** run `launch_chrome_with_omnidl.bat` from the repo root. It opens Edge with the
extension pre-loaded in its own profile.

**Chrome / Brave / Edge, manual:**
1. Open `chrome://extensions` (or `edge://extensions`).
2. Turn on **Developer mode**.
3. Click **Load unpacked** and pick this `extension` folder.

> Chrome 137+ ignores the `--load-extension` command-line flag, so in Chrome use "Load unpacked".

## Use

1. Start OmniDL (`OmniDL-Pro.exe` or `python main.py`).
2. Play a video in the browser.
3. Click the floating **Download Video** button or the toolbar icon; the stream opens in OmniDL.
