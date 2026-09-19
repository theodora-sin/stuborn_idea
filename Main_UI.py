"""
Temu Sign Up Page - main UI
----------------------------
Combines everything that used to live in separate scripts into one
cohesive, styled tkinter app:

  password.py    -> ever-changing password rules            (evaluate_password)
  timer.py       -> countdown that wipes the form            (Countdown section)
  termandcon.py  -> scrollable, timed Terms & Conditions      (build_terms_section)
  date.py        -> "Pi Birthday Generator" instead of a      (build_birthday_section)
                    normal date-of-birth field
  rickroll.py    -> the "reward" for hitting Create Account   (rickroll)

Run with:  python stubborn_signup.py
(Needs tkinter, which ships with most Python installs. On some Linux
distros you may need to `sudo apt install python3-tk` first.)
"""

import tkinter as tk
from tkinter import ttk
import random
import calendar
import webbrowser

# ---------------------------------------------------------------------------
# Theme - loud orange/red "Temu" palette on a white background
# ---------------------------------------------------------------------------
BG = "#fff4ea"
CARD = "#ffffff"
ENTRY_BG = "#fff7f0"
BORDER = "#ffb37a"
TEXT = "#231a12"
MUTED = "#8a7361"
ACCENT = "#fb7701"
ACCENT_DARK = "#e35f00"
SUCCESS = "#2ecc71"
ERROR = "#ff3b30"

FONT_TITLE = ("Segoe UI", 21, "bold")
FONT_SUB = ("Segoe UI", 10)
FONT_LABEL = ("Segoe UI", 10, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_MONO = ("Consolas", 22, "bold")
FONT_BTN = ("Segoe UI", 11, "bold")

TOTAL_TIME = 45  # seconds before the form gets wiped

RICKROLL_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# First few hundred digits of pi, reused from the original date.py generator.
PI_DIGITS = (
    "14159265358979323846264338327950288419716939937510582097494459230781640628"
    "62089986280348253421170679821480865132823066470938446095505822317253594081"
    "28481117450284102701938521105559644622948954930381964428810975665933446128"
    "47564823378678316527120190914564856692346034861045432664821339360726024914"
)

TERMS_TEXT = """TERMS AND CONDITIONS

Last Updated: 18/9/2026

1. Acceptance of Terms
   By creating an account, you agree to be bound by these Terms and
   Conditions. If you do not agree, please do not proceed with registration.

2. Eligibility
   You must provide accurate information, including a truthful date and
   time of birth, and you confirm that you meet any minimum age
   requirement that applies in your jurisdiction.

3. Account Security
   You are responsible for maintaining the confidentiality of your
   password and for all activity that occurs under your account. Notify
   us immediately of any unauthorized use.

4. Acceptable Use
   You agree not to misuse the software, attempt to bypass its security
   controls, or use it for any unlawful purpose.

5. Data Handling
   Information you provide is stored to operate your account. We do not
   sell your personal data to third parties.

6. Governing Law
   These terms are governed by the laws applicable in your place of
   residence, without regard to conflict-of-law principles.

7. Contact
   Questions about these terms can be directed to the software's support
   channel.

-- End of Terms and Conditions --
"""


# ---------------------------------------------------------------------------
# Password rule engine (ported from password.py, logic unchanged)
# ---------------------------------------------------------------------------
def evaluate_password(pw):
    """Return (message, is_accepted) for a password, using the exact same
    ever-shifting rules as the original standalone password.py."""
    if pw == "":
        return "Enter a password to begin.", False

    checks = [
        (lambda p: len(p) < 8, "Password must be at least 8 characters."),
        (lambda p: len(p) < 12, "Actually... make it 12 characters."),
        (lambda p: "password" in p.lower(), "Nice try. You can't use 'password'."),
        (lambda p: "123" in p, "Too predictable. No 123..."),
        (lambda p: p.islower(), "You need a capital letter."),
        (lambda p: p.isupper(), "You need a lowercase letter."),
        (lambda p: not any(c.isdigit() for c in p), "You need a number."),
        (lambda p: not any(not c.isalnum() for c in p), "You need a special character."),
        (lambda p: "banana" not in p.lower(), "Your password must contain 'banana'."),
        (lambda p: "banana" in p.lower(), "Actually, we don't allow bananas."),
        (lambda p: "42" not in p, "Your password must contain the answer to everything."),
        (lambda p: len(p) < 20, "20 characters minimum. We changed our minds."),
        (lambda p: len(p) > 25, "That's too long. Please calm down."),
        (lambda p: "!" not in p, "Where is the enthusiasm?  !"),
        (lambda p: p.count("!") < 3, "One ! is not enough. We need THREE."),
        (lambda p: "?" in p, "Don't question our password policy."),
        (lambda p: " " in p, "Passwords cannot contain spaces. Obviously."),
        (lambda p: p[0].isdigit(), "Your password cannot start with a number."),
        (lambda p: p[-1].isdigit(), "Your password cannot end with a number."),
        (lambda p: "admin" in p.lower(), "You are not allowed to be admin."),
        (lambda p: "hello" in p.lower(), "Don't say hello to us."),
        (lambda p: p.lower() == p.lower()[::-1], "Palindrome passwords are forbidden."),
        (lambda p: len(set(p)) < 5, "Your password lacks personality."),
        (lambda p: len(p) == 13, "Your password is too confident."),
        (lambda p: "terms" in p.lower(), "This password has violated our terms and conditions."),
        (lambda p: p.count("a") > 3, "We don't like that password."),
        (lambda p: p.lower().startswith("v"), "Password rejected. Reason: vibes."),
        (lambda p: p.count("e") == 0, "Please choose a password that makes us happier."),
        (lambda p: p.lower().startswith("pass"), "This password is suspiciously password-like."),
        (lambda p: p.count("!") > 5, "Our lawyers don't like this password."),
        (lambda p: p.endswith("."), "Password accepted. Just kidding."),
        (lambda p: len(p) == 47, "Password almost accepted. Please wait 47 business days."),
        (lambda p: p.lower() == "nobody", "This password is already being used by someone who doesn't exist."),
        (lambda p: p.count("p") >= 3, "Your password has been sent to our password department."),
        (lambda p: len(set(p)) == 1, "Password rejected due to insufficient passwordness."),
    ]
    for condition, message in checks:
        if condition(pw):
            return message, False
    return "Password accepted! ...probably.", True


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
class StubbornSignupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Temu Sign Up Page")
        self.root.configure(bg=BG)
        self.root.geometry("560x760")
        self.root.minsize(480, 600)

        self.form_state = {
            "password_ok": False,
            "terms_ok": False,
            "birthday_ok": False,
        }
        self.time_left = TOTAL_TIME
        self._countdown_job = None

        self._build_style()
        self._build_layout()
        self._start_countdown()

    # -- styling --------------------------------------------------------
    def _build_style(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background=CARD)
        style.configure("Root.TFrame", background=BG)
        style.configure("TLabel", background=CARD, foreground=TEXT, font=FONT_BODY)
        style.configure("Title.TLabel", background=BG, foreground=TEXT, font=FONT_TITLE)
        style.configure("Sub.TLabel", background=BG, foreground=MUTED, font=FONT_SUB)
        style.configure("Header.TLabel", background=CARD, foreground=ACCENT, font=FONT_LABEL)
        style.configure("Timer.TLabel", background=BG, foreground=ERROR, font=FONT_LABEL)
        style.configure("Field.TLabel", background=CARD, foreground=MUTED, font=FONT_LABEL)

        style.configure(
            "Accent.TButton",
            background=ACCENT,
            foreground="#1a1a1a",
            font=FONT_BTN,
            borderwidth=0,
            padding=8,
        )
        style.map("Accent.TButton", background=[("active", ACCENT_DARK)])

        style.configure(
            "Ghost.TButton",
            background=CARD,
            foreground=TEXT,
            font=FONT_BODY,
            borderwidth=1,
            padding=6,
        )
        style.map("Ghost.TButton", background=[("active", BORDER)])

        style.configure("TCheckbutton", background=CARD, foreground=TEXT, font=FONT_BODY)
        style.map("TCheckbutton", background=[("active", CARD)])

        style.configure("TLabelframe", background=CARD, bordercolor=BORDER)
        style.configure("TLabelframe.Label", background=CARD, foreground=ACCENT, font=FONT_LABEL)

        style.configure(
            "Vertical.TScrollbar",
            background=CARD,
            troughcolor=BG,
            bordercolor=BG,
            arrowcolor=TEXT,
        )

    def _entry(self, parent, **kwargs):
        e = tk.Entry(
            parent,
            bg=ENTRY_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
            font=FONT_BODY,
            **kwargs,
        )
        return e

    # -- layout -----------------------------------------------------------
    def _build_layout(self):
        # Header (fixed, outside the scroll area)
        header = ttk.Frame(self.root, style="Root.TFrame", padding=(20, 18, 20, 6))
        header.pack(fill="x")
        ttk.Label(header, text="Temu Sign Up Page", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header, text="Join now! Limited time offer!! (offer never ends)", style="Sub.TLabel"
        ).pack(anchor="w", pady=(2, 8))

        self.timer_label = ttk.Label(header, text="", style="Timer.TLabel")
        self.timer_label.pack(anchor="w")

        # Scrollable body
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        self.body = ttk.Frame(canvas, style="Root.TFrame")

        self.body.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.body, anchor="nw", width=520)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows / macOS
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

        self._build_account_section()
        self._build_password_section()
        self._build_birthday_section()
        self._build_terms_section()
        self._build_submit_section()

    def _card(self, title):
        frame = ttk.Frame(self.body, padding=16)
        frame.pack(fill="x", pady=(0, 14))
        ttk.Label(frame, text=title, style="Header.TLabel").pack(anchor="w", pady=(0, 10))
        return frame

    # -- section: username --------------------------------------------
    def _build_account_section(self):
        card = self._card("Account details")
        ttk.Label(card, text="USERNAME", style="Field.TLabel").pack(anchor="w")
        self.username_entry = self._entry(card)
        self.username_entry.pack(fill="x", pady=(4, 0), ipady=4)

    # -- section: password ----------------------------------------------
    def _build_password_section(self):
        card = self._card("Choose a password")
        ttk.Label(card, text="PASSWORD", style="Field.TLabel").pack(anchor="w")

        row = ttk.Frame(card)
        row.pack(fill="x", pady=(4, 8))
        self.password_entry = self._entry(row, show="\u2022")
        self.password_entry.pack(side="left", fill="x", expand=True, ipady=4)
        ttk.Button(
            row, text="Check", style="Ghost.TButton", command=self._check_password
        ).pack(side="left", padx=(8, 0))

        self.password_feedback = ttk.Label(
            card, text="Enter a password to begin.", foreground=MUTED, wraplength=460
        )
        self.password_feedback.pack(anchor="w")

    def _check_password(self):
        pw = self.password_entry.get()
        message, ok = evaluate_password(pw)
        self.form_state["password_ok"] = ok
        self.password_feedback.config(
            text=message, foreground=SUCCESS if ok else ERROR
        )
        self._refresh_submit_state()

    # -- section: birthday (pi generator) --------------------------------
    def _build_birthday_section(self):
        card = self._card("Date of birth")
        ttk.Label(
            card,
            text=(
                "We don't trust you to type your own birthday, so instead you'll "
                "pull a random 6-digit sequence out of the digits of pi. Each click "
                "below drops you at a new random position in pi and reads off the "
                "next 6 digits as DD/MM/YY. Keep clicking \"Roll again\" until the "
                "sequence you land on actually matches your real birthday - that's "
                "the only correct one, everything else doesn't count."
            ),
            foreground=MUTED,
            wraplength=460,
            justify="left",
        ).pack(anchor="w", pady=(0, 10))

        reel = ttk.Frame(card)
        reel.pack(anchor="w")
        self.birthday_slots = []
        for i in range(6):
            if i in (2, 4):
                tk.Label(reel, text="/", font=FONT_MONO, bg=CARD, fg=MUTED).pack(side="left")
            slot = tk.Label(
                reel,
                text="-",
                font=FONT_MONO,
                width=2,
                bg=ENTRY_BG,
                fg=TEXT,
                relief="flat",
                highlightthickness=1,
                highlightbackground=BORDER,
            )
            slot.pack(side="left", padx=2)
            self.birthday_slots.append(slot)

        self.birthday_status = ttk.Label(
            card, text="No birthday generated yet.", foreground=MUTED
        )
        self.birthday_status.pack(anchor="w", pady=(10, 10))

        self.birthday_btn = ttk.Button(
            card,
            text="Generate my birthday",
            style="Accent.TButton",
            command=self._generate_birthday,
        )
        self.birthday_btn.pack(anchor="w")

    def _get_pi_birthday(self):
        while True:
            i = random.randint(0, len(PI_DIGITS) - 1)
            seq = "".join(PI_DIGITS[(i + j) % len(PI_DIGITS)] for j in range(6))
            d, m, y = int(seq[:2]), int(seq[2:4]), int(seq[4:])
            if 1 <= m <= 12 and 1 <= d <= calendar.monthrange(2000 + y, m)[1]:
                return seq

    def _generate_birthday(self):
        self.birthday_btn.config(state="disabled")
        self.birthday_status.config(text="Rolling...", foreground=MUTED)
        seq = self._get_pi_birthday()

        def reveal(pos, ticks=6):
            if pos == 6:
                self.form_state["birthday_ok"] = True
                self.birthday_status.config(
                    text=f"Your assigned birthday: {seq[:2]}/{seq[2:4]}/{seq[4:]}",
                    foreground=SUCCESS,
                )
                self.birthday_btn.config(state="normal", text="Generate a different one")
                self._refresh_submit_state()
                return
            self.birthday_slots[pos].config(
                text=str(random.randint(0, 9)) if ticks else seq[pos]
            )
            self.root.after(
                40, reveal, pos if ticks else pos + 1, max(ticks - 1, 0) if ticks else 6
            )

        reveal(0)

    def _reset_birthday(self):
        self.form_state["birthday_ok"] = False
        for slot in self.birthday_slots:
            slot.config(text="-")
        self.birthday_status.config(text="No birthday generated yet.", foreground=MUTED)
        self.birthday_btn.config(state="normal", text="Generate my birthday")

    # -- section: terms & conditions --------------------------------------
    def _build_terms_section(self):
        card = self._card("Terms and Conditions")

        text_frame = tk.Frame(card, bg=CARD)
        text_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(text_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.terms_widget = tk.Text(
            text_frame,
            wrap="word",
            height=10,
            bg=ENTRY_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            font=("Consolas", 9),
            yscrollcommand=scrollbar.set,
        )
        self.terms_widget.insert("1.0", TERMS_TEXT)
        self.terms_widget.config(state="disabled")
        self.terms_widget.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.terms_widget.yview)

        word_count = len(TERMS_TEXT.split())
        self.terms_min_seconds = max(8, int(word_count / 200 * 60))
        self.terms_read_state = {
            "scrolled_to_bottom": False,
            "min_time_elapsed": False,
            "seconds_remaining": self.terms_min_seconds,
        }

        self.terms_progress = ttk.Label(
            card,
            text=f"Please read the full document (~{self.terms_min_seconds}s).",
            foreground=MUTED,
            wraplength=460,
        )
        self.terms_progress.pack(anchor="w", pady=(8, 0))

        self.terms_timer_label = ttk.Label(card, text="", foreground=MUTED)
        self.terms_timer_label.pack(anchor="w")

        self.terms_agree_var = tk.BooleanVar(value=False)
        self.terms_check = ttk.Checkbutton(
            card,
            text="I have read and agree to the Terms and Conditions",
            variable=self.terms_agree_var,
            state="disabled",
            command=self._on_terms_change,
        )
        self.terms_check.pack(anchor="w", pady=(8, 0))

        def check_scroll_position():
            top, bottom = self.terms_widget.yview()
            if bottom >= 0.999:
                self.terms_read_state["scrolled_to_bottom"] = True
                self._try_unlock_terms()

        def on_scroll_event(event=None):
            card.after(50, check_scroll_position)

        def on_key_scroll(event):
            if event.keysym == "End":
                return "break"
            card.after(50, check_scroll_position)

        self.terms_widget.bind("<MouseWheel>", on_scroll_event)
        self.terms_widget.bind("<Button-4>", on_scroll_event)
        self.terms_widget.bind("<Button-5>", on_scroll_event)
        scrollbar.bind("<B1-Motion>", on_scroll_event)
        scrollbar.bind("<ButtonRelease-1>", on_scroll_event)
        self.terms_widget.bind("<Key>", on_key_scroll)

        self._tick_terms_countdown()

    def _try_unlock_terms(self):
        state = self.terms_read_state
        if state["scrolled_to_bottom"] and state["min_time_elapsed"]:
            self.terms_check.config(state="normal")
            self.terms_progress.config(
                text="Thanks for reading. You may now tick the box.", foreground=SUCCESS
            )
            self.terms_timer_label.config(text="")
            return
        missing = []
        if not state["scrolled_to_bottom"]:
            missing.append("scroll to the end")
        if not state["min_time_elapsed"]:
            missing.append("finish the minimum reading time")
        self.terms_progress.config(text="Please " + " and ".join(missing) + ".", foreground=MUTED)

    def _tick_terms_countdown(self):
        remaining = self.terms_read_state["seconds_remaining"]
        if remaining <= 0:
            self.terms_timer_label.config(text="")
            self.terms_read_state["min_time_elapsed"] = True
            self._try_unlock_terms()
            return
        self.terms_timer_label.config(text=f"Time remaining before you can tick the box: {remaining}s")
        self.terms_read_state["seconds_remaining"] = remaining - 1
        self.root.after(1000, self._tick_terms_countdown)

    def _on_terms_change(self):
        self.form_state["terms_ok"] = self.terms_agree_var.get()
        self._refresh_submit_state()

    def _reset_terms(self):
        self.terms_read_state["scrolled_to_bottom"] = False
        self.terms_read_state["min_time_elapsed"] = False
        self.terms_read_state["seconds_remaining"] = self.terms_min_seconds
        self.terms_agree_var.set(False)
        self.terms_check.config(state="disabled")
        self.terms_widget.yview_moveto(0)
        self.terms_progress.config(
            text=f"Please read the full document (~{self.terms_min_seconds}s).", foreground=MUTED
        )
        self.form_state["terms_ok"] = False
        self._tick_terms_countdown()

    # -- section: submit -----------------------------------------------
    def _build_submit_section(self):
        card = self._card("Finish up")
        self.submit_hint = ttk.Label(
            card, text="Fill everything above to unlock account creation.", foreground=MUTED, wraplength=460
        )
        self.submit_hint.pack(anchor="w", pady=(0, 10))

        self.submit_btn = ttk.Button(
            card, text="Create Account", style="Accent.TButton", command=self._on_submit
        )
        self.submit_btn.pack(anchor="w")

    def _refresh_submit_state(self):
        missing = []
        if not self.form_state["password_ok"]:
            missing.append("an accepted password")
        if not self.form_state["birthday_ok"]:
            missing.append("a generated birthday")
        if not self.form_state["terms_ok"]:
            missing.append("agreement to the Terms")
        if missing:
            self.submit_hint.config(
                text="Still needed: " + ", ".join(missing) + ".", foreground=MUTED
            )
        else:
            self.submit_hint.config(
                text="Everything looks in order. Ready when you are.", foreground=SUCCESS
            )

    def _on_submit(self):
        if not self.username_entry.get().strip():
            self.submit_hint.config(text="You forgot a username.", foreground=ERROR)
            return
        if not all(self.form_state.values()):
            self._refresh_submit_state()
            return
        # Everything is satisfied - time for the real reward.
        webbrowser.open(RICKROLL_URL)

    # -- countdown that wipes the form -----------------------------------
    def _start_countdown(self):
        self.time_left = TOTAL_TIME
        self._tick_countdown()

    def _tick_countdown(self):
        if self.time_left <= 0:
            self.timer_label.config(text="TIME'S UP! Starting over...")
            self.root.after(900, self._reset_form)
            return
        self.timer_label.config(text=f"Time remaining to complete signup: {self.time_left}s")
        self.time_left -= 1
        self._countdown_job = self.root.after(1000, self._tick_countdown)

    def _reset_form(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.password_feedback.config(text="Enter a password to begin.", foreground=MUTED)
        self.form_state["password_ok"] = False
        self._reset_birthday()
        self._reset_terms()
        self._refresh_submit_state()
        self._start_countdown()


def main():
    root = tk.Tk()
    StubbornSignupApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
