import tkinter as tk

root = tk.Tk()
root.title("Stubborn Signup")

# ---------------- PASSWORD ----------------

password = tk.Entry(root, show="*")
password.pack()

password_label = tk.Label(root, text="Enter your password:")
password_label.pack()


def check_password():
    password_text = password.get()

    if len(password_text) < 8:
        password_label.config(text="Password must be at least 8 characters.")

    elif len(password_text) < 12:
        password_label.config(text="Actually... make it 12 characters.")

    elif "password" in password_text.lower():
        password_label.config(text="Nice try. You can't use 'password'.")

    elif "123" in password_text:
        password_label.config(text="Too predictable. No 123...")

    elif password_text.islower():
        password_label.config(text="You need a capital letter.")

    elif password_text.isupper():
        password_label.config(text="You need a lowercase letter.")

    elif not any(char.isdigit() for char in password_text):
        password_label.config(text="You need a number.")

    elif not any(not char.isalnum() for char in password_text):
        password_label.config(text="You need a special character.")

    elif "banana" not in password_text.lower():
        password_label.config(text="Your password must contain 'banana'.")

    elif "banana" in password_text.lower():
        password_label.config(text="Actually, we don't allow bananas.")

    elif "42" not in password_text:
        password_label.config(text="Your password must contain the answer to everything.")

    elif len(password_text) < 20:
        password_label.config(text="20 characters minimum. We changed our minds.")

    elif len(password_text) > 25:
        password_label.config(text="That's too long. Please calm down.")

    elif "!" not in password_text:
        password_label.config(text="Where is the enthusiasm?  !   ")

    elif password_text.count("!") < 3:
        password_label.config(text="One ! is not enough. We need THREE.")

    elif "?" in password_text:
        password_label.config(text="Don't question our password policy.")

    elif " " in password_text:
        password_label.config(text="Passwords cannot contain spaces. Obviously.")

    elif password_text[0].isdigit():
        password_label.config(text="Your password cannot start with a number.")

    elif password_text[-1].isdigit():
        password_label.config(text="Your password cannot end with a number.")

    elif "admin" in password_text.lower():
        password_label.config(text="You are not allowed to be admin.")

    elif "hello" in password_text.lower():
        password_label.config(text="Don't say hello to us.")

    elif password_text.lower() == password_text.lower()[::-1]:
        password_label.config(text="Palindrome passwords are forbidden.")

    elif len(set(password_text)) < 5:
        password_label.config(text="Your password lacks personality.")
    elif len(password_text) == 13:
        password_label.config(text="Your password is too confident.")

    elif "terms" in password_text.lower():
        password_label.config(text="This password has violated our terms and conditions.")

    elif password_text.count("a") > 3:
        password_label.config(text="We don't like that password.")

    elif password_text.lower().startswith("v"):
        password_label.config(text="Password rejected. Reason: vibes.")

    elif password_text.count("e") == 0:
        password_label.config(text="Please choose a password that makes us happier.")

    elif password_text.lower().startswith("pass"):
        password_label.config(text="This password is suspiciously password-like.")

    elif password_text.count("!") > 5:
        password_label.config(text="Our lawyers don't like this password.")

    elif password_text.endswith("."):
        password_label.config(text="Password accepted. Just kidding.")

    elif len(password_text) == 47:
        password_label.config(text="Password almost accepted. Please wait 47 business days.")

    elif password_text.lower() == "nobody":
        password_label.config(text="This password is already being used by someone who doesn't exist.")

    elif password_text.count("p") >= 3:
        password_label.config(text="Your password has been sent to our password department.")

    elif len(set(password_text)) == 1:
        password_label.config(text="Password rejected due to insufficient passwordness.")

    else:
        password_label.config(text="Password accepted! ...probably.")


check_button = tk.Button(
    root,
    text="Check Password",
    command=check_password
)
check_button.pack()

root.mainloop()
