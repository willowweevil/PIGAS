from Xlib import X, display
from Xlib.protocol import event
import time

# Mapping keys to 'Xlib' keysyms
key_map = {
    'H': 0x48,  # Xlib keysyms for letters
    'E': 0x45,
    'L': 0x4C,
    'O': 0x4F,
    ' ': 0x20,
    # Add other necessary mappings...
}

def send_keys(display_instance, window, keys):
    # Grab the keyboard for this window
    window.grab_keyboard(True, X.GrabModeSync, X.GrabModeAsync, X.CurrentTime)

    for key in keys:
        if key in key_map:
            keycode = key_map[key]

            # Create and send key press event
            key_press_event = event.KeyPress(
                time=X.CurrentTime,
                root=display_instance.screen().root,
                window=window,
                same_screen=1,
                child=X.NONE,
                root_x=0,
                root_y=0,
                event_x=0,
                event_y=0,
                state=0,
                detail=keycode
            )
            window.send_event(key_press_event)

            # Create and send key release event
            key_release_event = event.KeyRelease(
                time=X.CurrentTime,
                root=display_instance.screen().root,
                window=window,
                same_screen=1,
                child=X.NONE,
                root_x=0,
                root_y=0,
                event_x=0,
                event_y=0,
                state=0,
                detail=keycode
            )
            window.send_event(key_release_event)

            time.sleep(0.1)  # Short delay between key presses

def main():
    display_instance = display.Display()
    screen = display_instance.screen()

    # Replace with the exact window title you want to target
    window_id = None
    for window in screen.root.query_tree().children:
        if window.get_wm_name() == "ivan@thinkpad-ubuntu: ~":
            window_id = window
            break

    if window_id:
        window_id.map()  # Make sure it is mapped
        send_keys(display_instance, window_id, "wwww")
    else:
        print("Window not found.")

if __name__ == "__main__":
    main()