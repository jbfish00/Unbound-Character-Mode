# Sourced by every test runner: moves the emulator + all synthetic input
# onto a private Xvfb display so tests NEVER touch the user's screen,
# focus, or keyboard.
#
# Usage (in a runner, before launching mgba-qt):
#   . "$HERE/headless_display.sh"
# Cleanup: headless_display_stop (also wired into your trap).
#
# ⚠️ THIS FILE USED TO LOSE A RACE WITH ITSELF, roughly one run in three, and
# the failure did not look like a display problem. It was:
#
#   HEADLESS_DISPLAY=":$((90 + $$ % 8))"
#   Xvfb "$HEADLESS_DISPLAY" ... &
#   sleep 1
#
# Three separate defects, each measured:
#
#   1. `sleep 1` is a guess, not a wait. Under load Xvfb needs longer, mgba-qt
#      then starts with no display and ABORTS ("could not connect to display
#      :96" / "no Qt platform plugin could be initialized").
#   2. The display number came from `$$ % 8`, so only 8 slots existed and two
#      runners could pick the same one. A second Xvfb on a taken display exits
#      immediately -- and `sleep 1` swallowed that too.
#   3. ⭐ Neither failure was REPORTED. The runner carried on and died later at
#      `xdotool search --pid` with "mgba window not found", which reads like an
#      emulator bug. A whole suite run was diagnosed as a Character Mode
#      regression on the strength of that line.
#
# So: pick a display nobody owns, WAIT for it to answer, and fail loudly and
# immediately if it never does.

headless_display_start() {
    local n sock
    HEADLESS_DISPLAY=""
    # 90-129: a wide range, and each candidate is checked for an existing
    # socket AND probed, so a stale server from a killed run is skipped rather
    # than collided with.
    for n in $(seq 90 129); do
        sock="/tmp/.X11-unix/X$n"
        [ -e "$sock" ] && continue
        [ -e "/tmp/.X$n-lock" ] && continue
        if ! DISPLAY=":$n" xdpyinfo >/dev/null 2>&1; then
            HEADLESS_DISPLAY=":$n"
            break
        fi
    done
    if [ -z "$HEADLESS_DISPLAY" ]; then
        echo "headless_display: no free X display in :90-:129 -- stale Xvfb servers?" >&2
        return 1
    fi

    Xvfb "$HEADLESS_DISPLAY" -screen 0 480x320x24 -nolisten tcp >/dev/null 2>&1 &
    HEADLESS_XVFB_PID=$!

    # Wait for the display to actually answer, up to 15s. This is the fix for
    # defect 1: a readiness check, not a duration.
    local waited=0
    while [ "$waited" -lt 150 ]; do
        if DISPLAY="$HEADLESS_DISPLAY" xdpyinfo >/dev/null 2>&1; then
            export DISPLAY="$HEADLESS_DISPLAY"
            export LIBGL_ALWAYS_SOFTWARE=1   # software GL keeps QOpenGL happy
            return 0
        fi
        # If Xvfb died (display taken, missing binary), stop waiting for it.
        if ! kill -0 "$HEADLESS_XVFB_PID" 2>/dev/null; then
            echo "headless_display: Xvfb exited before $HEADLESS_DISPLAY came up" >&2
            return 1
        fi
        sleep 0.1
        waited=$((waited + 1))
    done
    echo "headless_display: $HEADLESS_DISPLAY did not become ready in 15s" >&2
    kill "$HEADLESS_XVFB_PID" 2>/dev/null
    return 1
}

# Fail the RUN, not a later unrelated-looking step. Sourced files cannot exit
# their caller, so the runners' `|| exit 1` is what stops them; this at least
# guarantees the reason is printed at the point it happened.
if ! headless_display_start; then
    echo "headless_display: giving up -- the emulator would have started with" >&2
    echo "  no display and failed later as 'mgba window not found'." >&2
    HEADLESS_DISPLAY_FAILED=1
fi

headless_display_stop() {
    kill "$HEADLESS_XVFB_PID" 2>/dev/null
}
