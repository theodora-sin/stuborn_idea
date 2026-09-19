import tkinter as tk
from tkinter import ttk, messagebox

from termandcon import TERMS_TEXT

#Roughly how many words a reader get through per minutes
READING_WORDS_PER_MINUTE = 200
MIN_READ_SECONDS= (8, int(len(TERMS_TEXT.split()) / READING_WORDS_PER_MINUTE * 60))

class RegistrationApp(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=15)
        self.pack(fill="both", expand=True)
 
        self._scrolled_to_bottom = False
        self._min_time_elapsed = False
 
        self._build_username_section()
        self._build_birthday_section()
        self._build_password_section()
        self._build_terms_section()
        self._build_submit_section()
 
        # Start the minimum-reading-time countdown as soon as the window opens.
        self.after(MIN_READ_SECONDS * 1000, self._mark_time_elapsed)
 
    # ------------------------------------------------------------------
    def _build_username_section(self):
        frame = ttk.LabelFrame(self, text="Username")
        frame.pack(fill="x", pady=(0, 10))
 
        self.username_var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=self.username_var, width=30)
        entry.grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.username_var.trace_add("write", lambda *a: self._refresh_submit_state())
 
    def _build_birthday_section(self):
        self.birthday_widget = BirthdayTimeWidget(self)
        self.birthday_widget.pack(fill="x", pady=(0, 10))
        self._poll_birthday_validity()
 
    def _poll_birthday_validity(self):
        self._refresh_submit_state()
        self.after(300, self._poll_birthday_validity)
 
    def _build_password_section(self):
        self.password_widget = PasswordWidget(self)
        self.password_widget.pack(fill="x", pady=(0, 10))
        self.password_widget.password_var.trace_add(
            "write", lambda *a: self._refresh_submit_state()
        )
 
    def _build_terms_section(self):
        frame = ttk.LabelFrame(self, text="Terms and Conditions")
        frame.pack(fill="both", expand=True, pady=(0, 10))
 
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill="both", expand=True, padx=8, pady=8)
 
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
 
        self.terms_text = tk.Text(
            text_frame, wrap="word", height=10, width=60,
            yscrollcommand=scrollbar.set
        )
        self.terms_text.insert("1.0", TERMS_TEXT)
        self.terms_text.config(state="disabled")  # read-only, but still scrollable
        self.terms_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.terms_text.yview)
 
        # Detect genuine scrolling to the bottom.
        self.terms_text.bind("<MouseWheel>", self._on_scroll_event)   # Windows/Mac
        self.terms_text.bind("<Button-4>", self._on_scroll_event)     # Linux up
        self.terms_text.bind("<Button-5>", self._on_scroll_event)     # Linux down
        scrollbar.bind("<B1-Motion>", self._on_scroll_event)
        scrollbar.bind("<ButtonRelease-1>", self._on_scroll_event)
        self.terms_text.bind("<Key>", self._on_key_scroll)
 
        self.progress_label = ttk.Label(
            frame, text=f"Please read the full document (~{MIN_READ_SECONDS}s)."
        )
        self.progress_label.pack(anchor="w", padx=8)
 
        self.agree_var = tk.BooleanVar(value=False)
        self.agree_check = ttk.Checkbutton(
            frame, text="I have read and agree to the Terms and Conditions",
            variable=self.agree_var, state="disabled",
            command=self._refresh_submit_state
        )
        self.agree_check.pack(anchor="w", padx=8, pady=(4, 8))
 
    def _build_submit_section(self):
        self.submit_btn = ttk.Button(
            self, text="Submit", state="disabled", command=self._on_submit
        )
        self.submit_btn.pack(pady=(5, 0))
 
    # ------------------------------------------------------------------
    # Terms & Conditions gating logic
    # ------------------------------------------------------------------
    def _on_key_scroll(self, event):
        """
        Block keys that would let the user leap straight to the bottom
        without actually scrolling through the content (e.g. Ctrl+End).
        Arrow keys / Page Up / Page Down are still allowed since those
        still require the user to move through the document.
        """
        blocked_keys = {"End"}
        if event.keysym in blocked_keys:
            return "break"
        # After any allowed key movement, re-check scroll position shortly after.
        self.after(50, self._check_scroll_position)
 
    def _on_scroll_event(self, event=None):
        # Let the scroll happen, then check position shortly after.
        self.after(50, self._check_scroll_position)
 
    def _check_scroll_position(self):
        top, bottom = self.terms_text.yview()
        if bottom >= 0.999:
            self._scrolled_to_bottom = True
            self._try_unlock_checkbox()
 
    def _mark_time_elapsed(self):
        self._min_time_elapsed = True
        self._try_unlock_checkbox()
 
    def _try_unlock_checkbox(self):
        if self._scrolled_to_bottom and self._min_time_elapsed:
            self.agree_check.config(state="normal")
            self.progress_label.config(text="Thanks for reading. You may now tick the box.")
        else:
            missing = []
            if not self._scrolled_to_bottom:
                missing.append("scroll to the end")
            if not self._min_time_elapsed:
                missing.append("finish the minimum reading time")
            self.progress_label.config(text="Please " + " and ".join(missing) + ".")
 
    # ------------------------------------------------------------------
    # Overall form validity
    # ------------------------------------------------------------------
    def _refresh_submit_state(self):
        username_ok = len(self.username_var.get().strip()) > 0
        birthday_ok = self.birthday_widget.is_valid()
        password_ok = len(self.password_widget.get()) > 0
        agree_ok = self.agree_var.get()
 
        if username_ok and birthday_ok and password_ok and agree_ok:
            self.submit_btn.config(state="normal")
        else:
            self.submit_btn.config(state="disabled")
 
    def _on_submit(self):
        data = {
            "username": self.username_var.get().strip(),
            "birthday": self.birthday_widget.get(),
            "password": self.password_widget.get(),
            "agreed_to_terms": self.agree_var.get(),
        }
        # Replace this with your real submit/save logic.
        messagebox.showinfo("Submitted", f"Account created for '{data['username']}'.")
        print(data)
 
 
def main():
    root = tk.Tk()
    root.title("Create Account")
    root.geometry("560x640")
    RegistrationApp(root)
    root.mainloop()
 
 
if __name__ == "__main__":
    main()