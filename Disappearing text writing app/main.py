"""A writing exercise that clears the page after five seconds of inactivity."""

import time
import tkinter as tk


IDLE_LIMIT_SECONDS = 5.0


class DangerousWritingApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("The Five-Second Page")
        self.root.geometry("940x760")
        self.root.minsize(680, 580)
        self.root.configure(bg="#111816")

        self.is_active = False
        self.last_activity: float | None = None
        self.tick_job: str | None = None

        self._build_ui()
        self._update_timer()
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self.root.after(100, self.editor.focus_set)

    def _build_ui(self) -> None:
        self.container = tk.Frame(self.root, bg="#111816", padx=48, pady=34)
        self.container.pack(fill=tk.BOTH, expand=True)

        top_line = tk.Frame(self.container, bg="#111816")
        top_line.pack(fill=tk.X)
        tk.Label(
            top_line,
            text="A WRITING EXPERIMENT",
            bg="#111816",
            fg="#9ba99e",
            font=("Segoe UI", 9, "bold"),
        ).pack(side=tk.LEFT)
        tk.Label(
            top_line,
            text="NO PAUSE  ·  NO AUTOSAVE",
            bg="#111816",
            fg="#77857b",
            font=("Segoe UI", 9),
        ).pack(side=tk.RIGHT)

        tk.Label(
            self.container,
            text="The Five-Second Page",
            bg="#111816",
            fg="#f0eee3",
            font=("Georgia", 30, "bold"),
        ).pack(anchor="w", pady=(16, 5))
        tk.Label(
            self.container,
            text="Keep the words moving. Stop for five seconds and the page disappears.",
            bg="#111816",
            fg="#aab5aa",
            font=("Segoe UI", 11),
        ).pack(anchor="w")

        timer_card = tk.Frame(
            self.container, bg="#1a2420", padx=20, pady=14, highlightthickness=1,
            highlightbackground="#29362f",
        )
        timer_card.pack(fill=tk.X, pady=(24, 16))

        timer_copy = tk.Frame(timer_card, bg="#1a2420")
        timer_copy.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(
            timer_copy,
            text="TIME UNTIL THE PAGE IS LOST",
            bg="#1a2420",
            fg="#aab5aa",
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w")
        self.status_label = tk.Label(
            timer_copy,
            text="Start writing whenever you're ready.",
            bg="#1a2420",
            fg="#e2e7dc",
            font=("Segoe UI", 10),
        )
        self.status_label.pack(anchor="w", pady=(4, 0))

        timer_value = tk.Frame(timer_card, bg="#1a2420")
        timer_value.pack(side=tk.RIGHT, padx=(16, 0))
        self.timer_label = tk.Label(
            timer_value,
            text="5.0",
            bg="#1a2420",
            fg="#a8d5a2",
            font=("Consolas", 24, "bold"),
            width=5,
            anchor="e",
        )
        self.timer_label.pack(side=tk.LEFT)
        tk.Label(
            timer_value,
            text=" sec",
            bg="#1a2420",
            fg="#aab5aa",
            font=("Segoe UI", 10),
        ).pack(side=tk.LEFT, anchor="s", pady=(0, 5))

        self.timer_bar = tk.Canvas(
            self.container, height=3, bg="#29362f", highlightthickness=0
        )
        self.timer_bar.pack(fill=tk.X, pady=(0, 16))

        editor_frame = tk.Frame(
            self.container, bg="#19211e", highlightthickness=1, highlightbackground="#29362f"
        )
        editor_frame.pack(fill=tk.BOTH, expand=True)
        self.editor = tk.Text(
            editor_frame,
            wrap=tk.WORD,
            undo=True,
            autoseparators=True,
            maxundo=-1,
            bg="#19211e",
            fg="#e9e9dc",
            insertbackground="#a8d5a2",
            selectbackground="#44614f",
            selectforeground="#ffffff",
            font=("Georgia", 15),
            padx=24,
            pady=22,
            spacing1=4,
            spacing3=4,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
        )
        self.editor.pack(fill=tk.BOTH, expand=True)
        self.editor.bind("<<Modified>>", self._on_text_changed)

        footer = tk.Frame(self.container, bg="#111816")
        footer.pack(fill=tk.X, pady=(12, 0))
        self.word_count_label = tk.Label(
            footer,
            text="0 words",
            bg="#111816",
            fg="#77857b",
            font=("Segoe UI", 9),
        )
        self.word_count_label.pack(side=tk.LEFT)
        tk.Label(
            footer,
            text="Your writing is never saved.",
            bg="#111816",
            fg="#77857b",
            font=("Segoe UI", 9),
        ).pack(side=tk.LEFT, padx=(18, 0))
        tk.Button(
            footer,
            text="Clear page",
            command=self._clear_page,
            bg="#26332c",
            fg="#dce4d9",
            activebackground="#34473a",
            activeforeground="#ffffff",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=14,
            pady=7,
            cursor="hand2",
        ).pack(side=tk.RIGHT)

    def _on_text_changed(self, _event: tk.Event) -> None:
        if not self.editor.edit_modified():
            return

        self.editor.edit_modified(False)
        content = self.editor.get("1.0", "end-1c")
        self.word_count_label.config(text=f"{len(content.split())} words")

        if content:
            self.is_active = True
            self.last_activity = time.monotonic()
            self.status_label.config(text="Keep going. The clock resets with every edit.")
        else:
            self.is_active = False
            self.last_activity = None
            self.status_label.config(text="Start writing whenever you're ready.")

    def _update_timer(self) -> None:
        remaining = IDLE_LIMIT_SECONDS
        if self.is_active and self.last_activity is not None:
            elapsed = time.monotonic() - self.last_activity
            remaining = max(0.0, IDLE_LIMIT_SECONDS - elapsed)
            if remaining <= 0:
                self._clear_page(lost=True)
                remaining = IDLE_LIMIT_SECONDS

        self.timer_label.config(text=f"{remaining:.1f}")
        if remaining > 2.5:
            color = "#a8d5a2"
        elif remaining > 1:
            color = "#e5bd76"
        else:
            color = "#e78476"
        self.timer_label.config(fg=color)

        self.timer_bar.delete("all")
        width = self.timer_bar.winfo_width()
        fraction = remaining / IDLE_LIMIT_SECONDS
        if width > 1:
            self.timer_bar.create_rectangle(
                0, 0, width * fraction, 3, fill=color, outline=""
            )
        self.tick_job = self.root.after(50, self._update_timer)

    def _clear_page(self, lost: bool = False) -> None:
        self.editor.delete("1.0", "end")
        self.editor.edit_modified(False)
        self.is_active = False
        self.last_activity = None
        self.word_count_label.config(text="0 words")
        if lost:
            self.status_label.config(text="The page disappeared. Take a breath, then begin again.")
        else:
            self.status_label.config(text="Fresh page. Start writing whenever you're ready.")
        self.editor.focus_set()

    def _close(self) -> None:
        if self.tick_job is not None:
            self.root.after_cancel(self.tick_job)
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    DangerousWritingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()