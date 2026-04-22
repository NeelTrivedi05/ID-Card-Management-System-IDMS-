"""
photo_crop.py — Face-Crop & Auto-Resize Photo Tool (Feature 05)

Interactive crop dialog where the admin can pan and adjust a crop
box over the uploaded photo.  The cropped result is saved as a
properly-sized passport-style image for ID cards.
"""

import tkinter as tk
from tkinter import messagebox
import os
import theme as _theme

try:
    from PIL import Image, ImageTk, ImageDraw
except ImportError:
    Image = ImageTk = ImageDraw = None


# Target output size for ID card photos (width x height)
CROP_OUTPUT_W = 200
CROP_OUTPUT_H = 250
CROP_RATIO    = CROP_OUTPUT_W / CROP_OUTPUT_H   # 0.8

# Canvas display size
CANVAS_W = 460
CANVAS_H = 400


class PhotoCropDialog:
    """
    Toplevel dialog that lets the user drag-to-position a fixed-ratio
    crop box over a photo. On confirm, the cropped area is resized to
    CROP_OUTPUT_W×CROP_OUTPUT_H and saved to photos/.
    """

    def __init__(self, parent, image_path, output_dir="photos"):
        if Image is None:
            messagebox.showerror(
                "Missing Library",
                "Pillow is required for the photo crop tool.\n"
                "Run: pip install Pillow",
            )
            self.result_path = None
            return

        self.parent = parent
        self.image_path = image_path
        self.output_dir = output_dir
        self.result_path = None          # set on successful crop
        os.makedirs(output_dir, exist_ok=True)

        # Load original image
        self.orig_img = Image.open(image_path).convert("RGB")
        ow, oh = self.orig_img.size

        # Scale image to fit canvas
        scale = min(CANVAS_W / ow, CANVAS_H / oh, 1.0)
        self.display_w = int(ow * scale)
        self.display_h = int(oh * scale)
        self.scale = scale

        self.display_img = self.orig_img.resize(
            (self.display_w, self.display_h), Image.LANCZOS
        )

        # Crop box dimensions (in display coords)
        crop_h = int(self.display_h * 0.75)
        crop_w = int(crop_h * CROP_RATIO)
        if crop_w > self.display_w * 0.9:
            crop_w = int(self.display_w * 0.9)
            crop_h = int(crop_w / CROP_RATIO)

        self.crop_w = crop_w
        self.crop_h = crop_h

        # Initial position (centre)
        self.crop_x = (self.display_w - crop_w) // 2
        self.crop_y = (self.display_h - crop_h) // 2

        # Drag state
        self._drag_start = None

        self._build_ui()

    def _build_ui(self):
        t = _theme.get()
        F = _theme.FONTS

        self.win = tk.Toplevel(self.parent)
        self.win.title("Crop Photo — Drag to Position")
        self.win.geometry(f"{CANVAS_W + 40}x{CANVAS_H + 100}")
        self.win.configure(bg=t["DARK_BG"])
        self.win.resizable(False, False)
        self.win.grab_set()

        # Centre
        self.win.update_idletasks()
        x = (self.win.winfo_screenwidth()  // 2) - (CANVAS_W + 40) // 2
        y = (self.win.winfo_screenheight() // 2) - (CANVAS_H + 100) // 2
        self.win.geometry(f"+{x}+{y}")

        tk.Label(self.win, text="📷 Drag the box to frame the face",
                 font=F["body_bold"], bg=t["DARK_BG"], fg=t["TEXT_MAIN"]
                 ).pack(pady=(10, 4))

        tk.Label(self.win, text="The highlighted area will be cropped & resized for the ID card.",
                 font=F["micro"], bg=t["DARK_BG"], fg=t["TEXT_HINT"]
                 ).pack(pady=(0, 6))

        # Canvas
        self.canvas = tk.Canvas(self.win, width=CANVAS_W, height=CANVAS_H,
                                bg=t["PANEL_BG"], highlightthickness=0)
        self.canvas.pack(padx=20)

        # Draw image offset (centred on canvas)
        self.img_offset_x = (CANVAS_W - self.display_w) // 2
        self.img_offset_y = (CANVAS_H - self.display_h) // 2

        self._draw()

        # Bind events
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

        # Buttons
        btn_frame = tk.Frame(self.win, bg=t["DARK_BG"], pady=8)
        btn_frame.pack()

        _theme.make_btn(btn_frame, "Confirm Crop", "BTN_SUCCESS",
                        command=self._confirm, icon="✅")
        _theme.make_btn(btn_frame, "Cancel", "BTN_DANGER",
                        command=self.win.destroy)

    def _draw(self):
        """Redraw the canvas with the image and crop overlay."""
        self.canvas.delete("all")

        # Create semi-transparent overlay version
        overlay = self.display_img.copy()
        dark = Image.new("RGBA", overlay.size, (0, 0, 0, 140))
        overlay = overlay.convert("RGBA")
        overlay = Image.alpha_composite(overlay, dark)

        # Paste the bright (uncropped) region back
        bright = self.display_img.crop((
            self.crop_x, self.crop_y,
            self.crop_x + self.crop_w, self.crop_y + self.crop_h,
        ))
        overlay.paste(bright, (self.crop_x, self.crop_y))

        # Convert and display
        self._tk_img = ImageTk.PhotoImage(overlay.convert("RGB"))
        self.canvas.create_image(
            self.img_offset_x, self.img_offset_y,
            image=self._tk_img, anchor="nw",
        )

        # Draw crop rectangle border
        rx1 = self.img_offset_x + self.crop_x
        ry1 = self.img_offset_y + self.crop_y
        rx2 = rx1 + self.crop_w
        ry2 = ry1 + self.crop_h
        accent = _theme.get().get("BADGE_VALID", "#22c55e")
        self.canvas.create_rectangle(rx1, ry1, rx2, ry2,
                                      outline=accent, width=2, dash=(6, 3))

        # Corner markers
        m = 8
        for (cx, cy) in [(rx1, ry1), (rx2, ry1), (rx1, ry2), (rx2, ry2)]:
            self.canvas.create_rectangle(cx - m, cy - m, cx + m, cy + m,
                                          fill=accent, outline="")

    def _on_press(self, event):
        self._drag_start = (event.x, event.y)

    def _on_drag(self, event):
        if self._drag_start is None:
            return
        dx = event.x - self._drag_start[0]
        dy = event.y - self._drag_start[1]

        new_x = self.crop_x + dx
        new_y = self.crop_y + dy

        # Clamp within image bounds
        new_x = max(0, min(new_x, self.display_w - self.crop_w))
        new_y = max(0, min(new_y, self.display_h - self.crop_h))

        self.crop_x = new_x
        self.crop_y = new_y
        self._drag_start = (event.x, event.y)
        self._draw()

    def _on_release(self, event):
        self._drag_start = None

    def _confirm(self):
        """Crop the original image and save to output_dir."""
        # Map display coords back to original image coords
        inv_scale = 1.0 / self.scale
        left   = int(self.crop_x * inv_scale)
        top    = int(self.crop_y * inv_scale)
        right  = int((self.crop_x + self.crop_w) * inv_scale)
        bottom = int((self.crop_y + self.crop_h) * inv_scale)

        cropped = self.orig_img.crop((left, top, right, bottom))
        cropped = cropped.resize((CROP_OUTPUT_W, CROP_OUTPUT_H), Image.LANCZOS)

        # Save with a unique filename
        base = os.path.splitext(os.path.basename(self.image_path))[0]
        out_name = f"{base}_cropped.jpg"
        out_path = os.path.join(self.output_dir, out_name)

        # Avoid overwriting
        counter = 1
        while os.path.exists(out_path):
            out_name = f"{base}_cropped_{counter}.jpg"
            out_path = os.path.join(self.output_dir, out_name)
            counter += 1

        cropped.save(out_path, quality=95)
        self.result_path = out_path
        self.win.destroy()
