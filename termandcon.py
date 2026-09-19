import tkinter as tk
from tkinter import ttk

TERMS_TEXT = """TERMS AND CONDITIONS

Last Updated: [18/9/2026]
1. Acceptance of Terms
By creating an account, you agree to be bound by these Terms and Conditions.
If you do not agree, please do not proceed with registration.
 
2. Eligibility
You must provide accurate information, including a truthful date and time
of birth, and you confirm that you meet any minimum age requirement that
applies in your jurisdiction.
 
3. Account Security
You are responsible for maintaining the confidentiality of your password
and for all activity that occurs under your account. Notify us immediately
of any unauthorized use.
 
4. Acceptable Use
You agree not to misuse the software, attempt to bypass its security
controls, or use it for any unlawful purpose.
 
5. Data Handling
Information you provide is stored to operate your account. We do not sell
your personal data to third parties.
 
6. Governing Law
These terms are governed by the laws applicable in your place of residence,
without regard to conflict-of-law principles.
 
7. Contact
Questions about these terms can be directed to the software's support
channel.
 
-- End of Terms and Conditions --
"""
READING_WORDS_PER_MINUTE = 200


def create_terms_widget(parent, text=TERMS_TEXT, min_read_seconds=None,
                        title="Terms and Conditions", on_change=None):
    if min_read_seconds is None:
        word_count = len(text.split())
        min_read_seconds = int(word_count / READING_WORDS_PER_MINUTE * 60)
        if min_read_seconds < 8:
            min_read_seconds = 8

    frame = ttk.LabelFrame(parent, text=title)

    text_frame = ttk.Frame(frame)
    text_frame.pack(fill="both", expand=True, padx=8, pady=8)

    scrollbar = ttk.Scrollbar(text_frame, orient="vertical")
    scrollbar.pack(side="right", fill="y")

    terms_text_widget = tk.Text(
        text_frame, wrap="word", height=10, width=60,
        yscrollcommand=scrollbar.set
    )
    terms_text_widget.insert("1.0", text)
    terms_text_widget.config(state="disabled")  # read-only, but still scrollable
    terms_text_widget.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=terms_text_widget.yview)

    progress_label = ttk.Label(
        frame, text=f"Please read the full document (~{min_read_seconds}s)."
    )
    progress_label.pack(anchor="w", padx=8)

    timer_label = ttk.Label(frame, text="")
    timer_label.pack(anchor="w", padx=8, pady=(2, 0))

    agree_var = tk.BooleanVar(value=False)

    # Small mutable dict standing in for what would otherwise be instance
    # state on a class.
    read_state = {
        "scrolled_to_bottom": False,
        "min_time_elapsed": False,
        "seconds_remaining": min_read_seconds,
    }

    def notify_change():
        if on_change:
            on_change()

    agree_check = ttk.Checkbutton(
        frame, text="I have read and agree to the Terms and Conditions",
        variable=agree_var, state="disabled", command=notify_change
    )
    agree_check.pack(anchor="w", padx=8, pady=(4, 8))

    def try_unlock_checkbox():
        if read_state["scrolled_to_bottom"] and read_state["min_time_elapsed"]:
            agree_check.config(state="normal")
            progress_label.config(text="Thanks for reading. You may now tick the box.")
            timer_label.config(text="")
            return

        missing = []
        if not read_state["scrolled_to_bottom"]:
            missing.append("scroll to the end")
        if not read_state["min_time_elapsed"]:
            missing.append("finish the minimum reading time")
        progress_label.config(text="Please " + " and ".join(missing) + ".")

    def check_scroll_position():
        top, bottom = terms_text_widget.yview()
        if bottom >= 0.999:
            read_state["scrolled_to_bottom"] = True
            try_unlock_checkbox()

    def on_scroll_event(event=None):
        frame.after(50, check_scroll_position)

    def on_key_scroll(event):
        # Block jumping straight to the bottom; allow normal scroll-through keys.
        if event.keysym == "End":
            return "break"
        frame.after(50, check_scroll_position)

    terms_text_widget.bind("<MouseWheel>", on_scroll_event)  # Windows/Mac
    terms_text_widget.bind("<Button-4>", on_scroll_event)  # Linux up
    terms_text_widget.bind("<Button-5>", on_scroll_event)  # Linux down
    scrollbar.bind("<B1-Motion>", on_scroll_event)
    scrollbar.bind("<ButtonRelease-1>", on_scroll_event)
    terms_text_widget.bind("<Key>", on_key_scroll)

    def mark_time_elapsed():
        read_state["min_time_elapsed"] = True
        try_unlock_checkbox()

    def tick_countdown():
        remaining = read_state["seconds_remaining"]

        if remaining <= 0:
            timer_label.config(text="")
            mark_time_elapsed()
            return

        timer_label.config(text=f"Time remaining before you can tick the box: {remaining}s")
        read_state["seconds_remaining"] = remaining - 1
        frame.after(1000, tick_countdown)

    tick_countdown()

    def is_valid():
        return agree_var.get()

    def get_value():
        return agree_var.get()

    def reset():
        read_state["scrolled_to_bottom"] = False
        read_state["min_time_elapsed"] = False
        read_state["seconds_remaining"] = min_read_seconds
        agree_var.set(False)
        agree_check.config(state="disabled")
        terms_text_widget.yview_moveto(0)
        progress_label.config(text=f"Please read the full document (~{min_read_seconds}s).")
        tick_countdown()

    return {
        "frame": frame,
        "is_valid": is_valid,
        "get_value": get_value,
        "reset": reset,
    }


# Quick standalone test: `python terms_widget.py`
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Terms Widget Test")
    root.geometry("500x420")


    def on_change():
        print("Agreed:", widget["is_valid"]())


    widget = create_terms_widget(root, on_change=on_change)
    widget["frame"].pack(fill="both", expand=True, padx=15, pady=15)
    root.mainloop()
