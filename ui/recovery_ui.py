import customtkinter as ctk

class RecoveryView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.card = ctk.CTkFrame(self, width=380, height=480, corner_radius=15, fg_color="#2B2B2B")
        self.card.pack(expand=True, pady=20)
        self.card.pack_propagate(False)

        ctk.CTkLabel(self.card, text="Account Recovery", font=("Poppins", 22, "bold"), text_color="#FFFFFF").pack(pady=(25, 5))

        self.status_label = ctk.CTkLabel(self.card, text="", font=("Poppins", 11), text_color="red", wraplength=320)
        self.status_label.pack(pady=(0, 5))

        # Step 1: Username Search
        self.entry_username = ctk.CTkEntry(self.card, placeholder_text="Enter your Username", width=300, height=38)
        self.entry_username.pack(pady=6)

        self.btn_search = ctk.CTkButton(
            self.card, text="Find Account", width=300, height=36, fg_color="#3A3A3A", hover_color="#505050",
            command=self.handle_fetch_question
        )
        self.btn_search.pack(pady=4)

        # Step 2: Question Display & Verification Fields (Hidden until found)
        self.question_display = ctk.CTkLabel(
            self.card, text="[ Security Question Will Appear Here ]", font=("Poppins", 11, "italic"),
            text_color="#AAAAAA", wraplength=300
        )
        self.question_display.pack(pady=(12, 6))

        self.entry_answer = ctk.CTkEntry(self.card, placeholder_text="Security Answer", width=300, height=38)
        self.entry_answer.pack(pady=6)

        self.entry_new_password = ctk.CTkEntry(self.card, placeholder_text="New Password", width=300, height=38, show="*")
        self.entry_new_password.pack(pady=6)

        # Final Action Button
        self.btn_reset = ctk.CTkButton(
            self.card, text="Reset Password", width=300, height=40, font=("Poppins", 14, "bold"),
            fg_color="#000080", hover_color="#000055", command=self.handle_reset_password
        )
        self.btn_reset.pack(pady=(15, 10))

        # Return Link
        back_link = ctk.CTkLabel(self.card, text="Back to Log In", font=("Poppins", 12, "underline"), cursor="hand2")
        back_link.bind("<Button-1>", lambda e: self.controller.show_frame("LoginView"))
        back_link.pack(pady=4)

    def handle_fetch_question(self):
        username = self.entry_username.get()
        success, result = self.controller.auth_manager.get_security_question(username)

        if success:
            self.question_display.configure(text=f"Question: {result}", text_color="#00E676")
            self.status_label.configure(text="Account found! Answer question to proceed.", text_color="#00E676")
        else:
            self.question_display.configure(text="[ Security Question Will Appear Here ]", text_color="#AAAAAA")
            self.status_label.configure(text=result, text_color="red")

    def handle_reset_password(self):
        username = self.entry_username.get()
        answer = self.entry_answer.get()
        new_pwd = self.entry_new_password.get()

        success, message = self.controller.auth_manager.reset_password(username, answer, new_pwd)
        if success:
            self.status_label.configure(text=message, text_color="green")
            self.after(1500, lambda: self.controller.show_frame("LoginView"))
        else:
            self.status_label.configure(text=message, text_color="red")

    def on_show(self):
        self.status_label.configure(text="")
        self.question_display.configure(text="[ Security Question Will Appear Here ]", text_color="#AAAAAA")
        self.entry_username.delete(0, "end")
        self.entry_answer.delete(0, "end")
        self.entry_new_password.delete(0, "end")