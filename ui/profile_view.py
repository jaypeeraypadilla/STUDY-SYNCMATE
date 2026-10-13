import customtkinter as ctk
from tkinter import messagebox
from logic.user_prof import ProfileManager


class ProfileViewFrame(ctk.CTkFrame):
    """Embedded User Profile workspace for viewing and updating student details and security."""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.profile_logic = ProfileManager()
        self.is_editing = False  # Tracks whether fields are unlocked for editing

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # =============================================================
        # LEFT PANEL: PERSONAL INFORMATION
        # =============================================================
        self.info_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1E1E2E")
        self.info_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(
            self.info_frame, 
            text="👤 Personal Information", 
            font=("Poppins", 16, "bold"), 
            text_color="#FFFFFF"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        # Username (Read-Only)
        ctk.CTkLabel(self.info_frame, text="Username:", font=("Poppins", 11), text_color="#AAAAAA").pack(anchor="w", padx=20, pady=(2, 0))
        self.entry_username = ctk.CTkEntry(self.info_frame, height=32, state="disabled")
        self.entry_username.pack(fill="x", padx=20, pady=(0, 8))

        # Full Name
        ctk.CTkLabel(self.info_frame, text="Full Name:", font=("Poppins", 11)).pack(anchor="w", padx=20, pady=(2, 0))
        self.entry_name = ctk.CTkEntry(self.info_frame, height=32, state="disabled")
        self.entry_name.pack(fill="x", padx=20, pady=(0, 8))

        # Age & Gender Row
        self.row_age_gender = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        self.row_age_gender.pack(fill="x", padx=20, pady=(0, 8))
        self.row_age_gender.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(self.row_age_gender, text="Age:", font=("Poppins", 11)).grid(row=0, column=0, sticky="w")
        self.entry_age = ctk.CTkEntry(self.row_age_gender, height=32, width=80, state="disabled")
        self.entry_age.grid(row=1, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkLabel(self.row_age_gender, text="Gender:", font=("Poppins", 11)).grid(row=0, column=1, sticky="w", padx=(5, 0))
        self.combo_gender = ctk.CTkOptionMenu(
            self.row_age_gender, 
            values=["Male", "Female", "Prefer not to say"], 
            height=32,
            fg_color="#2B2B3D", 
            button_color="#3B82F6",
            state="disabled"
        )
        self.combo_gender.grid(row=1, column=1, sticky="ew", padx=(5, 0))

        # Course & Year Level Row
        self.row_academic = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        self.row_academic.pack(fill="x", padx=20, pady=(0, 10))
        self.row_academic.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(self.row_academic, text="Course / Program:", font=("Poppins", 11)).grid(row=0, column=0, sticky="w")
        self.entry_course = ctk.CTkEntry(self.row_academic, height=32, state="disabled")
        self.entry_course.grid(row=1, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkLabel(self.row_academic, text="Year Level:", font=("Poppins", 11)).grid(row=0, column=1, sticky="w", padx=(5, 0))
        self.combo_year = ctk.CTkOptionMenu(
            self.row_academic, 
            values=["1st Year", "2nd Year", "3rd Year", "4th Year", "5th Year"], 
            height=32,
            fg_color="#2B2B3D", 
            button_color="#3B82F6",
            state="disabled"
        )
        self.combo_year.grid(row=1, column=1, sticky="ew", padx=(5, 0))

        # Edit / Save Changes Toggle Button
        self.btn_edit_save = ctk.CTkButton(
            self.info_frame,
            text="✏️ Edit Changes",
            font=("Poppins", 12, "bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            height=38,
            command=self.toggle_edit_mode
        )
        self.btn_edit_save.pack(fill="x", padx=20, pady=(10, 15))

        # =============================================================
        # RIGHT PANEL: SECURITY & PASSWORD CHANGE
        # =============================================================
        self.security_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1E1E2E")
        self.security_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(
            self.security_frame, 
            text="🔒 Security & Password", 
            font=("Poppins", 16, "bold"), 
            text_color="#FFFFFF"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        # Security Question Display
        ctk.CTkLabel(self.security_frame, text="Security Question:", font=("Poppins", 11), text_color="#AAAAAA").pack(anchor="w", padx=20, pady=(2, 0))
        self.lbl_sec_question = ctk.CTkLabel(
            self.security_frame, text="Not loaded", font=("Poppins", 11, "italic"), text_color="#3B82F6", anchor="w"
        )
        self.lbl_sec_question.pack(fill="x", padx=20, pady=(0, 15))

        # Current Password
        ctk.CTkLabel(self.security_frame, text="Current Password:", font=("Poppins", 11)).pack(anchor="w", padx=20, pady=(2, 0))
        self.entry_curr_pass = ctk.CTkEntry(self.security_frame, show="•", height=32)
        self.entry_curr_pass.pack(fill="x", padx=20, pady=(0, 10))

        # New Password
        ctk.CTkLabel(self.security_frame, text="New Password:", font=("Poppins", 11)).pack(anchor="w", padx=20, pady=(2, 0))
        self.entry_new_pass = ctk.CTkEntry(self.security_frame, show="•", height=32)
        self.entry_new_pass.pack(fill="x", padx=20, pady=(0, 15))

        # Change Password Button
        self.btn_change_pass = ctk.CTkButton(
            self.security_frame,
            text="🔑 Update Password",
            font=("Poppins", 12, "bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            height=38,
            command=self.save_password
        )
        self.btn_change_pass.pack(fill="x", padx=20, pady=(10, 15))

    # =============================================================
    # EVENT HANDLERS & LIFECYCLE
    # =============================================================

    def _get_user_id(self) -> int | None:
        if hasattr(self.controller, "current_user") and self.controller.current_user:
            return self.controller.current_user.get("id")
        return None

    def toggle_edit_mode(self):
        """Toggles between locked view mode and editable save mode."""
        if not self.is_editing:
            # Switch to editing state
            self.is_editing = True
            self.entry_name.configure(state="normal")
            self.entry_age.configure(state="normal")
            self.combo_gender.configure(state="normal")
            self.entry_course.configure(state="normal")
            self.combo_year.configure(state="normal")

            self.btn_edit_save.configure(text="💾 Save Changes", fg_color="#10B981", hover_color="#059669")
        else:
            # Save updates and lock fields back
            user_id = self._get_user_id()
            if not user_id:
                messagebox.showerror("Session Error", "No active user session found.")
                return

            success, message, updated_data = self.profile_logic.update_profile(
                user_id=user_id,
                full_name=self.entry_name.get(),
                age=self.entry_age.get(),
                gender=self.combo_gender.get(),
                course=self.entry_course.get(),
                year_level=self.combo_year.get()
            )

            if success:
                messagebox.showinfo("Success", message)
                if hasattr(self.controller, "current_user") and self.controller.current_user:
                    self.controller.current_user.update(updated_data)
                    
                if hasattr(self.controller, "frames") and "DashboardView" in self.controller.frames:
                    self.controller.frames["DashboardView"].on_show()

                # Lock fields back
                self.is_editing = False
                self.entry_name.configure(state="disabled")
                self.entry_age.configure(state="disabled")
                self.combo_gender.configure(state="disabled")
                self.entry_course.configure(state="disabled")
                self.combo_year.configure(state="disabled")

                self.btn_edit_save.configure(text="✏️ Edit Changes", fg_color="#3B82F6", hover_color="#2563EB")
            else:
                messagebox.showerror("Error", message)

    def load_profile_data(self):
        """Fetches current user profile from database and populates UI fields."""
        user_id = self._get_user_id()
        if not user_id:
            return

        profile = self.profile_logic.get_user_profile(user_id)
        if profile:
            self.entry_username.configure(state="normal")
            self.entry_username.delete(0, "end")
            self.entry_username.insert(0, profile.get("username", ""))
            self.entry_username.configure(state="disabled")

            self.entry_name.configure(state="normal")
            self.entry_name.delete(0, "end")
            self.entry_name.insert(0, profile.get("full_name", ""))
            self.entry_name.configure(state="disabled" if not self.is_editing else "normal")

            self.entry_age.configure(state="normal")
            self.entry_age.delete(0, "end")
            self.entry_age.insert(0, str(profile.get("age", "")))
            self.entry_age.configure(state="disabled" if not self.is_editing else "normal")

            gender = profile.get("gender", "Male")
            self.combo_gender.set(gender if gender in ["Male", "Female", "Prefer not to say"] else "Male")

            self.entry_course.configure(state="normal")
            self.entry_course.delete(0, "end")
            self.entry_course.insert(0, profile.get("course", ""))
            self.entry_course.configure(state="disabled" if not self.is_editing else "normal")

            year = profile.get("year_level", "1st Year")
            self.combo_year.set(year)

            self.lbl_sec_question.configure(text=profile.get("security_question", "None set"))

    def save_password(self):
        """Updates user password."""
        user_id = self._get_user_id()
        if not user_id:
            messagebox.showerror("Session Error", "No active user session found.")
            return

        curr_pass = self.entry_curr_pass.get()
        new_pass = self.entry_new_pass.get()

        success, message = self.profile_logic.change_password(user_id, curr_pass, new_pass)
        if success:
            messagebox.showinfo("Success", message)
            self.entry_curr_pass.delete(0, "end")
            self.entry_new_pass.delete(0, "end")
        else:
            messagebox.showerror("Error", message)

    def on_show(self):
        """Triggered automatically when profile view is raised."""
        self.is_editing = False
        self.btn_edit_save.configure(text="✏️ Edit Changes", fg_color="#3B82F6", hover_color="#2563EB")
        self.load_profile_data()
        
        # Ensure fields start disabled whenever view is opened
        self.entry_name.configure(state="disabled")
        self.entry_age.configure(state="disabled")
        self.combo_gender.configure(state="disabled")
        self.entry_course.configure(state="disabled")
        self.combo_year.configure(state="disabled")