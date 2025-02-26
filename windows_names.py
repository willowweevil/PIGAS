from Xlib import display

def list_window_names():
    # Connect to the X server
    display_instance = display.Display()
    screen = display_instance.screen()

    # Get the root window
    root = screen.root

    # Query the tree of windows
    window_ids = root.query_tree().children

    # Iterate over each window and print its name
    for window_id in window_ids:
        try:
            window_name = window_id.get_wm_name()
            if window_name:
                print(f"Window ID: {window_id.id}, Name: {window_name}")
        except Exception as e:
            # Handle any exceptions (e.g., if a window doesn't have a name)
            print(f"Could not get name for window ID: {window_id.id}, Error: {e}")

if __name__ == "__main__":
    list_window_names()