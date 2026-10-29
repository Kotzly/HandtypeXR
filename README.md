# HandtypeXR

A hand-gesture keyboard for Meta Quest 3 on PC VR, inspired by fingerspelling.
Handshapes are read from the Quest's hand tracking, turned into letters, and sent
to Windows as keystrokes, so it works in any app on the PC.

**Status: feasibility spike.** Nothing is recognized yet. The only script,
`spike.py`, checks whether the idea can work at all.

## The question the spike answers

Can a background program on the PC keep reading your hand skeleton while a VR
game has focus? If yes, a system-wide keyboard is possible. If no, the project
has to live inside a single app.

## How the pieces connect

```
Quest 3 (hand tracking)
   │  Steam Link app streams the headset to the PC over Wi-Fi,
   │  including your hand skeleton
   ▼
PC: SteamVR  ──►  spike.py (reads the skeleton as a SteamVR overlay)
```

Nothing of ours runs on the Quest. The Quest only runs Steam Link. Everything
else runs on the PC.

**The Quest must stay connected to the PC the whole time.** spike.py reads hands
through SteamVR, so if Steam Link disconnects or SteamVR closes, there is no data.

## What you need

| Where | What |
|---|---|
| PC | Windows 10/11, a VR-capable GPU, Steam, SteamVR, Python 3.9+ (64-bit) |
| Quest 3 | The **Steam Link** app from the Meta Horizon Store |
| Network | PC and Quest on the same network. PC on Ethernet, Quest on 5 GHz or 6 GHz Wi-Fi works best |

You do **not** need developer mode on the Quest, a Meta developer account,
or a USB cable.

### Which PC connection to use

| Connection | Use it? |
|---|---|
| **Steam Link** (free, Valve) | **Yes, use this.** It forwards hand tracking to SteamVR. |
| Virtual Desktop (paid) | Should work too. In its settings turn on Hand tracking and *Emulate Index Controllers*, and pick SteamVR as the OpenXR runtime. |
| Meta Quest Link / Air Link | **No.** It doesn't forward hand tracking to SteamVR the way this needs. |

## One-time setup

### On the PC

1. Install Steam, then install **SteamVR** from the Steam store.
2. Install Python 3.9+ (64-bit). During install, tick "Add Python to PATH".
3. Download this repo and install the one dependency:
   ```
   git clone https://github.com/Kotzly/HandtypeXR
   cd HandtypeXR
   pip install -r requirements.txt
   ```

### On the Quest 3

1. Install **Steam Link** from the Meta Horizon Store.
2. Turn on hand tracking: *Settings > Movement tracking > Hand and body tracking*.
3. Allow Steam Link to use it: *Settings > Privacy & safety > App permissions >
   Hand and body tracking*, and make sure Steam Link is allowed.

Menu names move around between Quest updates; if a path doesn't match, search
Settings for "hand tracking".

### Pair the headset (first time only)

1. On the PC, open Steam and stay logged in.
2. On the Quest, open Steam Link. It finds your PC on the network.
3. Select the PC. A code appears in the headset; enter it on the PC when Steam asks.

## Running the test (every time)

1. **PC:** open Steam.
2. **Quest:** open Steam Link and connect to the PC. SteamVR starts on the PC
   automatically. Leave it connected.
3. **Quest:** put the controllers down so the headset switches to hand tracking
   (you should see your hands instead of controllers).
4. **PC:** in a terminal in the HandtypeXR folder, run:
   ```
   python spike.py
   ```
   To also save the data (useful later for training):
   ```
   python spike.py --csv samples.csv
   ```
5. **Check without a game:** curl and open your fingers. Each hand shows `ON`
   and five bars (thumb to pinky) that fill as you curl.
6. **Check with a game:** start any VR game from SteamVR while spike.py keeps
   running. The `scene_pid` number changes when the game takes focus.
   **The bars must keep moving.**

Stop with Ctrl+C. You can see the terminal from inside the headset through the
SteamVR desktop view, or take the headset off to look.

### If the bars stay `off`

SteamVR may not have connected the skeleton to this script. Fix it once:

1. In SteamVR: *Settings > Controllers > Manage Controller Bindings*.
2. Pick this script in the app list (it appears while spike.py is running).
3. Choose a binding that maps both hand skeletons ("HandtypeXR spike - skeleton only"),
   or create one that binds the left and right skeleton.

The included binding covers the `knuckles` (Index) and `oculus_touch`
controller types. The type Steam Link reports for tracked hands may be different,
which is why this step can be needed.

## What to record

| Setup | Bars move without a game | Bars move with a game in focus |
|---|---|---|
| Steam Link | | |
| Virtual Desktop | | |

- **Both columns yes:** the system-wide keyboard is possible. Next step is recognition.
- **Second column no:** an overlay can't read hands behind a game. The project
  moves to an in-app keyboard instead.

## Troubleshooting: Linux PC with ALVR

Steam Link isn't available for SteamVR on Linux, so on a Linux PC the Quest
connects through [ALVR](https://github.com/alvr-org/ALVR) instead. Getting
ALVR to show a picture took several fixes. This is the setup that ended up
working, on Ubuntu 22.04 with SteamVR 2.17.10 and a Quest 3, as of October 2026.
Reading the hand skeleton through ALVR with spike.py hasn't been tested yet.

### 1. Pick the GPU (laptops with Intel + NVIDIA)

ALVR has to render and encode video on the same GPU. If the NVIDIA GPU has no
hardware video encoder (NVENC), for example a GeForce 940MX, run everything
on the Intel GPU:

```
sudo prime-select intel
```

Reboot afterwards. To get the NVIDIA GPU back for other games, run
`sudo prime-select on-demand` and reboot.

### 2. Update Mesa (the Intel/AMD graphics driver)

Ubuntu 22.04 ships Mesa 23.2, which is too old for ALVR's frame capture. Install
Mesa 25 from the kisak *turtle* PPA (the `kisak-mesa` PPA no longer publishes
packages for 22.04):

```
sudo add-apt-repository ppa:kisak/turtle
sudo apt update && sudo apt full-upgrade
```

Check that `apt-cache policy mesa-vulkan-drivers` shows 25.x, then reboot.

### 3. Install the right ALVR version on the PC

Use the nightly **[v21.0.0-dev14+nightly.2026.10.03](https://github.com/alvr-org/ALVR-nightly/releases/tag/v21.0.0-dev14%2Bnightly.2026.10.03)**.
Other versions don't work with this setup:

- **Stable v20.14.1** makes SteamVR crash about a second after startup. It doesn't
  handle `vkWaitForPresentKHR`, which SteamVR 2.17.7 and later call every frame
  (fixed in [ALVR #3357](https://github.com/alvr-org/ALVR/pull/3357)).
- **Nightlies from 2026-10-04 on** switched Linux to a new "driver direct mode"
  ([ALVR #3398](https://github.com/alvr-org/ALVR/pull/3398)). On Intel GPUs it
  crashes SteamVR or streams black ([ALVR #3420](https://github.com/alvr-org/ALVR/issues/3420)).

Install it from the ALVR Launcher (*Add version*, channel Nightly), or download
`alvr_streamer_linux.tar.gz` from that release and extract it. Use only this
version's dashboard (`alvr_streamer_linux/bin/alvr_dashboard`): opening another
ALVR version's dashboard registers that version's driver with SteamVR instead.

### 4. Install the matching ALVR app on the Quest

The Quest app must be the same version. Download `alvr_client_android.apk`
from the same release and install it over USB with adb. This needs developer
mode on the Quest.

1. Let your user access the Quest over USB (Linux blocks it by default):
   ```
   echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="2833", MODE="0666", GROUP="plugdev"' | sudo tee /etc/udev/rules.d/51-meta-quest.rules
   sudo udevadm control --reload-rules && sudo udevadm trigger
   ```
2. Plug in the Quest, put it on, and accept **Allow USB debugging**
   (tick *Always allow*). `adb devices` should list it as `device`.
3. Remove any older ALVR app and install the new one:
   ```
   adb uninstall alvr.client
   adb install alvr_client_android.apk
   ```
   The nightly installs as `alvr.client.dev`, a separate app in the Quest library.

The ALVR Launcher ships adb in `~/.local/share/ALVR-Launcher/installations/<version>/bin/platform-tools/`.
If its *Install APK* button does nothing, the missing udev rule from step 1 is
the usual cause.

### 5. Set SteamVR's launch options

In Steam, right-click SteamVR > *Properties* > *Launch Options*:

```
~/.local/share/Steam/steamapps/common/SteamVR/bin/vrmonitor.sh %command%
```

Without it, SteamVR runs ALVR's driver inside Steam's container, and the
compositor (which runs outside it) can't reach ALVR's video encoder. The
headset then gets sound but shows only black. SteamVR's log warns that it is
"NOT running in a Steam for Linux pressure-vessel container runtime"; with this
ALVR version that is expected.

### 6. Connect

1. Start the 10.03 ALVR dashboard on the PC.
2. Open ALVR on the Quest. When the headset appears in the dashboard, click **Trust**.
3. Click **Launch SteamVR** in the dashboard.

On a weak GPU, lower the load in the dashboard under *Settings > Video*: set
*Transcoding view resolution* to Scale 0.5, the refresh rate to 72 Hz, and
the codec to H264. Expect a low-resolution, choppy picture on integrated
graphics.

### Where to look when it fails

| Symptom | Likely cause | Fix |
|---|---|---|
| SteamVR crashes about a second after "Startup Complete" | ALVR older than 2026-08-25 | Step 3 |
| SteamVR crashes at "Creating samplers" in `libvulkan_intel.so` | ALVR nightly from 2026-10-04 or later | Step 3 |
| Quest shows black but plays sound | SteamVR running inside Steam's container | Step 5 |
| `adb devices` says `no permissions` | Missing udev rule | Step 4 |
| `adb devices` says `unauthorized` | USB debugging not accepted in the headset | Step 4 |

Logs: SteamVR writes to `~/.local/share/Steam/logs/` (`vrcompositor.txt`,
`vrserver.txt`); crashes also appear in `journalctl -k | grep segfault`. To get
ALVR's own log, turn on *Settings > Extra > Logging > Log to disk* in the
dashboard; it writes `~/alvr_session_log.txt`.

## Files

| File | What it is |
|---|---|
| `spike.py` | The test. Prints live finger curl per hand, optionally logs to CSV. |
| `actions.json` | Tells SteamVR this script wants the left and right hand skeletons. |
| `bindings_skeleton.json` | Default binding: skeletons only, no buttons, so it doesn't interfere with the game. |
