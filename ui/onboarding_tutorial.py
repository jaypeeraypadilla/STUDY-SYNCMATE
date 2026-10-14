import customtkinter as ctk


class OnboardingTutorial(ctk.CTkToplevel):
    """Floating step-by-step tutorial modal that highlights and points to app features."""

    def __init__(self, parent, controller, target_widgets=None, on_finish_callback=None):
        super().__init__(parent)
        self.controller = controller
        self.parent_app = parent
        self.target_widgets = target_widgets or {}
        self.on_finish_callback = on_finish_callback

        self.title("Study SyncMate Guide 🎓")
        self.geometry("380x220")
        self.resizable(False, False)
        self.overrideredirect(True)  # Removes standard OS window borders for a floating tooltip look
        self.transient(parent)
        self.grab_set()

        # Tutorial Steps Data with optional target widget keys
        self.steps = [
            {
                "icon": "🚀",
                "title": "Welcome to Study SyncMate!",
                "desc": "Your centralized, modular academic desktop app designed to keep notes, quizzes, and schedules synchronized.",
                "target": None  # Centers on screen
            },
            {
                "icon": "📓",
                "title": "My Notes Workspace",
                "desc": "Create notes by subject, format text with bold/headers, and upload media attachments here.",
                "target": "notes"
            },
            {
                "icon": "🧠",
                "title": "Quizzes & Flashcards",
                "desc": "Turn your saved notes into interactive multiple choice, identification, and enumeration practice tests instantly.",
                "target": "quizzes"
            },
            {
                "icon": "📅",
                "title": "Schedule & Task Planner",
                "desc": "Organize academic deadlines, set task priorities, and track active study goals using the calendar.",
                "target": "schedule"
            },
            {
                "icon": "📊",
                "title": "Progress & Settings",
                "desc": "Monitor study hours, view past quiz performance scores, and customize your app preferences.",
                "target": "progress"
            }
        ]
        
        self.current_step = 0

        # Floating Card Container with Accent Border Effect
        self.card_frame = ctk.CTkFrame(
            self, 
            fg_color=("#FFFFFF", "#1E1E2E"), 
            border_color="#3B82F6", 
            border_width=2, 
            corner_radius=12
        )
        self.card_frame.pack(fill="both", expand=True, padx=2, pady=2)

        # Header Row (Step Counter + Close)
        header_row = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        header_row.pack(fill="x", padx=15, pady=(12, 0))

        self.lbl_step_indicator = ctk.CTkLabel(
            header_row, text="", font=("Poppins", 10, "bold"), text_color="#3B82F6"
        )
        self.lbl_step_indicator.pack(side="left")

        ctk.CTkButton(
            header_row, text="✕", width=24, height=24, font=("Poppins", 11, "bold"),
            fg_color="transparent", text_color=("gray50", "#888888"),
            hover_color=("gray85", "#2B2B3D"), command=self.close_tutorial
        ).pack(side="right")

        # Content Layout
        content_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=(2, 10))

        self.lbl_title = ctk.CTkLabel(
            content_frame, text="", font=("Poppins", 14, "bold"), text_color=("gray10", "#FFFFFF"), anchor="w"
        )
        self.lbl_title.pack(fill="x", pady=(2, 4))

        self.lbl_desc = ctk.CTkLabel(
            content_frame, text="", font=("Poppins", 11), text_color=("gray40", "#AAAAAA"),
            justify="left", anchor="w", wraplength=330
        )
        self.lbl_desc.pack(fill="x", pady=(0, 10))

        # Navigation Buttons Footer
        nav_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        nav_frame.pack(fill="x", padx=15, pady=(0, 12))

        self.btn_back = ctk.CTkButton(
            nav_frame, text="← Back", font=("Poppins", 11), fg_color="transparent",
            text_color=("gray50", "#888888"), hover_color=("gray85", "#2B2B3D"), width=70, height=30,
            command=self.prev_step
        )
        self.btn_back.pack(side="left")

        self.btn_next = ctk.CTkButton(
            nav_frame, text="Next ➔", font=("Poppins", 11, "bold"),
            fg_color="#3B82F6", hover_color="#2563EB", width=90, height=30,
            command=self.next_step
        )
        self.btn_next.pack(side="right")

        # Load first step and position window
        self.update_step_ui()

    def update_step_ui(self):
        step_data = self.steps[self.current_step]
        self.lbl_step_indicator.configure(text=f"STEP {self.current_step + 1} OF {len(self.steps)}")
        self.lbl_title.configure(text=f"{step_data['icon']}  {step_data['title']}")
        self.lbl_desc.configure(text=step_data["desc"])

        # Button states
        if self.current_step == 0:
            self.btn_back.pack_forget()
        else:
            self.btn_back.pack(side="left")

        if self.current_step == len(self.steps) - 1:
            self.btn_next.configure(text="✨ Finish", fg_color="#10B981", hover_color="#059669")
        else:
            self.btn_next.configure(text="Next ➔", fg_color="#3B82F6", hover_color="#2563EB")

        # Reposition floating card near target widget or center
        self.position_floating_card(step_data.get("target"))

    def position_floating_card(self, target_key):
        """Calculates screen coordinates to float the tutorial card next to target widgets."""
        self.update_idletasks()
        w, h = 380, 220

        if target_key and self.target_widgets and target_key in self.target_widgets:
            widget = self.target_widgets[target_key]
            try:
                # Get root absolute coordinates of the target button/frame
                x = widget.winfo_rootx() + widget.winfo_width() + 15
                y = widget.winfo_rooty()
                
                # Check if it goes off screen on the right, fallback to placing it on the left
                screen_w = self.winfo_screenwidth()
                if x + w > screen_w:
                    x = widget.winfo_rootx() - w - 15

                self.geometry(f"{w}x{h}+{x}+{y}")
                return
            except Exception:
                pass

        # Default fallback: Center on screen
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def next_step(self):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.update_step_ui()
        else:
            self.close_tutorial()

    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.update_step_ui()

    def close_tutorial(self):
        if self.on_finish_callback:
            self.on_finish_callback()
        self.destroy()