import tkinter as tk
from tkinter import ttk


class ScrollableFrame(tk.Frame):

    def __init__(self, parent, width=400, height=520, bg="#2B2B2B"):
        super().__init__(parent, bg=bg)

        self.canvas = tk.Canvas(
            self, width=width, height=height, bg=bg, highlightthickness=0
        )
        self.scrollbar = tk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.scrollable_content = tk.Frame(self.canvas, bg=bg)

        self.scrollable_content.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scrollable_content, anchor="nw"
        )

        # Keep inner frame width aligned with canvas width
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width),
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bind mousewheel scrolling
        self.canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(
                int(-1 * (e.delta / 120)), "units"
            ),
        )


class SignUpView(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Scrollable Card Frame
        self.card = ScrollableFrame(self, width=400, height=520, bg="#2B2B2B")
        self.card.pack(expand=True, pady=20)
        card_body = self.card.scrollable_content

        # Back to Login Button (Placed at the top)
        self.btn_back = tk.Button(
            card_body,
            text="← Back to Login",
            font=("Poppins", 10, "bold"),
            bg="#2B2B2B",
            fg="#3B82F6",
            activebackground="#2B2B2B",
            activeforeground="#2563EB",
            cursor="hand2",
            relief="flat",
            command=lambda: self.controller.show_frame("LoginView"),
        )
        self.btn_back.pack(anchor="w", padx=15, pady=(15, 0))

        # Header
        tk.Label(
            card_body,
            text="Create Account",
            font=("Poppins", 22, "bold"),
            bg="#2B2B2B",
            fg="#FFFFFF",
        ).pack(pady=(5, 5))

        # Status Label
        self.status_label = tk.Label(
            card_body, text="", font=("Poppins", 11), bg="#2B2B2B", fg="red"
        )
        self.status_label.pack(pady=(0, 10))

        # Profile Inputs
        self.entry_name = self._create_entry(card_body, "Full Name")
        self.entry_age = self._create_entry(card_body, "Age")

        self.combo_gender = ttk.Combobox(
            card_body,
            values=[
                "Select Gender",
                "Male",
                "Female",
                "Non-binary",
                "Prefer not to say",
            ],
            state="readonly",
            width=32,
            font=("Poppins", 10),
        )
        self.combo_gender.set("Select Gender")
        self.combo_gender.pack(pady=6, ipady=4)

        self.entry_course = self._create_entry(card_body, "Course (e.g., BSIT)")

        self.combo_year = ttk.Combobox(
            card_body,
            values=[
                "Select Year Level",
                "1st Year",
                "2nd Year",
                "3rd Year",
                "4th Year",
                "5th Year",
            ],
            state="readonly",
            width=32,
            font=("Poppins", 10),
        )
        self.combo_year.set("Select Year Level")
        self.combo_year.pack(pady=6, ipady=4)

        # Security Verification
        tk.Label(
            card_body,
            text="Security Recovery",
            font=("Poppins", 12, "bold"),
            bg="#2B2B2B",
            fg="#AAAAAA",
        ).pack(pady=(12, 2))

        self.combo_question = ttk.Combobox(
            card_body,
            values=[
                "Select Security Question",
                "What was your first pet's name?",
                "What is your mother's maiden name?",
                "What elementary school did you attend?",
                "What is your favorite book?",
            ],
            state="readonly",
            width=32,
            font=("Poppins", 10),
        )
        self.combo_question.set("Select Security Question")
        self.combo_question.pack(pady=6, ipady=4)

        self.entry_sec_answer = self._create_entry(card_body, "Security Answer")

        # Account Credentials
        tk.Label(
            card_body,
            text="Account Credentials",
            font=("Poppins", 12, "bold"),
            bg="#2B2B2B",
            fg="#AAAAAA",
        ).pack(pady=(12, 2))

        self.entry_username = self._create_entry(card_body, "Create Username")
        self.entry_password = self._create_entry(
            card_body, "Create Password", is_password=True
        )

        # Buttons
        tk.Button(
            card_body,
            text="Register Account",
            font=("Poppins", 14, "bold"),
            bg="#000080",
            fg="#FFFFFF",
            activebackground="#000055",
            activeforeground="#FFFFFF",
            cursor="hand2",
            relief="flat",
            width=26,
            command=self.handle_signup,
        ).pack(pady=(18, 10), ipady=4)

        login_link = tk.Label(
            card_body,
            text="Already have an account? Log In",
            font=("Poppins", 12, "underline"),
            bg="#2B2B2B",
            fg="#FFFFFF",
            cursor="hand2",
        )
        login_link.bind(
            "<Button-1>", lambda e: self.controller.show_frame("LoginView")
        )
        login_link.pack(pady=(0, 15))

    def _create_entry(self, parent, placeholder, is_password=False):
        """Helper to instantiate dark-styled Tkinter entries with placeholder support."""
        entry = tk.Entry(
            parent,
            font=("Poppins", 10),
            bg="#3A3A3A",
            fg="#FFFFFF",
            insertbackground="#FFFFFF",
            relief="flat",
            width=32,
        )
        entry.pack(pady=6, ipady=6)
        self._add_placeholder(entry, placeholder, is_password)
        return entry

    def _add_placeholder(self, entry, placeholder, is_password=False):
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

    def handle_signup(self):
        gender = (
            self.combo_gender.get()
            if self.combo_gender.get() != "Select Gender"
            else ""
        )
        year_level = (
            self.combo_year.get()
            if self.combo_year.get() != "Select Year Level"
            else ""
        )
        question = (
            self.combo_question.get()
            if self.combo_question.get() != "Select Security Question"
            else ""
        )

        success, message = self.controller.auth_manager.register_user(
            name=self._get_entry_value(self.entry_name),
            age=self._get_entry_value(self.entry_age),
            gender=gender,
            course=self._get_entry_value(self.entry_course),
            year_level=year_level,
            sec_question=question,
            sec_answer=self._get_entry_value(self.entry_sec_answer),
            username=self._get_entry_value(self.entry_username),
            password=self._get_entry_value(self.entry_password),
        )

        if success:
            self.status_label.configure(text=message, fg="green")
            self.after(1200, lambda: self.controller.show_frame("LoginView"))
        else:
            self.status_label.configure(text=message, fg="red")