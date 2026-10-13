import customtkinter as ctk


class OnboardingTutorial(ctk.CTkToplevel):
    """Interactive step-by-step tutorial modal for first-time Study SyncMate users."""

    def __init__(self, parent, controller, on_finish_callback=None):
        super().__init__(parent)
        self.controller = controller
        self.on_finish_callback = on_finish_callback

        self.title("Welcome to Study SyncMate 🎓")
        self.geometry("460x320")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()  # Make modal modal-focused

        # Center the modal on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_reqwidth()) // 2
        y = (self.winfo_screenheight() - self.winfo_reqheight()) // 2
        self.geometry(f"+{x}+{y}")

        # Tutorial Steps Data
        self.steps = [
            {
                "icon": "🚀",
                "title": "Welcome to Study SyncMate!",
                "desc": "Your centralized, modular academic desktop application designed to keep your notes, quizzes, and schedules perfectly synchronized."
            },
            {
                "icon": "📓",
                "title": "My Notes Workspace",
                "desc": "Create notes by subject, format text, and upload media attachments (images, PDFs, documents) to build your personal knowledge base."
            },
            {
                "icon": "🧠",
                "title": "Intelligent Quizzes & Flashcards",
                "desc": "Turn your saved notes into interactive Multiple Choice, Identification, and Enumeration practice tests or flashcard reviews instantly."
            },
            {
                "icon": "📅",
                "title": "Schedule & Task Planner",
                "desc": "Organize your academic deadlines, set priorities, and track active study tasks using the interactive calendar view."
            },
            {
                "icon": "📊",
                "title": "Progress Analytics & Settings",
                "desc": "Monitor your study hours, view past quiz performance scores, and customize your app experience with Dark/Light themes and font scaling!"
            }
        ]
        
        self.current_step = 0

        # UI Container Frame
        self.card_frame = ctk.CTkFrame(self, fg_color=("white", "#1E1E2E"), corner_radius=12)
        self.card_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Icon Label
        self.lbl_icon = ctk.CTkLabel(self.card_frame, text="", font=("Poppins", 36))
        self.lbl_icon.pack(pady=(20, 5))

        # Title Label
        self.lbl_title = ctk.CTkLabel(
            self.card_frame, text="", font=("Poppins", 16, "bold"), text_color=("gray10", "#FFFFFF")
        )
        self.lbl_title.pack(pady=(0, 8))

        # Description Label
        self.lbl_desc = ctk.CTkLabel(
            self.card_frame, 
            text="", 
            font=("Poppins", 12), 
            text_color=("gray40", "#AAAAAA"), 
            justify="center", 
            wraplength=380
        )
        self.lbl_desc.pack(pady=(0, 20), padx=20)

        # Navigation Buttons Frame
        nav_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        nav_frame.pack(fill="x", padx=25, pady=(0, 15))

        self.btn_skip = ctk.CTkButton(
            nav_frame, text="Skip Tour", font=("Poppins", 11), fg_color="transparent", 
            text_color=("gray50", "#888888"), hover_color=("gray85", "#2B2B3D"), width=90, command=self.close_tutorial
        )
        self.btn_skip.pack(side="left")

        self.btn_next = ctk.CTkButton(
            nav_frame, text="Next ➔", font=("Poppins", 12, "bold"), 
            fg_color="#3B82F6", hover_color="#2563EB", width=110, height=36, command=self.next_step
        )
        self.btn_next.pack(side="right")

        # Load first step
        self.update_step_ui()

    def update_step_ui(self):
        step_data = self.steps[self.current_step]
        self.lbl_icon.configure(text=step_data["icon"])
        self.lbl_title.configure(text=step_data["title"])
        self.lbl_desc.configure(text=step_data["desc"])

        if self.current_step == len(self.steps) - 1:
            self.btn_next.configure(text="✨ Get Started", fg_color="#10B981", hover_color="#059669")
        else:
            self.btn_next.configure(text="Next ➔", fg_color="#3B82F6", hover_color="#2563EB")

    def next_step(self):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.update_step_ui()
        else:
            self.close_tutorial()

    def close_tutorial(self):
        if self.on_finish_callback:
            self.on_finish_callback()
        self.destroy()