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

## Files

| File | What it is |
|---|---|
| `spike.py` | The test. Prints live finger curl per hand, optionally logs to CSV. |
| `actions.json` | Tells SteamVR this script wants the left and right hand skeletons. |
| `bindings_skeleton.json` | Default binding: skeletons only, no buttons, so it doesn't interfere with the game. |
