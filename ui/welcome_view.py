import os
import customtkinter as ctk
from PIL import Image


class WelcomeView(ctk.CTkFrame):
    """Welcome / Splash screen displayed before the login screen with a smooth slide-up animation."""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#1E1E1E")
        self.controller = controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Centered Welcome Card using place() for smooth coordinate animation
        self.center_card = ctk.CTkFrame(self, fg_color="#2B2B3D", corner_radius=16, width=460, height=380)
        self.center_card.place(relx=0.5, rely=0.58, anchor="center")  # Start slightly lower
        self.center_card.grid_propagate(False)

        # App Icon / Emoji
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(base_dir, "logo_dark.jpeg")

        try:
            pil_image = Image.open(logo_path)
            self.logo_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(100, 100))
            
            # App Logo Label
            self.logo_label = ctk.CTkLabel(self.center_card, image=self.logo_image, text="")
            self.logo_label.pack(pady=(25, 10))
        except Exception as e:
            print(f"Failed to load logo image: {e}")
            # Fallback to emoji if image fails to load
            self.logo_label = ctk.CTkLabel(self.center_card, text="🎓📚", font=("Poppins", 50))
            self.logo_label.pack(pady=(25, 10))

        # Title
        ctk.CTkLabel(
            self.center_card, 
            text="Study SyncMate", 
            font=("Poppins", 24, "bold"), 
            text_color="#FFFFFF"
        ).pack(pady=(0, 5))

        # Subtitle Description
        ctk.CTkLabel(
            self.center_card, 
            text="Your centralized, modular academic desktop companion designed to keep your notes, quizzes, and schedules synchronized.", 
            font=("Poppins", 13), 
            text_color="#AAAAAA",
            justify="center",
            wraplength=380
        ).pack(pady=(0, 30), padx=20)

        # Get Started Button (Transitions to LoginView)
        btn_start = ctk.CTkButton(
            self.center_card,
            text="Get Started ➔",
            font=("Poppins", 16, "bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            width=200,
            height=42,
            command=lambda: controller.show_frame("LoginView")
        )
        btn_start.pack(pady=10)

        # Animation tracking variables
        self.anim_rely = 0.58
        self.target_rely = 0.50

    def on_show(self):
        """Triggered automatically when view is raised; replays the smooth slide-in effect."""
        self.anim_rely = 0.58
        self.center_card.place(relx=0.5, rely=self.anim_rely, anchor="center")
        self._run_slide_animation()

    def _run_slide_animation(self):
        """Smooth incremental animation loop using self.after()."""
        if self.anim_rely > self.target_rely:
            self.anim_rely -= 0.006  # Step size for smooth gliding speed
            if self.anim_rely < self.target_rely:
                self.anim_rely = self.target_rely
            
            self.center_card.place(relx=0.5, rely=self.anim_rely, anchor="center")
            self.after(10, self._run_slide_animation)