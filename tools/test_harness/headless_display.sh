# Sourced by every test runner: moves the emulator + all synthetic input
# onto a private Xvfb display so tests NEVER touch the user's screen,
# focus, or keyboard. The display number is derived from the PID to allow
# parallel runs.
#
# Usage (in a runner, before launching mgba-qt):
#   . "$HERE/headless_display.sh"
# Cleanup: headless_display_stop (also wired into your trap).

HEADLESS_DISPLAY=":$((90 + $$ % 8))"
Xvfb "$HEADLESS_DISPLAY" -screen 0 480x320x24 -nolisten tcp >/dev/null 2>&1 &
HEADLESS_XVFB_PID=$!
sleep 1
export DISPLAY="$HEADLESS_DISPLAY"
# software GL keeps QOpenGL happy without a real GPU surface
export LIBGL_ALWAYS_SOFTWARE=1

headless_display_stop() {
    kill "$HEADLESS_XVFB_PID" 2>/dev/null
}
