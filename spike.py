"""
Feasibility spike for HandtypeXR.

Question it answers: can a background SteamVR overlay app keep reading
hand-tracking skeleton data while another VR app (a game) has focus?

Run it, start any VR app, and watch whether the finger-curl bars keep moving.

    python spike.py              # print live finger curl
    python spike.py --csv out.csv  # also log every sample (useful as training data later)
"""

import argparse
import csv
import os
import sys
import time

import openvr

HERE = os.path.dirname(os.path.abspath(__file__))
FINGERS = ["thumb", "index", "middle", "ring", "pinky"]


def bar(x, width=10):
    x = max(0.0, min(1.0, x))
    n = round(x * width)
    return "#" * n + "." * (width - n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", help="write samples to this CSV file")
    ap.add_argument("--hz", type=float, default=10.0, help="print/log rate")
    args = ap.parse_args()

    # Overlay = runs alongside whatever scene app (game) is in front.
    try:
        openvr.init(openvr.VRApplication_Overlay)
    except Exception as e:
        sys.exit(f"Could not connect to SteamVR ({e}). Is the headset connected and SteamVR running?")
    vrinput = openvr.VRInput()
    vrinput.setActionManifestPath(os.path.join(HERE, "actions.json"))

    action_set = vrinput.getActionSetHandle("/actions/spike")
    skeletons = {
        "L": vrinput.getActionHandle("/actions/spike/in/skeleton_left"),
        "R": vrinput.getActionHandle("/actions/spike/in/skeleton_right"),
    }
    active_sets = (openvr.VRActiveActionSet_t * 1)()
    active_sets[0].ulActionSet = action_set

    writer = None
    if args.csv:
        f = open(args.csv, "w", newline="")
        writer = csv.writer(f)
        writer.writerow(
            ["t", "scene_pid", "hand", "active"]
            + [f"curl_{n}" for n in FINGERS]
            + [f"splay_{i}" for i in range(4)]
        )

    print("Running. Start a VR game and check whether the bars keep moving. Ctrl+C to stop.\n")
    t0 = time.time()
    try:
        while True:
            vrinput.updateActionState(active_sets)

            try:
                scene_pid = openvr.VRApplications().getCurrentSceneProcessId()
            except Exception:
                scene_pid = -1

            line = [f"t={time.time() - t0:6.1f}s scene_pid={scene_pid:>6}"]
            for hand, handle in skeletons.items():
                try:
                    active = bool(vrinput.getSkeletalActionData(handle).bActive)
                    s = vrinput.getSkeletalSummaryData(handle, openvr.VRSummaryType_FromDevice)
                    curl = list(s.flFingerCurl)
                    splay = list(s.flFingerSplay)
                except Exception as e:  # inactive action or no data
                    active, curl, splay = False, [0.0] * 5, [0.0] * 4
                    err = type(e).__name__
                else:
                    err = ""

                line.append(
                    f"{hand}:{'ON ' if active else 'off'} "
                    + " ".join(bar(c, 5) for c in curl)
                    + (f" ({err})" if err else "")
                )
                if writer:
                    writer.writerow([f"{time.time() - t0:.3f}", scene_pid, hand, int(active)] + curl + splay)

            print(" | ".join(line), flush=True)
            time.sleep(1.0 / args.hz)
    except KeyboardInterrupt:
        pass
    finally:
        openvr.shutdown()


if __name__ == "__main__":
    sys.exit(main())
