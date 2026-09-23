"""
Typing Speed Test Desktop Application
Udemy Portfolio Project - Built with Tkinter
"""

import json
import os
import random
import time
import tkinter as tk
from tkinter import ttk

# Curated bank of common high-frequency words for typing speed tests
WORD_BANK = [
    "the", "be", "of", "and", "a", "to", "in", "he", "have", "it", "that", "for", "they", "I",
    "with", "as", "not", "on", "she", "at", "by", "this", "we", "you", "do", "but", "his",
    "from", "say", "her", "or", "an", "will", "my", "one", "all", "would", "there", "their",
    "what", "so", "up", "out", "if", "about", "who", "get", "which", "go", "me", "when",
    "make", "can", "like", "time", "no", "just", "him", "know", "take", "people", "into",
    "year", "your", "good", "some", "could", "them", "see", "other", "than", "then", "now",
    "look", "only", "come", "its", "over", "think", "also", "back", "after", "use", "two",
    "how", "our", "work", "first", "well", "way", "even", "new", "want", "because", "any",
    "these", "give", "day", "most", "us", "water", "long", "find", "very", "world", "great",
    "where", "much", "should", "before", "right", "too", "mean", "old", "same", "tell", "boy",
    "follow", "came", "show", "around", "farm", "three", "small", "set", "put", "end", "does",
    "another", "large", "must", "big", "such", "turn", "here", "why", "ask", "went", "men",
    "read", "need", "land", "different", "home", "move", "try", "kind", "hand", "picture",
    "again", "change", "off", "play", "spell", "air", "away", "animal", "house", "point",
    "page", "letter", "mother", "answer", "found", "study", "still", "learn", "America",
    "high", "every", "near", "add", "food", "between", "own", "below", "country", "plant",
    "last", "school", "father", "keep", "tree", "never", "start", "city", "earth", "eyes",
    "light", "thought", "head", "under", "story", "saw", "left", "few", "while", "along",
    "might", "close", "something", "seem", "next", "hard", "open", "example", "begin", "life",
    "always", "those", "both", "paper", "together", "got", "group", "often", "run", "important",
    "until", "children", "side", "feet", "car", "mile", "night", "walk", "white", "sea",
    "began", "grow", "took", "river", "four", "carry", "state", "once", "book", "hear",
    "stop", "without", "second", "late", "miss", "idea", "enough", "eat", "face", "watch",
    "far", "real", "almost", "let", "above", "girl", "sometimes", "mountain", "cut", "young",
    "talk", "soon", "list", "song", "being", "leave", "family"
]

HIGH_SCORES_FILE = os.path.join(os.path.dirname(__file__), "high_scores.json")


class TypingSpeedTestApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Typing Speed Master - Desktop WPM Test")
        self.root.geometry("920x660")
        self.root.minsize(820, 580)
        self.root.configure(bg="#1E1E2E")

        # Game state variables
        self.test_duration = 60  # seconds
        self.time_left = self.test_duration
        self.is_running = False
        self.is_finished = False
        self.start_time: float | None = None
        self.timer_job = None

        self.words: list[str] = []
        self.current_word_idx = 0
        self.correct_words = 0
        self.wrong_words = 0
        self.correct_chars = 0
        self.total_keystrokes = 0

        self.high_scores = self._load_high_scores()

        self._setup_styles()
        self._build_ui()
        self.reset_test()

        # Ensure input box is focused on startup
        self.root.after(100, self.focus_entry)
        self.root.after(300, self.focus_entry)

    def _setup_styles(self):
        """Configure dark ttk styling."""
        self.style = ttk.Style(self.root)
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")

        self.style.configure(".", background="#1E1E2E", foreground="#CDD6F4", font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#89B4FA", background="#1E1E2E")
        self.style.configure("StatValue.TLabel", font=("Segoe UI", 20, "bold"), foreground="#A6E3A1", background="#252538")
        self.style.configure("StatTitle.TLabel", font=("Segoe UI", 9), foreground="#A6ADC8", background="#252538")

    def _build_ui(self):
        """Construct the complete UI layout."""
        # Main padding wrapper
        self.container = tk.Frame(self.root, bg="#1E1E2E", padx=30, pady=20)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Top Bar: Title & Controls
        top_bar = tk.Frame(self.container, bg="#1E1E2E")
        top_bar.pack(fill=tk.X, pady=(0, 15))

        title_lbl = ttk.Label(top_bar, text="⚡ Typing Speed Test", style="Header.TLabel")
        title_lbl.pack(side=tk.LEFT)

        controls_frame = tk.Frame(top_bar, bg="#1E1E2E")
        controls_frame.pack(side=tk.RIGHT)

        tk.Label(controls_frame, text="Duration:", bg="#1E1E2E", fg="#A6ADC8", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=6)
        self.duration_var = tk.IntVar(value=60)
        for dur in [15, 30, 60]:
            rb = tk.Radiobutton(
                controls_frame, text=f"{dur}s", value=dur, variable=self.duration_var,
                bg="#1E1E2E", fg="#CDD6F4", selectcolor="#313244", activebackground="#1E1E2E",
                activeforeground="#89B4FA", font=("Segoe UI", 9, "bold"),
                command=self.change_duration
            )
            rb.pack(side=tk.LEFT, padx=3)

        # Prominent Start / Reset Button in header
        self.start_btn = tk.Button(
            controls_frame, text="▶️ START TEST", command=self.toggle_start_reset,
            bg="#A6E3A1", fg="#1E1E2E", activebackground="#94D38F", activeforeground="#1E1E2E",
            font=("Segoe UI", 10, "bold"), relief="flat", padx=16, pady=4, cursor="hand2"
        )
        self.start_btn.pack(side=tk.LEFT, padx=(15, 0))

        # Stats Cards Row
        stats_frame = tk.Frame(self.container, bg="#1E1E2E")
        stats_frame.pack(fill=tk.X, pady=(0, 18))
        stats_frame.columnconfigure((0, 1, 2, 3), weight=1, uniform="stat_col")

        self.time_card, self.time_val_lbl = self._create_stat_card(stats_frame, 0, "TIME REMAINING", "60s", "#FAB387")
        self.wpm_card, self.wpm_val_lbl = self._create_stat_card(stats_frame, 1, "NET WPM", "0", "#A6E3A1")
        self.acc_card, self.acc_val_lbl = self._create_stat_card(stats_frame, 2, "ACCURACY", "100%", "#89B4FA")
        self.best_card, self.best_val_lbl = self._create_stat_card(stats_frame, 3, "PERSONAL BEST", f"{self._get_best_wpm()} WPM", "#F9E2AF")

        # Word Display Box (Scrolling multi-line text box)
        word_box_frame = tk.Frame(self.container, bg="#252538", bd=1, relief="solid")
        word_box_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        self.text_display = tk.Text(
            word_box_frame, bg="#252538", fg="#6C7086", font=("Consolas", 18),
            wrap=tk.WORD, padx=22, pady=22, spacing2=14, relief="flat",
            selectbackground="#45475A", cursor="xterm", takefocus=0
        )
        self.text_display.pack(fill=tk.BOTH, expand=True)

        # Clicking on text display shifts focus to entry box without taking focus
        def on_text_click(event):
            self.focus_entry()
            return "break"
        self.text_display.bind("<Button-1>", on_text_click)

        # Tags for word states
        self.text_display.tag_configure("upcoming", foreground="#6C7086")
        self.text_display.tag_configure("current", foreground="#FFFFFF", background="#3B4252")
        self.text_display.tag_configure("current_partial", foreground="#A6E3A1", background="#3B4252")
        self.text_display.tag_configure("current_error", foreground="#F38BA8", background="#4C2834")
        self.text_display.tag_configure("correct", foreground="#A6E3A1")
        self.text_display.tag_configure("wrong", foreground="#F38BA8", underline=True)

        # Input Area with clear instructions
        input_container = tk.Frame(self.container, bg="#1E1E2E")
        input_container.pack(fill=tk.X, pady=(0, 8))

        input_header = tk.Frame(input_container, bg="#1E1E2E")
        input_header.pack(fill=tk.X, pady=(0, 6))

        self.instruction_lbl = tk.Label(
            input_header, text="⌨️ Type the word and press SPACE to advance to the next word:",
            bg="#1E1E2E", fg="#CDD6F4", font=("Segoe UI", 10, "bold")
        )
        self.instruction_lbl.pack(side=tk.LEFT)

        self.status_badge = tk.Label(
            input_header, text="🟢 Click 'START TEST' or start typing",
            bg="#1E1E2E", fg="#A6E3A1", font=("Segoe UI", 9, "bold")
        )
        self.status_badge.pack(side=tk.RIGHT)

        # Prominent input field
        self.entry_frame = tk.Frame(input_container, bg="#89B4FA", padx=2, pady=2)
        self.entry_frame.pack(fill=tk.X)

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(
            self.entry_frame, textvariable=self.entry_var, font=("Consolas", 20, "bold"),
            bg="#313244", fg="#FFFFFF", insertbackground="#89B4FA", relief="flat",
            justify="center"
        )
        self.entry.pack(fill=tk.X, ipady=8)

        # Listen for keystrokes to give live feedback
        self.entry_var.trace_add("write", self.on_text_change)

        # Handle space and enter explicitly
        self.entry.bind("<space>", self.on_space_pressed)
        self.entry.bind("<Return>", self.on_space_pressed)

        # If user presses keys while focus was on window/container, redirect to entry
        def on_global_key(event):
            if self.is_finished:
                return
            if event.widget != self.entry:
                self.focus_entry()
                if event.char and event.char.isprintable() and event.keysym not in ["Return", "Tab", "Escape"]:
                    self.entry.insert(tk.END, event.char)
                    return "break"
        self.root.bind("<Key>", on_global_key)

    def _create_stat_card(self, parent: tk.Frame, col: int, title: str, default_val: str, val_color: str):
        """Helper to create a sleek dashboard metric card."""
        card = tk.Frame(parent, bg="#252538", padx=15, pady=12, bd=1, relief="solid")
        card.grid(row=0, column=col, padx=5, sticky="nsew")

        title_lbl = tk.Label(card, text=title, bg="#252538", fg="#A6ADC8", font=("Segoe UI", 9, "bold"))
        title_lbl.pack(anchor="w")

        val_lbl = tk.Label(card, text=default_val, bg="#252538", fg=val_color, font=("Segoe UI", 20, "bold"))
        val_lbl.pack(anchor="w", pady=(4, 0))

        return card, val_lbl

    def focus_entry(self):
        """Focus the typing entry box."""
        if not self.is_finished:
            self.entry.focus_set()

    def toggle_start_reset(self):
        """Toggle between starting the test and resetting it."""
        if self.is_running:
            self.reset_test()
        else:
            self.start_test()

    def start_test(self):
        """Explicitly start the typing test."""
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

        self.is_running = True
        self.is_finished = False
        self.start_time = time.time()

        self.start_btn.config(text="🔄 RESET TEST", bg="#F38BA8", fg="#1E1E2E")
        self.status_badge.config(text="⏱️ TEST IN PROGRESS - TYPE NOW!", fg="#89B4FA")
        self.entry.config(state=tk.NORMAL, bg="#313244", fg="#FFFFFF")
        self.entry_frame.config(bg="#89B4FA")
        self.entry_var.set("")
        self.focus_entry()

        self._tick()

    def _load_high_scores(self) -> dict:
        """Load saved high scores from JSON file."""
        if os.path.exists(HIGH_SCORES_FILE):
            try:
                with open(HIGH_SCORES_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"60": 0, "30": 0, "15": 0}

    def _save_high_scores(self):
        """Save high scores to JSON file."""
        try:
            with open(HIGH_SCORES_FILE, "w") as f:
                json.dump(self.high_scores, f, indent=2)
        except Exception:
            pass

    def _get_best_wpm(self) -> int:
        return self.high_scores.get(str(self.test_duration), 0)

    def change_duration(self):
        """Switch duration setting and reset the test."""
        self.test_duration = self.duration_var.get()
        self.best_val_lbl.config(text=f"{self._get_best_wpm()} WPM")
        self.reset_test()

    def reset_test(self):
        """Reset the test to initial ready state."""
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

        self.time_left = self.test_duration
        self.is_running = False
        self.is_finished = False
        self.start_time = None

        self.current_word_idx = 0
        self.correct_words = 0
        self.wrong_words = 0
        self.correct_chars = 0
        self.total_keystrokes = 0

        # Shuffle 150 random words
        self.words = [random.choice(WORD_BANK) for _ in range(150)]

        # Reset labels
        self.time_val_lbl.config(text=f"{self.time_left}s", fg="#FAB387")
        self.wpm_val_lbl.config(text="0")
        self.acc_val_lbl.config(text="100%")
        self.start_btn.config(text="▶️ START TEST", bg="#A6E3A1", fg="#1E1E2E")
        self.status_badge.config(text="🟢 Click 'START TEST' or start typing", fg="#A6E3A1")

        # Reset entry
        self.entry.config(state=tk.NORMAL, bg="#313244", fg="#FFFFFF")
        self.entry_frame.config(bg="#89B4FA")
        self.entry_var.set("")
        self.focus_entry()

        # Render words in display box
        self._render_words()

    def _render_words(self):
        """Populate and format the text widget with the current word bank."""
        self.text_display.config(state=tk.NORMAL)
        self.text_display.delete("1.0", tk.END)

        for word in self.words:
            self.text_display.insert(tk.END, word + " ")

        self.text_display.tag_add("upcoming", "1.0", tk.END)
        self._highlight_current_word()
        self.text_display.config(state=tk.DISABLED)

    def _highlight_current_word(self):
        """Highlight the active target word in the text display."""
        self.text_display.tag_remove("current", "1.0", tk.END)
        self.text_display.tag_remove("current_partial", "1.0", tk.END)
        self.text_display.tag_remove("current_error", "1.0", tk.END)

        if self.current_word_idx >= len(self.words):
            return

        start_idx = self._get_word_index_position(self.current_word_idx)
        end_idx = f"{start_idx} + {len(self.words[self.current_word_idx])}c"

        self.text_display.tag_add("current", start_idx, end_idx)
        self.text_display.see(start_idx)

    def _get_word_index_position(self, word_index: int) -> str:
        """Calculate the 'line.column' Tkinter index for a given word index."""
        char_offset = sum(len(self.words[i]) + 1 for i in range(word_index))
        return f"1.0 + {char_offset}c"

    def on_text_change(self, *args):
        """Live feedback on every letter typed."""
        if self.is_finished:
            return

        raw_text = self.entry_var.get()

        # If user pressed space (or space was entered in raw_text)
        if raw_text.endswith(" "):
            typed_word = raw_text.strip()
            if typed_word:
                self._submit_word(typed_word)
            self.entry_var.set("")
            return

        # Start timer on first keystroke WITHOUT erasing user's typed character
        if raw_text and not self.is_running:
            self.is_running = True
            self.is_finished = False
            self.start_time = time.time()
            self.start_btn.config(text="🔄 RESET TEST", bg="#F38BA8", fg="#1E1E2E")
            self.status_badge.config(text="⏱️ TEST IN PROGRESS - TYPE NOW!", fg="#89B4FA")
            self._tick()

        if not raw_text:
            self.entry.config(bg="#313244", fg="#FFFFFF")
            self.entry_frame.config(bg="#89B4FA")
            self._highlight_current_word()
            return

        self.total_keystrokes += 1

        if self.current_word_idx >= len(self.words):
            return

        target = self.words[self.current_word_idx]
        start_idx = self._get_word_index_position(self.current_word_idx)
        end_idx = f"{start_idx} + {len(target)}c"

        self.text_display.config(state=tk.NORMAL)
        self.text_display.tag_remove("current", start_idx, end_idx)
        self.text_display.tag_remove("current_partial", start_idx, end_idx)
        self.text_display.tag_remove("current_error", start_idx, end_idx)

        # Check if typed prefix matches target word so far
        if target.startswith(raw_text):
            # Correct letters typed
            self.entry.config(bg="#313244", fg="#A6E3A1")
            self.entry_frame.config(bg="#A6E3A1")
            self.text_display.tag_add("current_partial", start_idx, end_idx)
        else:
            # Typo detected
            self.entry.config(bg="#482B36", fg="#F38BA8")
            self.entry_frame.config(bg="#F38BA8")
            self.text_display.tag_add("current_error", start_idx, end_idx)

        self.text_display.config(state=tk.DISABLED)

    def on_space_pressed(self, event):
        """Trigger word evaluation when space or enter is pressed."""
        if self.is_finished:
            return "break"

        # Start timer if not running
        if not self.is_running:
            self.is_running = True
            self.is_finished = False
            self.start_time = time.time()
            self.start_btn.config(text="🔄 RESET TEST", bg="#F38BA8", fg="#1E1E2E")
            self.status_badge.config(text="⏱️ TEST IN PROGRESS - TYPE NOW!", fg="#89B4FA")
            self._tick()

        typed = self.entry_var.get().strip()
        if typed:
            self._submit_word(typed)

        self.entry_var.set("")
        return "break"

    def _submit_word(self, typed: str):
        """Evaluate the submitted word, update tags, metrics, and advance to next word."""
        if self.current_word_idx >= len(self.words):
            return

        target = self.words[self.current_word_idx]
        start_idx = self._get_word_index_position(self.current_word_idx)
        end_idx = f"{start_idx} + {len(target)}c"

        self.text_display.config(state=tk.NORMAL)
        self.text_display.tag_remove("upcoming", start_idx, end_idx)
        self.text_display.tag_remove("current", start_idx, end_idx)
        self.text_display.tag_remove("current_partial", start_idx, end_idx)
        self.text_display.tag_remove("current_error", start_idx, end_idx)

        if typed == target:
            self.correct_words += 1
            self.correct_chars += len(target) + 1  # include space
            self.text_display.tag_add("correct", start_idx, end_idx)
        else:
            self.wrong_words += 1
            self.text_display.tag_add("wrong", start_idx, end_idx)

        self.text_display.config(state=tk.DISABLED)

        # Reset entry styling for the next word
        self.entry.config(bg="#313244", fg="#FFFFFF")
        self.entry_frame.config(bg="#89B4FA")

        # Advance to the next word immediately
        self.current_word_idx += 1
        self._highlight_current_word()
        self._update_live_metrics()

    def _tick(self):
        """Recursive 1-second countdown loop."""
        if not self.is_running:
            return

        if self.time_left > 0:
            self.time_left -= 1
            self.time_val_lbl.config(text=f"{self.time_left}s")
            self._update_live_metrics()
            self.timer_job = self.root.after(1000, self._tick)
        else:
            self._finish_test()

    def _update_live_metrics(self):
        """Calculate and update WPM and Accuracy metrics in real time."""
        if not self.start_time:
            return

        elapsed_seconds = max(1.0, time.time() - self.start_time)
        elapsed_minutes = elapsed_seconds / 60.0

        # Net WPM formula: (correct characters / 5) / elapsed minutes
        wpm = int((self.correct_chars / 5.0) / elapsed_minutes)
        self.wpm_val_lbl.config(text=str(max(0, wpm)))

        # Accuracy
        total_attempted = self.correct_words + self.wrong_words
        if total_attempted > 0:
            acc = int((self.correct_words / total_attempted) * 100)
            self.acc_val_lbl.config(text=f"{acc}%")

    def _finish_test(self):
        """Handle test completion, calculate final scores, and display results modal."""
        self.is_running = False
        self.is_finished = True
        self.status_badge.config(text="🏁 TEST FINISHED", fg="#FAB387")
        self.start_btn.config(text="🔁 TRY AGAIN", bg="#89B4FA", fg="#1E1E2E")
        self.entry.config(state=tk.DISABLED, bg="#252538")
        self.entry_frame.config(bg="#45475A")

        elapsed_minutes = self.test_duration / 60.0
        final_wpm = int((self.correct_chars / 5.0) / elapsed_minutes)
        final_wpm = max(0, final_wpm)

        total_attempted = self.correct_words + self.wrong_words
        accuracy = int((self.correct_words / total_attempted) * 100) if total_attempted > 0 else 0

        # Check high score
        dur_key = str(self.test_duration)
        prev_best = self.high_scores.get(dur_key, 0)
        is_new_record = final_wpm > prev_best

        if is_new_record:
            self.high_scores[dur_key] = final_wpm
            self._save_high_scores()
            self.best_val_lbl.config(text=f"{final_wpm} WPM")

        self._show_results_dialog(final_wpm, accuracy, is_new_record)

    def _show_results_dialog(self, wpm: int, accuracy: int, is_new_record: bool):
        """Display an attractive results summary popup."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Test Complete!")
        dialog.geometry("460x430")
        dialog.resizable(False, False)
        dialog.configure(bg="#1E1E2E")
        dialog.transient(self.root)
        dialog.grab_set()

        # Center dialog relative to main window
        self.root.update_idletasks()
        rx = self.root.winfo_x() + (self.root.winfo_width() // 2) - 230
        ry = self.root.winfo_y() + (self.root.winfo_height() // 2) - 215
        dialog.geometry(f"+{rx}+{ry}")

        content = tk.Frame(dialog, bg="#1E1E2E", padx=25, pady=25)
        content.pack(fill=tk.BOTH, expand=True)

        badge_text = "🎉 NEW PERSONAL RECORD!" if is_new_record else "Test Completed!"
        badge_fg = "#F9E2AF" if is_new_record else "#89B4FA"
        tk.Label(content, text=badge_text, font=("Segoe UI", 14, "bold"), bg="#1E1E2E", fg=badge_fg).pack(pady=(0, 10))

        # Main WPM score banner
        wpm_box = tk.Frame(content, bg="#252538", padx=20, pady=15, bd=1, relief="solid")
        wpm_box.pack(fill=tk.X, pady=(0, 15))

        tk.Label(wpm_box, text=f"{wpm}", font=("Segoe UI", 36, "bold"), bg="#252538", fg="#A6E3A1").pack()
        tk.Label(wpm_box, text="Words Per Minute (WPM)", font=("Segoe UI", 10), bg="#252538", fg="#A6ADC8").pack()

        # Detailed breakdown
        details = [
            ("Accuracy", f"{accuracy}%"),
            ("Correct Words", f"{self.correct_words}"),
            ("Errors", f"{self.wrong_words}"),
            ("Total Keystrokes", f"{self.total_keystrokes}"),
            (f"Best ({self.test_duration}s)", f"{self.high_scores.get(str(self.test_duration), 0)} WPM")
        ]

        details_frame = tk.Frame(content, bg="#1E1E2E")
        details_frame.pack(fill=tk.X, pady=(0, 20))

        for label, val in details:
            row = tk.Frame(details_frame, bg="#1E1E2E")
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=label, bg="#1E1E2E", fg="#A6ADC8", font=("Segoe UI", 9)).pack(side=tk.LEFT)
            tk.Label(row, text=val, bg="#1E1E2E", fg="#CDD6F4", font=("Segoe UI", 9, "bold")).pack(side=tk.RIGHT)

        # Action Buttons
        btn_frame = tk.Frame(content, bg="#1E1E2E")
        btn_frame.pack(fill=tk.X)

        def restart_and_close():
            dialog.destroy()
            self.reset_test()

        play_again_btn = tk.Button(
            btn_frame, text="🔁 Try Again", command=restart_and_close,
            bg="#89B4FA", fg="#1E1E2E", font=("Segoe UI", 10, "bold"),
            relief="flat", pady=8, cursor="hand2"
        )
        play_again_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        close_btn = tk.Button(
            btn_frame, text="Close", command=dialog.destroy,
            bg="#313244", fg="#CDD6F4", font=("Segoe UI", 10),
            relief="flat", pady=8, cursor="hand2"
        )
        close_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))


def main():
    root = tk.Tk()
    app = TypingSpeedTestApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
