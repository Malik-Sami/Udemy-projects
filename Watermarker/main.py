"""
Watermark Studio - Desktop Image Watermarking Application
Udemy Portfolio Project - Built with Tkinter and Pillow (PIL)
"""

import math
import os
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageTk

DEFAULT_FONT_NAME = "arial.ttf"
FALLBACK_FONTS = ["arial.ttf", "segoeui.ttf", "tahoma.ttf", "calibri.ttf"]


def get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Attempt to load a clean TrueType font, falling back to default."""
    for font_name in FALLBACK_FONTS:
        try:
            return ImageFont.truetype(font_name, size=size)
        except OSError:
            continue
    try:
        return ImageFont.load_default()
    except Exception:
        return None


class WatermarkerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Watermark Studio")
        self.root.geometry("1100x720")
        self.root.minsize(950, 620)

        # Application state
        self.original_image: Image.Image | None = None
        self.image_path: str | None = None
        self.logo_image: Image.Image | None = None
        self.logo_path: str | None = None
        self.watermark_color: str = "#FFFFFF"
        self.preview_photo: ImageTk.PhotoImage | None = None

        self._setup_theme()
        self._build_ui()

    def _setup_theme(self):
        """Configure clean ttk styling."""
        self.style = ttk.Style(self.root)
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")

        self.style.configure(".", font=("Segoe UI", 9))
        self.style.configure("TFrame", background="#F5F6F8")
        self.style.configure("Sidebar.TFrame", background="#FFFFFF")
        self.style.configure("TLabel", background="#FFFFFF", foreground="#2D3748")
        self.style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), foreground="#1A202C")
        self.style.configure("SubHeader.TLabel", font=("Segoe UI", 9, "bold"), foreground="#4A5568")
        self.style.configure("Accent.TButton", font=("Segoe UI", 9, "bold"))
        self.style.configure("Save.TButton", font=("Segoe UI", 10, "bold"))

    def _build_ui(self):
        """Build the responsive user interface layout."""
        # Main container
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)

        # Left control sidebar
        sidebar_frame = ttk.Frame(main_paned, style="Sidebar.TFrame", padding=15, width=380)
        sidebar_frame.pack_propagate(False)
        main_paned.add(sidebar_frame, weight=0)

        # Right preview canvas
        preview_container = ttk.Frame(main_paned, style="TFrame", padding=15)
        main_paned.add(preview_container, weight=1)

        self._build_sidebar(sidebar_frame)
        self._build_preview_area(preview_container)
        self._build_status_bar()

    def _build_sidebar(self, parent: ttk.Frame):
        """Build all watermark control widgets inside the left sidebar."""
        # Section 1: File Loading
        ttk.Label(parent, text="Image Source", style="Header.TLabel").pack(anchor="w", pady=(0, 6))

        file_btn_frame = ttk.Frame(parent, style="Sidebar.TFrame")
        file_btn_frame.pack(fill=tk.X, pady=(0, 10))

        open_btn = ttk.Button(file_btn_frame, text="📁 Open Base Image", command=self.load_base_image, style="Accent.TButton")
        open_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        self.file_info_label = ttk.Label(parent, text="No image selected", foreground="#718096", wraplength=340)
        self.file_info_label.pack(anchor="w", pady=(0, 12))

        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 12))

        # Section 2: Watermark Type Tabs
        ttk.Label(parent, text="Watermark Settings", style="Header.TLabel").pack(anchor="w", pady=(0, 6))

        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.X, pady=(0, 10))

        # --- Text Watermark Tab ---
        text_tab = ttk.Frame(self.notebook, style="Sidebar.TFrame", padding=10)
        self.notebook.add(text_tab, text="  Text Watermark  ")

        ttk.Label(text_tab, text="Watermark Text:").pack(anchor="w", pady=(2, 2))
        self.text_var = tk.StringVar(value="© MyBrand Photography")
        self.text_var.trace_add("write", lambda *args: self.trigger_preview())
        text_entry = ttk.Entry(text_tab, textvariable=self.text_var)
        text_entry.pack(fill=tk.X, pady=(0, 8))

        # Font Size Slider
        ttk.Label(text_tab, text="Font Size (% of image height):").pack(anchor="w")
        self.font_scale_var = tk.DoubleVar(value=4.5)
        font_slider = ttk.Scale(text_tab, from_=1.0, to=15.0, variable=self.font_scale_var, command=lambda e: self.trigger_preview())
        font_slider.pack(fill=tk.X, pady=(0, 8))

        # Color Picker Row
        color_frame = ttk.Frame(text_tab, style="Sidebar.TFrame")
        color_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(color_frame, text="Color:").pack(side=tk.LEFT)
        self.color_swatch = tk.Label(color_frame, bg=self.watermark_color, width=4, relief="solid", bd=1)
        self.color_swatch.pack(side=tk.LEFT, padx=8)
        color_btn = ttk.Button(color_frame, text="Choose Color", command=self.pick_color)
        color_btn.pack(side=tk.LEFT)

        # Text Opacity Slider
        ttk.Label(text_tab, text="Text Opacity (%):").pack(anchor="w")
        self.text_opacity_var = tk.IntVar(value=75)
        text_opacity_slider = ttk.Scale(text_tab, from_=5, to=100, variable=self.text_opacity_var, command=lambda e: self.trigger_preview())
        text_opacity_slider.pack(fill=tk.X, pady=(0, 4))

        # --- Logo Watermark Tab ---
        logo_tab = ttk.Frame(self.notebook, style="Sidebar.TFrame", padding=10)
        self.notebook.add(logo_tab, text="  Logo / Image  ")

        logo_btn = ttk.Button(logo_tab, text="🖼️ Select Logo File (PNG)", command=self.load_logo_image)
        logo_btn.pack(fill=tk.X, pady=(4, 6))

        self.logo_info_label = ttk.Label(logo_tab, text="No logo chosen", foreground="#718096", wraplength=320)
        self.logo_info_label.pack(anchor="w", pady=(0, 8))

        # Logo Scale Slider
        ttk.Label(logo_tab, text="Logo Scale (% of image width):").pack(anchor="w")
        self.logo_scale_var = tk.DoubleVar(value=20.0)
        logo_scale_slider = ttk.Scale(logo_tab, from_=5.0, to=60.0, variable=self.logo_scale_var, command=lambda e: self.trigger_preview())
        logo_scale_slider.pack(fill=tk.X, pady=(0, 8))

        # Logo Opacity Slider
        ttk.Label(logo_tab, text="Logo Opacity (%):").pack(anchor="w")
        self.logo_opacity_var = tk.IntVar(value=85)
        logo_opacity_slider = ttk.Scale(logo_tab, from_=5, to=100, variable=self.logo_opacity_var, command=lambda e: self.trigger_preview())
        logo_opacity_slider.pack(fill=tk.X, pady=(0, 4))

        self.notebook.bind("<<NotebookTabChanged>>", lambda e: self.trigger_preview())

        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(8, 12))

        # Section 3: Position and Layout
        ttk.Label(parent, text="Position & Layout", style="Header.TLabel").pack(anchor="w", pady=(0, 6))

        pos_grid = ttk.Frame(parent, style="Sidebar.TFrame")
        pos_grid.pack(fill=tk.X, pady=(0, 8))

        self.position_var = tk.StringVar(value="Bottom-Right")
        positions = [
            ("Top-Left", 0, 0), ("Top-Right", 0, 1),
            ("Center", 1, 0),
            ("Bottom-Left", 2, 0), ("Bottom-Right", 2, 1)
        ]
        for name, r, c in positions:
            rb = ttk.Radiobutton(pos_grid, text=name, value=name, variable=self.position_var, command=self.trigger_preview)
            rb.grid(row=r, column=c, sticky="w", padx=4, pady=2)

        # Tile across checkbox
        self.tile_var = tk.BooleanVar(value=False)
        tile_cb = ttk.Checkbutton(parent, text="Tile across entire image (Full Protection)", variable=self.tile_var, command=self.trigger_preview)
        tile_cb.pack(anchor="w", pady=(4, 10))

        # Margin / Padding Slider
        ttk.Label(parent, text="Edge Margin (%):").pack(anchor="w")
        self.margin_var = tk.DoubleVar(value=3.0)
        margin_slider = ttk.Scale(parent, from_=0.5, to=15.0, variable=self.margin_var, command=lambda e: self.trigger_preview())
        margin_slider.pack(fill=tk.X, pady=(0, 14))

        # Section 4: Export Button
        save_btn = ttk.Button(parent, text="💾 Save Watermarked Image", command=self.save_image, style="Save.TButton")
        save_btn.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))

    def _build_preview_area(self, parent: ttk.Frame):
        """Build the right preview area."""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(header_frame, text="Live Preview", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)

        self.canvas_container = ttk.Frame(parent)
        self.canvas_container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_container, bg="#E2E8F0", highlightthickness=1, highlightbackground="#CBD5E0")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self.trigger_preview())

        # Placeholder text on startup
        self.canvas_text_id = self.canvas.create_text(
            350, 250,
            text="Click 'Open Base Image' on the left to start watermarking",
            font=("Segoe UI", 12),
            fill="#718096"
        )

    def _build_status_bar(self):
        """Build the bottom status bar."""
        self.status_var = tk.StringVar(value="Ready. Open an image to begin.")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w", padding=(8, 4))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_base_image(self):
        """Open a file dialog to load an image."""
        filetypes = [
            ("Supported Images", "*.png;*.jpg;*.jpeg;*.webp;*.bmp"),
            ("JPEG Files", "*.jpg;*.jpeg"),
            ("PNG Files", "*.png"),
            ("All Files", "*.*")
        ]
        path = filedialog.askopenfilename(title="Select Base Image", filetypes=filetypes)
        if not path:
            return

        try:
            img = Image.open(path)
            self.original_image = img.convert("RGBA")
            self.image_path = path

            filename = os.path.basename(path)
            w, h = self.original_image.size
            self.file_info_label.config(text=f"{filename}\n({w} x {h} px)")
            self.status_var.set(f"Loaded {filename} [{w}x{h} px]")
            self.trigger_preview()
        except Exception as err:
            messagebox.showerror("Error Opening Image", f"Failed to load image:\n{err}")

    def load_logo_image(self):
        """Open a file dialog to load a watermark logo."""
        filetypes = [
            ("PNG Images with Alpha", "*.png"),
            ("All Images", "*.png;*.jpg;*.jpeg;*.webp;*.bmp"),
            ("All Files", "*.*")
        ]
        path = filedialog.askopenfilename(title="Select Watermark Logo", filetypes=filetypes)
        if not path:
            return

        try:
            img = Image.open(path)
            self.logo_image = img.convert("RGBA")
            self.logo_path = path

            filename = os.path.basename(path)
            w, h = self.logo_image.size
            self.logo_info_label.config(text=f"{filename} ({w}x{h} px)")
            self.status_var.set(f"Logo selected: {filename}")
            self.trigger_preview()
        except Exception as err:
            messagebox.showerror("Error Opening Logo", f"Failed to load logo:\n{err}")

    def pick_color(self):
        """Open color chooser dialog for text watermark."""
        chosen = colorchooser.askcolor(color=self.watermark_color, title="Choose Watermark Color")
        if chosen and chosen[1]:
            self.watermark_color = chosen[1]
            self.color_swatch.config(bg=self.watermark_color)
            self.trigger_preview()

    def get_watermark_settings(self) -> dict:
        """Collect current settings from GUI inputs."""
        active_tab_idx = self.notebook.index(self.notebook.select())
        mode = "text" if active_tab_idx == 0 else "logo"

        return {
            "mode": mode,
            "text": self.text_var.get(),
            "font_scale": self.font_scale_var.get(),
            "color_hex": self.watermark_color,
            "text_opacity": self.text_opacity_var.get(),
            "logo_scale": self.logo_scale_var.get(),
            "logo_opacity": self.logo_opacity_var.get(),
            "position": self.position_var.get(),
            "margin_pct": self.margin_var.get(),
            "tile": self.tile_var.get(),
        }

    def apply_watermark(self, base_img: Image.Image, settings: dict) -> Image.Image:
        """Apply watermark to any image (preview thumbnail or full-res image)."""
        width, height = base_img.size
        watermarked = base_img.copy().convert("RGBA")

        # Create a blank transparent overlay of exact matching dimensions
        overlay = Image.new("RGBA", (width, height), (255, 255, 255, 0))

        if settings["mode"] == "text":
            self._apply_text_watermark(overlay, width, height, settings)
        else:
            self._apply_logo_watermark(overlay, width, height, settings)

        return Image.alpha_composite(watermarked, overlay)

    def _apply_text_watermark(self, overlay: Image.Image, width: int, height: int, settings: dict):
        """Render text watermark onto overlay layer."""
        text = settings["text"].strip()
        if not text:
            return

        font_pixel_size = max(12, int(height * (settings["font_scale"] / 100.0)))
        font = get_font(font_pixel_size)

        # Parse RGB from hex
        hex_color = settings["color_hex"].lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        alpha = int(255 * (settings["text_opacity"] / 100.0))
        fill_color = (r, g, b, alpha)

        draw = ImageDraw.Draw(overlay)

        # Measure text bounding box
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        if settings["tile"]:
            # Tiled pattern across the entire image
            step_x = max(int(text_w * 1.5), 100)
            step_y = max(int(text_h * 2.5), 60)

            # Create a small rotated text tile
            tile_w = text_w + 60
            tile_h = text_h + 40
            text_tile = Image.new("RGBA", (tile_w, tile_h), (0, 0, 0, 0))
            tile_draw = ImageDraw.Draw(text_tile)
            tile_draw.text((30, 20), text, font=font, fill=fill_color)
            rotated_tile = text_tile.rotate(30, expand=True, resample=Image.Resampling.BICUBIC)
            rw, rh = rotated_tile.size

            for x in range(-rw, width + rw, max(step_x, rw)):
                for y in range(-rh, height + rh, max(step_y, rh)):
                    overlay.alpha_composite(rotated_tile, (x, y))
        else:
            margin = int(min(width, height) * (settings["margin_pct"] / 100.0))
            x, y = self._calc_position(width, height, text_w, text_h, margin, settings["position"])
            draw.text((x, y), text, font=font, fill=fill_color)

    def _apply_logo_watermark(self, overlay: Image.Image, width: int, height: int, settings: dict):
        """Render logo image watermark onto overlay layer."""
        if self.logo_image is None:
            return

        target_logo_width = max(20, int(width * (settings["logo_scale"] / 100.0)))
        aspect = self.logo_image.height / self.logo_image.width
        target_logo_height = max(20, int(target_logo_width * aspect))

        # Resize logo with high quality lanczos
        resized_logo = self.logo_image.resize((target_logo_width, target_logo_height), Image.Resampling.LANCZOS)

        # Apply opacity to logo alpha channel
        opacity_factor = settings["logo_opacity"] / 100.0
        r, g, b, a = resized_logo.split()
        a = a.point(lambda p: int(p * opacity_factor))
        resized_logo.putalpha(a)

        if settings["tile"]:
            step_x = max(int(target_logo_width * 1.6), 60)
            step_y = max(int(target_logo_height * 1.6), 60)
            for x in range(0, width, step_x):
                for y in range(0, height, step_y):
                    overlay.alpha_composite(resized_logo, (x, y))
        else:
            margin = int(min(width, height) * (settings["margin_pct"] / 100.0))
            x, y = self._calc_position(width, height, target_logo_width, target_logo_height, margin, settings["position"])
            overlay.alpha_composite(resized_logo, (x, y))

    def _calc_position(self, img_w: int, img_h: int, item_w: int, item_h: int, margin: int, position: str) -> tuple[int, int]:
        """Calculate (x, y) coordinates for single-item placement."""
        if position == "Top-Left":
            return margin, margin
        elif position == "Top-Right":
            return max(0, img_w - item_w - margin), margin
        elif position == "Center":
            return max(0, (img_w - item_w) // 2), max(0, (img_h - item_h) // 2)
        elif position == "Bottom-Left":
            return margin, max(0, img_h - item_h - margin)
        else:  # Bottom-Right
            return max(0, img_w - item_w - margin), max(0, img_h - item_h - margin)

    def trigger_preview(self):
        """Update the interactive preview display."""
        if self.original_image is None:
            return

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        if canvas_w < 50 or canvas_h < 50:
            return

        settings = self.get_watermark_settings()

        # Generate responsive thumbnail preserving aspect ratio
        img_w, img_h = self.original_image.size
        scale = min(canvas_w / img_w, canvas_h / img_h, 1.0)
        target_w = max(1, int(img_w * scale))
        target_h = max(1, int(img_h * scale))

        thumb = self.original_image.resize((target_w, target_h), Image.Resampling.BILINEAR)

        # Apply watermark to thumbnail
        preview_img = self.apply_watermark(thumb, settings)

        # Convert to Tk PhotoImage
        self.preview_photo = ImageTk.PhotoImage(preview_img)

        # Render onto canvas center
        self.canvas.delete("all")
        cx = canvas_w // 2
        cy = canvas_h // 2
        self.canvas.create_image(cx, cy, image=self.preview_photo, anchor=tk.CENTER)

    def save_image(self):
        """Save the watermarked image at original full resolution."""
        if self.original_image is None:
            messagebox.showwarning("No Image", "Please open an image first before saving.")
            return

        settings = self.get_watermark_settings()
        if settings["mode"] == "logo" and self.logo_image is None:
            messagebox.showwarning("No Logo", "Please select a logo image or switch to Text Watermark mode.")
            return

        # Prepare default save name
        orig_dir, orig_name = os.path.split(self.image_path) if self.image_path else ("", "image")
        root_name, ext = os.path.splitext(orig_name)
        default_filename = f"{root_name}_watermarked.png"

        save_path = filedialog.asksaveasfilename(
            title="Save Watermarked Image",
            initialdir=orig_dir,
            initialfile=default_filename,
            filetypes=[
                ("PNG Image (Lossless)", "*.png"),
                ("JPEG Image", "*.jpg;*.jpeg"),
                ("All Files", "*.*")
            ],
            defaultextension=".png"
        )
        if not save_path:
            return

        try:
            self.status_var.set("Applying watermark to full-resolution image...")
            self.root.update_idletasks()

            full_res_watermarked = self.apply_watermark(self.original_image, settings)

            # Handle format conversions (e.g. JPEG doesn't support alpha channel)
            ext_lower = os.path.splitext(save_path)[1].lower()
            if ext_lower in [".jpg", ".jpeg"]:
                # Paste RGBA onto white background for clean JPEG export
                rgb_canvas = Image.new("RGB", full_res_watermarked.size, (255, 255, 255))
                rgb_canvas.paste(full_res_watermarked, mask=full_res_watermarked.split()[3])
                rgb_canvas.save(save_path, "JPEG", quality=95)
            else:
                full_res_watermarked.save(save_path, "PNG")

            filename = os.path.basename(save_path)
            self.status_var.set(f"Successfully saved: {filename}")
            messagebox.showinfo("Success", f"Watermarked image successfully saved!\n\nLocation:\n{save_path}")
        except Exception as err:
            self.status_var.set("Error saving image.")
            messagebox.showerror("Save Error", f"Failed to save watermarked image:\n{err}")


def main():
    root = tk.Tk()
    app = WatermarkerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
