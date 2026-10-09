import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from logic.my_notes import NotesManager


class NotesDashboardView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.notes_logic = NotesManager()

        # Temporary list to store attached file paths for the current note
        self.selected_file_paths = []

        # Configure grid layout (2 columns: left for form, right for saved notes)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # =============================================================
        # LEFT FRAME: CREATE / EDIT NOTE FORM
        # =============================================================
        self.form_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1E1E2E")
        self.form_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(
            self.form_frame, 
            text="Create New Study Note", 
            font=("Poppins", 18, "bold"), 
            text_color="#FFFFFF"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        # 1. Subject / Category
        ctk.CTkLabel(self.form_frame, text="Subject / Course:", font=("Poppins", 12)).pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_subject = ctk.CTkEntry(self.form_frame, placeholder_text="e.g., Computer Science, Math", height=35)
        self.entry_subject.pack(fill="x", padx=20, pady=(0, 10))

        # 2. Title / Topic
        ctk.CTkLabel(self.form_frame, text="Title / Topic:", font=("Poppins", 12)).pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_title = ctk.CTkEntry(self.form_frame, placeholder_text="e.g., Data Structures & Algorithms", height=35)
        self.entry_title.pack(fill="x", padx=20, pady=(0, 10))

        # 3. Notes Content
        ctk.CTkLabel(self.form_frame, text="Note Content:", font=("Poppins", 12)).pack(anchor="w", padx=20, pady=(5, 2))
        self.textbox_content = ctk.CTkTextbox(self.form_frame, height=180)
        self.textbox_content.pack(fill="x", padx=20, pady=(0, 10))

        # 4. Attachments Section
        self.attachment_frame = ctk.CTkFrame(self.form_frame, fg_color="#2B2B3D", corner_radius=8)
        self.attachment_frame.pack(fill="x", padx=20, pady=10)

        self.btn_attach = ctk.CTkButton(
            self.attachment_frame,
            text="📎 Upload Media / Files",
            font=("Poppins", 12, "bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            command=self.select_files
        )
        self.btn_attach.pack(side="left", padx=10, pady=10)

        self.lbl_attachments_count = ctk.CTkLabel(
            self.attachment_frame, 
            text="No files attached", 
            font=("Poppins", 11),
            text_color="#AAAAAA"
        )
        self.lbl_attachments_count.pack(side="left", padx=10)

        # 5. Save Button
        self.btn_save = ctk.CTkButton(
            self.form_frame,
            text="💾 Save Note",
            font=("Poppins", 14, "bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=40,
            command=self.save_note
        )
        self.btn_save.pack(fill="x", padx=20, pady=(10, 15))

        # =============================================================
        # RIGHT FRAME: RECENT NOTES LIST
        # =============================================================
        self.notes_list_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1E1E2E")
        self.notes_list_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(
            self.notes_list_frame, 
            text="My Saved Notes", 
            font=("Poppins", 18, "bold"), 
            text_color="#FFFFFF"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        self.scroll_notes = ctk.CTkScrollableFrame(self.notes_list_frame, fg_color="transparent")
        self.scroll_notes.pack(fill="both", expand=True, padx=10, pady=10)

    # =============================================================
    # EVENT HANDLERS & LOGIC INTEGRATION
    # =============================================================

    def select_files(self):
        """Opens native file picker for images, videos, and documents."""
        file_paths = filedialog.askopenfilenames(
            title="Select Attachments (Images, Videos, Documents)",
            filetypes=[
                ("All Supported Files", "*.png *.jpg *.jpeg *.gif *.mp4 *.mkv *.avi *.pdf *.docx *.txt"),
                ("Images", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("Videos", "*.mp4 *.mkv *.avi *.mov *.webm"),
                ("Documents", "*.pdf *.docx *.txt")
            ]
        )

        if file_paths:
            self.selected_file_paths = list(file_paths)
            count = len(self.selected_file_paths)
            self.lbl_attachments_count.configure(
                text=f"{count} file(s) selected", 
                text_color="#10B981"
            )

    def save_note(self):
        """Reads user input and saves the note via NotesManager."""
        user_id = self.controller.current_user["id"] if hasattr(self.controller, "current_user") and self.controller.current_user else 1

        subject = self.entry_subject.get().strip()
        title = self.entry_title.get().strip()
        content = self.textbox_content.get("1.0", "end-1c").strip()

        if not title:
            messagebox.showwarning("Missing Title", "Please enter a title or topic for your note.")
            return

        success, message, note_id = self.notes_logic.create_note(
            user_id=user_id,
            title=title,
            content=content,
            subject=subject,
            attachment_paths=self.selected_file_paths
        )

        if success:
            messagebox.showinfo("Success", message)
            self.clear_form()
            self.load_user_notes()
        else:
            messagebox.showerror("Error", message)

    def clear_form(self):
        """Resets the input fields and clears selected attachment state."""
        self.entry_subject.delete(0, "end")
        self.entry_title.delete(0, "end")
        self.textbox_content.delete("1.0", "end")
        self.selected_file_paths = []
        self.lbl_attachments_count.configure(text="No files attached", text_color="#AAAAAA")

    def load_user_notes(self):
        """Fetches and displays saved notes from database."""
        for widget in self.scroll_notes.winfo_children():
            widget.destroy()

        user_id = self.controller.current_user["id"] if hasattr(self.controller, "current_user") and self.controller.current_user else 1
        notes = self.notes_logic.get_user_notes(user_id)

        if not notes:
            ctk.CTkLabel(self.scroll_notes, text="No notes saved yet.", text_color="#888888").pack(pady=20)
            return

        for note in notes:
            card = ctk.CTkFrame(self.scroll_notes, fg_color="#2B2B3D", corner_radius=8)
            card.pack(fill="x", pady=5, padx=5)

            # Header info
            ctk.CTkLabel(card, text=note["title"], font=("Poppins", 14, "bold"), text_color="#FFFFFF").pack(anchor="w", padx=10, pady=(8, 0))
            ctk.CTkLabel(card, text=f"Subject: {note['subject']}", font=("Poppins", 11), text_color="#3B82F6").pack(anchor="w", padx=10)

            # Attachments count indicator
            attachments = note.get("attachments", [])
            if attachments:
                ctk.CTkLabel(
                    card, 
                    text=f"📎 {len(attachments)} Media/Attachment(s)", 
                    font=("Poppins", 10), 
                    text_color="#10B981"
                ).pack(anchor="w", padx=10, pady=(2, 8))

    def on_show(self):
        """Lifecycle method triggered when view switches to notes dashboard."""
        self.load_user_notes()