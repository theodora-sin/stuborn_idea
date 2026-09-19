import tkinter as tk

root = tk.Tk()
root.title("Stubborn Signup")

username = tk.Entry(root)
username.pack()

password = tk.Entry(root)
password.pack()


time_left = 33

timer_label = tk.Label(root, text="Time remaining: 33 seconds")
timer_label.pack()


def clear_form():
    username.delete(0, tk.END)
    password.delete(0, tk.END)


def countdown():
    global time_left

    time_left -= 1

    timer_label.config(
        text=f"Time remaining: {time_left} seconds"
    )

    if time_left <= 0:
        timer_label.config(text="TIME'S UP!")
        clear_form()
    else:
        root.after(1000, countdown)


countdown()

root.mainloop()
