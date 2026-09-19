"""
Temu Sign Up Page - main UI
----------------------------
Combines everything into one cohesive, styled tkinter app:

  calculator.py  -> rigged "verify you're human" calculator   (build_calculator_section)
  password.py    -> ever-changing password rules              (evaluate_password)
  timer.py       -> countdown that wipes the form             (Countdown section)
  termandcon.py  -> scrollable, timed Terms & Conditions       (build_terms_section)
  date.py        -> "Pi Birthday Generator" instead of a       (build_birthday_section)
                    normal date-of-birth field
  rickroll.py    -> the "reward" for hitting Create Account    (rickroll)

Run with:  python stubborn_signup.py
(Needs tkinter, which ships with most Python installs. On some Linux
distros you may need to `sudo apt install python3-tk` first.)

Keep duck.png in the SAME FOLDER as this file - the rubber duck popup
loads it from disk. If duck.png is missing, or Pillow isn't installed,
it quietly falls back to a plain duck emoji instead.
"""

import tkinter as tk
from tkinter import ttk
import random
import calendar
import webbrowser
import os

try:
    from PIL import Image, ImageTk
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False

# ---------------------------------------------------------------------------
# Theme - deliberately garish, clashing "so-bad-it-hurts" palette.
# Loud lime background, hot-pink cards, screaming yellow fields, comic
# fonts everywhere - a design that looks broken on purpose.
# ---------------------------------------------------------------------------
BG = "#ccff00"
CARD = "#ff66cc"
ENTRY_BG = "#fff200"
BORDER = "#ff0000"
TEXT = "#0d0d0d"
MUTED = "#6600cc"
ACCENT = "#00e5ff"
ACCENT_DARK = "#0099ff"
SUCCESS = "#39ff14"
ERROR = "#ff0033"

FONT_TITLE = ("Comic Sans MS", 24, "bold")
FONT_SUB = ("Comic Sans MS", 11, "bold")
FONT_LABEL = ("Comic Sans MS", 11, "bold")
FONT_BODY = ("Comic Sans MS", 10)
FONT_MONO = ("Comic Sans MS", 22, "bold")
FONT_BTN = ("Comic Sans MS", 13, "bold")
FONT_CALC_DISPLAY = ("Comic Sans MS", 18, "bold")
FONT_MARQUEE = ("Comic Sans MS", 13, "bold")

TOTAL_TIME = 45  # seconds before the form gets wiped

RICKROLL_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

DUCK_IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "duck.png")
DUCK_IMAGE_SIZE = (130, 140)  # resized display size for the popup duck
DUCK_INTERVAL_MS = 5000  # a new duck pops up this often
DUCK_LIFETIME_MS = 8000  # each duck disappears on its own after this long
DUCK_BG = "#ffd400"  # solid yellow behind the duck - no more pink showing through

DODGE_AREA_SIZE = (460, 90)  # room the username field is allowed to roam in
DODGE_THRESHOLD_PX = 55  # how close the mouse has to get before it flees

# Colors the header/marquee/submit button strobe through - ugly on purpose.
STROBE_COLORS = ["#ff0033", "#00e5ff", "#39ff14", "#fff200", "#ff66cc", "#9900ff"]

MARQUEE_MESSAGES = [
    "!!! LIMITED TIME OFFER !!!",
    "*** ACT NOW OR REGRET FOREVER ***",
    ">>> 9,999,999 PEOPLE SIGNED UP TODAY <<<",
    "!!! DO NOT CLOSE THIS WINDOW !!!",
    "*** YOU HAVE BEEN SELECTED ***",
]

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
# Password rule engine (logic unchanged)
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
# Calculator "human verification" engine (capture / recapture)
# ---------------------------------------------------------------------------
def make_calculation():
    """
    Generate a hard multiplication or division question.
    Returns (a, b, op, correct_answer).
    """
    op = random.choice(["*", "/"])

    if op == "*":
        a = random.randint(100, 999)
        b = random.randint(100, 999)
        answer = a * b
    else:
        # Build a division question that still has a clean whole-number
        # answer, but with large operands so it's genuinely hard.
        divisor = random.randint(12, 97)
        quotient = random.randint(100, 999)
        a = divisor * quotient
        b = divisor
        answer = quotient

    return a, b, op, answer


def real_calculate(num1, op, num2):
    """The genuinely correct calculation."""
    if op == "+":
        return num1 + num2
    elif op == "-":
        return num1 - num2
    elif op == "*":
        return num1 * num2
    else:
        return num1 / num2 if num2 != 0 else 0


def wrong_calculate(num1, op, num2):
    """Deliberately uses a different operator to get a wrong answer."""
    other_ops = [o for o in ("+", "-", "*", "/") if o != op]
    wrong_op = random.choice(other_ops)
    return real_calculate(num1, wrong_op, num2)


def rigged_calculate(num1, op, num2, attempt_number):
    """Wrong method on attempts 1-2, correct method on attempt 3."""
    if attempt_number < 3:
        return wrong_calculate(num1, op, num2)
    else:
        return real_calculate(num1, op, num2)


def parse_expression(expr):
    """
    Parse a typed expression like '948*383' into (num1, op, num2).
    Returns None if it can't be parsed.
    """
    for op in ("+", "-", "*", "/"):
        # skip a leading '-' so we don't split a negative first number
        search_area = expr[1:] if expr.startswith("-") else expr
        if op in search_area:
            index = expr.index(op, 1) if expr.startswith("-") else expr.index(op)
            left = expr[:index]
            right = expr[index + 1:]
            try:
                return float(left), op, float(right)
            except ValueError:
                return None
    return None


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
class StubbornSignupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Temu Sign Up Page")
        self.root.configure(bg=BG)
        self.root.geometry("560x900")
        self.root.minsize(480, 640)

        self.form_state = {
            "password_ok": False,
            "calculator_ok": False,
            "birthday_ok": False,
            "terms_ok": False,
        }
        self.time_left = TOTAL_TIME
        self._countdown_job = None

        # calculator state
        self.calc_attempt = 1
        self.calc_problem = None  # (a, b, op, correct_answer)

        # strobe/marquee state (purely cosmetic - part of the "bad on
        # purpose" aesthetic)
        self._strobe_index = 0
        self._marquee_index = 0

        self._duck_image = self._load_duck_image()

        self._build_style()
        self._build_layout()
        self._start_countdown()
        self._tick_strobe()
        self._tick_marquee()
        self._tick_duck()

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

        style.configure(
            "Calc.TButton",
            background=ENTRY_BG,
            foreground=TEXT,
            font=FONT_BTN,
            borderwidth=1,
            padding=10,
        )
        style.map("Calc.TButton", background=[("active", BORDER)])

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
        # Flashing, obnoxious marquee strip - plain tk.Label so its colors
        # can be strobed freely without fighting the ttk style system.
        self.marquee_label = tk.Label(
            self.root,
            text=MARQUEE_MESSAGES[0],
            font=FONT_MARQUEE,
            bg=STROBE_COLORS[0],
            fg="#ffffff",
            pady=6,
        )
        self.marquee_label.pack(fill="x")

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
        self._build_calculator_section()
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

        # A fixed-size "arena" the entry can be freely repositioned inside
        # with place() - pack()/grid() can't move a widget around like this.
        area_w, area_h = DODGE_AREA_SIZE
        self.username_area = tk.Frame(card, bg=CARD, width=area_w, height=area_h)
        self.username_area.pack(fill="x", pady=(4, 0))
        self.username_area.pack_propagate(False)

        self.username_entry = self._entry(self.username_area, width=24)
        self.username_entry.place(x=10, y=15, height=28)

        # Global motion bind (bind_all, like the scroll-wheel binds above)
        # so we notice the mouse no matter which widget it's actually over.
        self.root.bind_all("<Motion>", self._maybe_dodge_username, add="+")

    def _maybe_dodge_username(self, event):
        try:
            ex = self.username_entry.winfo_rootx()
            ey = self.username_entry.winfo_rooty()
            ew = self.username_entry.winfo_width()
            eh = self.username_entry.winfo_height()
        except tk.TclError:
            return  # widget destroyed or not yet drawn

        # distance from the cursor to the nearest edge of the entry's box
        dx = max(ex - event.x_root, 0, event.x_root - (ex + ew))
        dy = max(ey - event.y_root, 0, event.y_root - (ey + eh))
        distance = (dx * dx + dy * dy) ** 0.5

        if distance < DODGE_THRESHOLD_PX:
            self._dodge_username()

    def _dodge_username(self):
        area_w, area_h = DODGE_AREA_SIZE
        entry_w = self.username_entry.winfo_width() or 150
        entry_h = self.username_entry.winfo_height() or 28

        max_x = max(area_w - entry_w - 5, 5)
        max_y = max(area_h - entry_h - 5, 5)
        new_x = random.randint(5, max_x)
        new_y = random.randint(5, max_y)
        self.username_entry.place(x=new_x, y=new_y)

    # -- section: password ----------------------------------------------
    def _build_password_section(self):
        card = self._card("Choose a password")
        ttk.Label(card, text="PASSWORD", style="Field.TLabel").pack(anchor="w")

        row = ttk.Frame(card)
        row.pack(fill="x", pady=(4, 8))
        self.password_entry = self._entry(row, show="•")
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

    # -- section: calculator (capture / recapture human check) ------------
    def _build_calculator_section(self):
        card = self._card("Verify you're human")
        ttk.Label(
            card,
            text=(
                "Solve the calculation below using the calculator provided. "
                "You get three tries - keep going until it says you're right."
            ),
            foreground=MUTED,
            wraplength=460,
            justify="left",
        ).pack(anchor="w", pady=(0, 10))

        self.calc_problem_label = ttk.Label(card, text="", style="Header.TLabel")
        self.calc_problem_label.pack(anchor="w", pady=(0, 8))

        self.calc_display_var = tk.StringVar()
        display = tk.Entry(
            card,
            textvariable=self.calc_display_var,
            font=FONT_CALC_DISPLAY,
            justify="right",
            state="readonly",
            readonlybackground=ENTRY_BG,
            fg=TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
        )
        display.pack(fill="x", ipady=6, pady=(0, 10))

        keypad = ttk.Frame(card)
        keypad.pack(anchor="w")

        button_layout = [
            ("7", 0, 0), ("8", 0, 1), ("9", 0, 2), ("/", 0, 3),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2), ("*", 1, 3),
            ("1", 2, 0), ("2", 2, 1), ("3", 2, 2), ("-", 2, 3),
            ("C", 3, 0), ("0", 3, 1), ("=", 3, 2), ("+", 3, 3),
        ]
        for label, row, col in button_layout:
            if label == "=":
                command = self._on_calc_equals
                style_name = "Accent.TButton"
            elif label == "C":
                command = self._on_calc_clear
                style_name = "Ghost.TButton"
            else:
                command = lambda char=label: self._on_calc_digit(char)
                style_name = "Calc.TButton"

            ttk.Button(
                keypad, text=label, width=5, style=style_name, command=command,
            ).grid(row=row, column=col, padx=2, pady=2)

        self.calc_feedback = ttk.Label(card, text="", foreground=MUTED, wraplength=460)
        self.calc_feedback.pack(anchor="w", pady=(10, 0))

        self._start_new_calc_attempt()

    def _start_new_calc_attempt(self):
        self.calc_problem = make_calculation()
        a, b, op, _answer = self.calc_problem
        self.calc_problem_label.config(text=f"Solve: {a} {op} {b} = ?")
        self.calc_display_var.set("")
        self.calc_feedback.config(text="", foreground=MUTED)

    def _on_calc_digit(self, char):
        self.calc_display_var.set(self.calc_display_var.get() + char)

    def _on_calc_clear(self):
        self.calc_display_var.set("")

    def _on_calc_equals(self):
        parsed = parse_expression(self.calc_display_var.get())
        if not parsed:
            self.calc_display_var.set("Error")
            return

        num1, op, num2 = parsed
        result = rigged_calculate(num1, op, num2, self.calc_attempt)
        self.calc_display_var.set(str(result))

        if self.calc_attempt < 3:
            self.calc_feedback.config(text="That's wrong, try again.", foreground=ERROR)
            self.calc_attempt += 1
            self.root.after(1200, self._start_new_calc_attempt)
        else:
            _a, _b, _op, correct_answer = self.calc_problem
            self.calc_feedback.config(
                text=f"That's right! (Real answer was {correct_answer})",
                foreground=SUCCESS,
            )
            self.form_state["calculator_ok"] = True
            self._refresh_submit_state()

    def _reset_calculator(self):
        self.calc_attempt = 1
        self.form_state["calculator_ok"] = False
        self._start_new_calc_attempt()

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

        # Its own style so the strobe loop can flash this button alone
        # without touching every other Accent.TButton in the app.
        self.submit_btn = ttk.Button(
            card, text="CREATE ACCOUNT!!!", style="Submit.TButton", command=self._on_submit
        )
        self.submit_btn.pack(anchor="w", ipadx=10, ipady=4)

    def _refresh_submit_state(self):
        # Purely cosmetic now - the button below ignores all of this and
        # redirects unconditionally, but the hint still pretends to care.
        missing = []
        if not self.form_state["password_ok"]:
            missing.append("an accepted password")
        if not self.form_state["calculator_ok"]:
            missing.append("the human verification calculation")
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
        # Stubborn by design: it doesn't matter what has or hasn't been
        # filled in - clicking this button always redirects.
        webbrowser.open(RICKROLL_URL)

    # -- strobe / marquee (cosmetic ugliness) ------------------------------
    def _tick_strobe(self):
        color = STROBE_COLORS[self._strobe_index % len(STROBE_COLORS)]
        self._strobe_index += 1

        self.marquee_label.config(bg=color)
        style = ttk.Style(self.root)
        style.configure("Submit.TButton", background=color, foreground="#ffffff", font=FONT_BTN, borderwidth=0)
        style.map("Submit.TButton", background=[("active", color)])

        self.root.after(400, self._tick_strobe)

    def _tick_marquee(self):
        text = MARQUEE_MESSAGES[self._marquee_index % len(MARQUEE_MESSAGES)]
        self._marquee_index += 1
        self.marquee_label.config(text=text)
        self.root.after(1600, self._tick_marquee)

    # -- rubber duck popup (appears every 15 seconds, unprompted) ---------
    def _load_duck_image(self):
        """
        Load duck.png (resized) for the popup. Falls back to None if the
        file is missing or Pillow isn't installed - _spawn_duck() then
        falls back to a plain emoji instead.
        """
        if not os.path.exists(DUCK_IMAGE_PATH):
            return None
        try:
            if _PIL_AVAILABLE:
                img = Image.open(DUCK_IMAGE_PATH).convert("RGBA")
                img = img.resize(DUCK_IMAGE_SIZE, Image.LANCZOS)
                return ImageTk.PhotoImage(img)
            else:
                # No Pillow: tkinter's own PhotoImage can still show a PNG,
                # just without smooth resizing (only whole-number shrinks).
                return tk.PhotoImage(file=DUCK_IMAGE_PATH).subsample(2, 2)
        except Exception:
            return None

    def _spawn_duck(self):
        duck = tk.Toplevel(self.root)
        duck.overrideredirect(True)  # no title bar/borders - looks like a sticker
        duck.attributes("-topmost", True)
        # Solid yellow, no border line at all (highlightthickness=0).
        duck.configure(bg=DUCK_BG, highlightthickness=0)

        width, height = DUCK_IMAGE_SIZE if self._duck_image is not None else (110, 110)

        # Random spot inside the screen area.
        max_x = max(self.root.winfo_screenwidth() - width, 0)
        max_y = max(self.root.winfo_screenheight() - height, 0)
        x = random.randint(0, max_x)
        y = random.randint(0, max_y)
        duck.geometry(f"{width}x{height}+{x}+{y}")

        if self._duck_image is not None:
            label = tk.Label(duck, image=self._duck_image, bg=DUCK_BG, borderwidth=0, highlightthickness=0)
            label.image = self._duck_image  # keep a reference so it isn't garbage-collected
        else:
            label = tk.Label(duck, text="\U0001F986", font=("Segoe UI Emoji", 48), bg=DUCK_BG)
        label.pack(expand=True, fill="both")

        # Click it to dismiss early; otherwise it disappears on its own.
        duck.bind("<Button-1>", lambda e: duck.destroy())
        label.bind("<Button-1>", lambda e: duck.destroy())
        duck.after(DUCK_LIFETIME_MS, duck.destroy)

    def _tick_duck(self):
        self._spawn_duck()
        self.root.after(DUCK_INTERVAL_MS, self._tick_duck)

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
        self._reset_calculator()
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
