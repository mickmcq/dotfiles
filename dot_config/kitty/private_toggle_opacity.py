import os

STATE_FILE = os.path.expanduser("~/.config/kitty/.opacity_state")

def main(args):
    pass

def handle_result(args, answer, target_window_id, boss):
    # Check current state from file
    is_opaque = False
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            is_opaque = f.read().strip() == "opaque"
    
    # Toggle
    if is_opaque:
        boss.set_background_opacity("default")
        with open(STATE_FILE, "w") as f:
            f.write("transparent")
    else:
        boss.set_background_opacity("1")
        with open(STATE_FILE, "w") as f:
            f.write("opaque")

handle_result.no_ui = True
