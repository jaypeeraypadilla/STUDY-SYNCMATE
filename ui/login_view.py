import os
import tkinter as tk
from PIL import Image, ImageTk


class LoginView(tk.Frame):

  def __init__(self, parent, controller):
    super().__init__(parent)
    self.controller = controller

    try:
      # Get the directory where this script is located
      current_dir = os.path.dirname(os.path.abspath(__file__))
      # Build the full path: script_dir/assets/your_background.jpg
      image_path = os.path.join(current_dir, "assets", "login_bg.jpeg")

      self.original_image = Image.open(image_path)
      self.bg_image = ImageTk.PhotoImage(self.original_image)

      # Create a label for the background and make it fill the entire frame
      self.bg_label = tk.Label(self, image=self.bg_image)
      self.bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
      
    except Exception as e:
      print(f"Error loading background image from assets: {e}")
      self.configure(bg="#1E1E1E")  # Fallback color

    # 2. Card Container (Created AFTER bg_label so it sits on top)
    self.card = tk.Frame(self, width=380, height=480, bg="#2B2B2B")
    self.card.pack(expand=True, pady=20)
    self.card.pack_propagate(False)

    # Header
    tk.Label(
        self.card,
        text="Log-In",
        font=("Poppins", 22, "bold"),
        bg="#2B2B2B",
        fg="#FFFFFF",
    ).pack(pady=(30, 5))

    # Status Message
    self.status_label = tk.Label(
        self.card, text="", font=("Poppins", 11), bg="#2B2B2B", fg="red"
    )
    self.status_label.pack(pady=(0, 10))

    # Inputs
    self.entry_username = tk.Entry(
        self.card,
        font=("Poppins", 11),
        bg="#3A3A3A",
        fg="#FFFFFF",
        insertbackground="#FFFFFF",
        relief="flat",
        width=30,
    )
    self.entry_username.pack(pady=8, ipady=8)
    self._add_placeholder(self.entry_username, "Username")

    self.entry_password = tk.Entry(
        self.card,
        font=("Poppins", 11),
        bg="#3A3A3A",
        fg="#FFFFFF",
        insertbackground="#FFFFFF",
        relief="flat",
        width=30,
    )
    self.entry_password.pack(pady=8, ipady=8)
    self._add_placeholder(self.entry_password, "Password", is_password=True)

    # Actions
    tk.Button(
        self.card,
        text="Log In",
        font=("Poppins", 14, "bold"),
        bg="#000080",
        fg="#FFFFFF",
        activebackground="#000055",
        activeforeground="#FFFFFF",
        cursor="hand2",
        relief="flat",
        width=26,
        command=self.handle_login,
    ).pack(pady=(20, 10), ipady=4)

    # Navigation Links
    signup_link = tk.Label(
        self.card,
        text="Don't have an account? Sign Up",
        font=("Poppins", 12, "underline"),
        bg="#2B2B2B",
        fg="#FFFFFF",
        cursor="hand2",
    )
    signup_link.bind(
        "<Button-1>", lambda e: self.controller.show_frame("SignUpView")
    )
    signup_link.pack(pady=4)

    forgot_link = tk.Label(
        self.card,
        text="Forgot Password?",
        font=("Poppins", 12, "underline"),
        bg="#2B2B2B",
        fg="#FFFFFF",
        cursor="hand2",
    )
    forgot_link.bind(
        "<Button-1>", lambda e: self.controller.show_frame("RecoveryView")
    )
    forgot_link.pack(pady=4)

  def _add_placeholder(self, entry, placeholder, is_password=False):
    """Replicates CTk placeholder_text in standard Tkinter using focus events."""
    entry.placeholder = placeholder
    entry.is_password = is_password

    def on_focus_in(e):
      if entry.get() == entry.placeholder:
        entry.delete(0, "end")
        entry.config(fg="#FFFFFF")
        if entry.is_password:
          entry.config(show="*")

    def on_focus_out(e):
      if not entry.get():
        entry.insert(0, entry.placeholder)
        entry.config(fg="#888888")
        if entry.is_password:
          entry.config(show="")

    # Initial state
    entry.insert(0, placeholder)
    entry.config(fg="#888888")
    if is_password:
      entry.config(show="")

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

  def _get_entry_value(self, entry):
    """Returns empty string if entry still contains placeholder text."""
    val = entry.get()
    return "" if val == getattr(entry, "placeholder", "") else val

  def handle_login(self):
    username = self._get_entry_value(self.entry_username)
    password = self._get_entry_value(self.entry_password)

    success, message, user_data = self.controller.auth_manager.login_user(
        username, password
    )
    if success:
      self.status_label.configure(text="", fg="green")
      self.controller.set_active_user(user_data)
    else:
      self.status_label.configure(text=message, fg="red")

  def on_show(self):
    self.status_label.configure(text="")
    self.entry_password.delete(0, "end")
    if hasattr(self.entry_password, "placeholder"):
      self.entry_password.insert(0, self.entry_password.placeholder)
      self.entry_password.config(fg="#888888", show="")