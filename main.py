import tkinter as tk
from PIL import Image, ImageTk
import itertools
import random
import sys
import os

# -------- Helper to find files both in script and exe --------


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    if getattr(sys, 'frozen', False):  # PyInstaller bundles as exe
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# --------------config-----------------
size = 64
speed = 5
fps = 20
frame_delay = int(1000 / fps)
idle_time = 2000
walk_time = 3000
# -------------------------------------
root = tk.Tk()
root.overrideredirect(True)
root.attributes('-topmost', True)
root.attributes('-transparentcolor', 'pink')

root.focus_force()       # Force the window to receive focus
root.grab_set()

root.bind("<Escape>", lambda e: root.destroy())


screem_W = root.winfo_screenwidth()
screem_H = root.winfo_screenheight()
root.geometry(f"{screem_W}x{screem_H}+0+0")

canvas = tk.Canvas(root, bg='pink', highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)

# -------- Load frames safely --------


def load_frames(prefix):
    frames = []
    flipped_frames = []

    for i in range(4):
        img_path = resource_path(f"{prefix}_{i}.png")
        img = Image.open(img_path)
        frames.append(ImageTk.PhotoImage(img))
        flipped_frames.append(
            ImageTk.PhotoImage(img.transpose(Image.FLIP_LEFT_RIGHT))
        )

    return frames, flipped_frames


idle_frames, idle_frames_flipped = load_frames("idle")
walk_frames, walk_frames_flipped = load_frames("walk")

idle_anim = itertools.cycle(idle_frames)
idle_anim_flipped = itertools.cycle(idle_frames_flipped)
walk_anim = itertools.cycle(walk_frames)
walk_anim_flipped = itertools.cycle(walk_frames_flipped)

state = 'idle'
direction = 1
x = screem_W // 2
y = screem_H - size - 5
idle_flip_ready = True

char = canvas.create_image(x, y, anchor="nw", image=idle_frames[0])

canvas.tag_bind(char, "<Button-1>", lambda e: root.destroy())

# -------- State management --------


def set_state(new_state):
    global state, idle_flip_ready
    state = new_state

    if new_state == 'idle':
        idle_flip_ready = True

    delay = walk_time if new_state == 'walk' else idle_time
    root.after(delay, toggle_state)


def toggle_state():
    global direction, idle_flip_ready
    if state == "idle":
        # Flip once at the end of idle with a chance
        if idle_flip_ready and random.random() < 0.05:
            direction *= -1
            idle_flip_ready = False
        set_state("walk")
    else:
        set_state("idle")

# -------- Update animation --------


def update():
    global x, direction

    if state == 'walk':
        x += speed * direction
        if x <= 0 or x >= screem_W - size:
            direction *= -1

        if direction == 1:
            frame = next(walk_anim_flipped)
        else:
            frame = next(walk_anim)

    else:
        if random.random() < 0.05:
            direction *= -1

        if direction == 1:
            frame = next(idle_anim)
        else:
            frame = next(idle_anim_flipped)

    canvas.itemconfig(char, image=frame)
    canvas.coords(char, x, y)
    root.after(frame_delay, update)


set_state("idle")
update()
root.mainloop()
