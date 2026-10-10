import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from logic.my_notes import NotesManager


class NotesDashboardView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.notes_logic = NotesManager()

        # Temporary list to store newly selected attached file paths
        self.selected_file_paths = []
        # Stores currently loaded note ID for updating/editing
        self.editing_note_id = None
        # Stores existing attachments when editing so they aren't lost
        self.current_existing_attachments = []

        # Configure grid layout (2 columns: left for form, right for saved notes per subject)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # =============================================================
        # LEFT FRAME: CREATE / EDIT NOTE FORM
        # =============================================================
        self.form_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1E1E2E")
        self.form_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.form_title_label = ctk.CTkLabel(
            self.form_frame, 
            text="Create New Study Note", 
            font=("Poppins", 18, "bold"), 
            text_color="#FFFFFF"
        )
        self.form_title_label.pack(anchor="w", padx=20, pady=(15, 10))

        # 1. Subject / Course Input
        ctk.CTkLabel(self.form_frame, text="Subject / Course:", font=("Poppins", 12)).pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_subject = ctk.CTkEntry(self.form_frame, placeholder_text="e.g., Computer Science, Math", height=35)
        self.entry_subject.pack(fill="x", padx=20, pady=(0, 10))

        # 2. Title / Topic Input
        ctk.CTkLabel(self.form_frame, text="Title / Topic:", font=("Poppins", 12)).pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_title = ctk.CTkEntry(self.form_frame, placeholder_text="e.g., Data Structures & Algorithms", height=35)
        self.entry_title.pack(fill="x", padx=20, pady=(0, 10))

        # 3. Notes Content Textbox
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

        # 5. Form Action Buttons (Save/Update & Reset)
        self.actions_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.actions_frame.pack(fill="x", padx=20, pady=(10, 15))

        self.btn_save = ctk.CTkButton(
            self.actions_frame,
            text="💾 Save Note",
            font=("Poppins", 14, "bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=40,
            command=self.save_note
        )
        self.btn_save.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.btn_clear = ctk.CTkButton(
            self.actions_frame,
            text="Reset",
            font=("Poppins", 12, "bold"),
            fg_color="#4B5563",
            hover_color="#374151",
            height=40,
            width=80,
            command=self.clear_form
        )
        self.btn_clear.pack(side="right", padx=(5, 0))

        # =============================================================
        # RIGHT FRAME: SAVED NOTES GROUPED BY SUBJECT
        # =============================================================
        self.notes_list_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1E1E2E")
        self.notes_list_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(
            self.notes_list_frame, 
            text="My Saved Notes (By Subject)", 
            font=("Poppins", 18, "bold"), 
            text_color="#FFFFFF"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        self.scroll_notes = ctk.CTkScrollableFrame(self.notes_list_frame, fg_color="transparent")
        self.scroll_notes.pack(fill="both", expand=True, padx=10, pady=10)

    # =============================================================
    # EVENT HANDLERS & LOGIC INTEGRATION
    # =============================================================

    def _get_user_id(self) -> int:
        if hasattr(self.controller, "current_user") and self.controller.current_user:
            return self.controller.current_user.get("id", 1)
        return 1

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
                text=f"{count} new file(s) selected", 
                text_color="#10B981"
            )

    def save_note(self):
        """Reads user input and saves or updates the note in database."""
        user_id = self._get_user_id()
        subject = self.entry_subject.get().strip()
        title = self.entry_title.get().strip()
        content = self.textbox_content.get("1.0", "end-1c").strip()

        if not title:
            messagebox.showwarning("Missing Title", "Please enter a title or topic for your note.")
            return

        if self.editing_note_id:
            # Update existing note (preserving old attachments + adding new ones)
            success, message = self.notes_logic.update_note(
                note_id=self.editing_note_id,
                title=title,
                content=content,
                subject=subject if subject else "General",
                existing_attachments=self.current_existing_attachments,
                new_attachment_paths=self.selected_file_paths
            )
        else:
            # Create new note
            success, message, note_id = self.notes_logic.create_note(
                user_id=user_id,
                title=title,
                content=content,
                subject=subject if subject else "General",
                attachment_paths=self.selected_file_paths
            )

        if success:
            messagebox.showinfo("Success", message)
            self.clear_form()
            self.load_user_notes()
        else:
            messagebox.showerror("Error", message)

    def clear_form(self):
        """Resets the input fields and resets the Save/Update button state."""
        self.editing_note_id = None
        self.current_existing_attachments = []
        self.form_title_label.configure(text="Create New Study Note")
        
        # Reset button back to "Save Note" (Green)
        self.btn_save.configure(text="💾 Save Note", fg_color="#10B981", hover_color="#059669")
        
        self.entry_subject.delete(0, "end")
        self.entry_title.delete(0, "end")
        self.textbox_content.delete("1.0", "end")
        self.selected_file_paths = []
        self.lbl_attachments_count.configure(text="No files attached", text_color="#AAAAAA")

    def load_user_notes(self):
        """Fetches and displays saved notes grouped per Subject with Topic Dropdowns."""
        for widget in self.scroll_notes.winfo_children():
            widget.destroy()

        user_id = self._get_user_id()
        notes = self.notes_logic.get_user_notes(user_id)

        if not notes:
            ctk.CTkLabel(self.scroll_notes, text="No notes saved yet.", text_color="#888888").pack(pady=20)
            return

        # Group notes by Subject: { "Computer Science": [note1, note2], "Math": [note3] }
        grouped_notes = {}
        for note in notes:
            subj = note.get("subject", "General") or "General"
            if subj not in grouped_notes:
                grouped_notes[subj] = []
            grouped_notes[subj].append(note)

        # Build UI card for each Subject
        for subject_name, subject_notes in grouped_notes.items():
            subject_card = ctk.CTkFrame(self.scroll_notes, fg_color="#2B2B3D", corner_radius=10)
            subject_card.pack(fill="x", pady=8, padx=5)

            # 1. Subject Header
            ctk.CTkLabel(
                subject_card, 
                text=f"📚 {subject_name} ({len(subject_notes)} Topic{'s' if len(subject_notes) > 1 else ''})", 
                font=("Poppins", 15, "bold"), 
                text_color="#3B82F6"
            ).pack(anchor="w", padx=15, pady=(12, 4))

            # 2. Topic/Title Dropdown Label
            ctk.CTkLabel(
                subject_card, 
                text="Select Topic / Title:", 
                font=("Poppins", 11), 
                text_color="#AAAAAA"
            ).pack(anchor="w", padx=15, pady=(0, 2))

            # Extract list of topic titles for dropdown
            topic_titles = [n["title"] for n in subject_notes]

            # 3. Topic Preview Container
            preview_frame = ctk.CTkFrame(subject_card, fg_color="#1E1E2E", corner_radius=8)
            
            lbl_title = ctk.CTkLabel(preview_frame, text="", font=("Poppins", 14, "bold"), text_color="#FFFFFF", anchor="w")
            lbl_title.pack(fill="x", padx=12, pady=(10, 2))

            lbl_content = ctk.CTkLabel(
                preview_frame, 
                text="", 
                font=("Poppins", 11), 
                text_color="#DDDDDD", 
                anchor="w", 
                justify="left", 
                wraplength=340
            )
            lbl_content.pack(fill="x", padx=12, pady=4)

            lbl_attachments = ctk.CTkLabel(preview_frame, text="", font=("Poppins", 10), text_color="#10B981", anchor="w")
            lbl_attachments.pack(fill="x", padx=12, pady=(2, 8))

            # Action Buttons Frame (Edit & Delete)
            btn_frame = ctk.CTkFrame(preview_frame, fg_color="transparent")
            btn_frame.pack(fill="x", padx=12, pady=(0, 10))

            current_note_ref = {"note": None}

            def edit_selected_note(ref=current_note_ref):
                note = ref["note"]
                if note:
                    self.editing_note_id = note["id"]
                    self.current_existing_attachments = note.get("attachments", [])
                    
                    # Update form title & transform Save button into an "Update Note" button (Amber)
                    self.form_title_label.configure(text=f"Editing: {note['title']}")
                    self.btn_save.configure(text="💾 Update Note", fg_color="#F59E0B", hover_color="#D97706")
                    
                    self.entry_subject.delete(0, "end")
                    self.entry_subject.insert(0, note.get("subject", ""))
                    self.entry_title.delete(0, "end")
                    self.entry_title.insert(0, note.get("title", ""))
                    self.textbox_content.delete("1.0", "end")
                    self.textbox_content.insert("1.0", note.get("content", ""))
                    
                    if self.current_existing_attachments:
                        self.lbl_attachments_count.configure(
                            text=f"{len(self.current_existing_attachments)} existing file(s)",
                            text_color="#3B82F6"
                        )

            def delete_selected_note(ref=current_note_ref):
                note = ref["note"]
                if note and messagebox.askyesno("Confirm Delete", f"Delete topic '{note['title']}'?"):
                    self.notes_logic.delete_note(note["id"])
                    self.clear_form()
                    self.load_user_notes()

            btn_edit_topic = ctk.CTkButton(
                btn_frame, text="✏️ Edit", font=("Poppins", 11, "bold"), 
                width=70, height=28, fg_color="#3B82F6", command=edit_selected_note
            )
            btn_edit_topic.pack(side="left", padx=(0, 5))

            btn_delete_topic = ctk.CTkButton(
                btn_frame, text="🗑️ Delete", font=("Poppins", 11, "bold"), 
                width=75, height=28, fg_color="#EF4444", hover_color="#DC2626", command=delete_selected_note
            )
            btn_delete_topic.pack(side="left")

            # Callback when user selects a topic title from dropdown
            def make_topic_selector(s_notes, p_frame, l_title, l_content, l_att, ref_holder):
                def on_topic_select(selected_title):
                    matched_note = next((n for n in s_notes if n["title"] == selected_title), None)
                    if matched_note:
                        ref_holder["note"] = matched_note
                        p_frame.pack(fill="x", padx=15, pady=(5, 12))
                        l_title.configure(text=matched_note["title"])

                        content = matched_note.get("content", "")
                        display_text = content if len(content) <= 180 else content[:180] + "..."
                        l_content.configure(text=display_text if display_text else "(No text content)")

                        attachments = matched_note.get("attachments", [])
                        if attachments:
                            l_att.configure(text=f"📎 {len(attachments)} Media/Attachment(s)")
                        else:
                            l_att.configure(text="No media attachments")
                return on_topic_select

            on_select_callback = make_topic_selector(
                subject_notes, preview_frame, lbl_title, lbl_content, lbl_attachments, current_note_ref
            )

            # 4. CTkOptionMenu Dropdown for Topics
            topic_dropdown = ctk.CTkOptionMenu(
                subject_card,
                values=topic_titles,
                command=on_select_callback,
                fg_color="#1E1E2E",
                button_color="#3B82F6",
                button_hover_color="#2563EB",
                font=("Poppins", 12),
                dropdown_font=("Poppins", 11),
                height=35
            )
            topic_dropdown.pack(fill="x", padx=15, pady=(0, 10))

            # Auto-select first topic by default
            if topic_titles:
                topic_dropdown.set(topic_titles[0])
                on_select_callback(topic_titles[0])

    def on_show(self):
        """Lifecycle method triggered when view switches to notes dashboard."""
        self.load_user_notes()