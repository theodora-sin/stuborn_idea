import webbrowser
import tkinter as tk
root = tk.Tk()
root.title("Stubborn Signup")

def rickroll():
    webbrowser.open(
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    )

create_account_button = tk.Button(
        root,
        text="Create Account",
        command=rickroll
)

create_account_button.pack()
root.mainloop()
