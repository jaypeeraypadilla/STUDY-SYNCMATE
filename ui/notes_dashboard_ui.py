import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
from logic.my_notes import NotesManager


class NotesDashboardView(ctk.CTkFrame):
    """Clean 3-column Master-Detail-Preview Notes Workspace with scalable font support."""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.notes_logic = NotesManager()

        # State tracking
        self.selected_file_paths = []
        self.editing_note_id = None
        self.current_existing_attachments = []
        self.active_subject_filter = "ALL"
        self.search_query = ""
        self.all_user_notes = []
        self.pill_buttons = {}
        self.active_selected_note = None

        # Configure 3-Column Grid Layout with scalable weighting
        self.grid_columnconfigure(0, weight=1, minsize=260)  # Left: Notes Explorer List
        self.grid_columnconfigure(1, weight=1, minsize=300)  # Middle: Editor Form
        self.grid_columnconfigure(2, weight=1, minsize=260)  # Right: Live Preview Pane
        self.grid_rowconfigure(0, weight=1)

        # =============================================================
        # COLUMN 1: NOTES EXPLORER (Search, Pills, Note Cards)
        # =============================================================
        self.explorer_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=("white", "#1E1E2E"))
        self.explorer_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        self.explorer_frame.grid_rowconfigure(3, weight=1)
        self.explorer_frame.grid_columnconfigure(0, weight=1)

        search_row = ctk.CTkFrame(self.explorer_frame, fg_color="transparent")
        search_row.pack(fill="x", padx=12, pady=(15, 10))

        self.entry_search = ctk.CTkEntry(
            search_row, 
            placeholder_text="🔍 Search Notes...", 
            fg_color=("gray90", "#2B2B3D"),
            text_color=("gray10", "#FFFFFF")
        )
        self.entry_search.pack(side="left", fill="x", expand=True, padx=(0, 6), ipady=4)
        self.entry_search.bind("<KeyRelease>", self.on_search_change)

        ctk.CTkButton(
            search_row,
            text="+ New",
            font=("Poppins", 11, "bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            width=70,
            command=self.clear_form
        ).pack(side="right", ipady=4)

        self.pills_frame = ctk.CTkScrollableFrame(self.explorer_frame, orientation="horizontal", fg_color="transparent", height=50)
        self.pills_frame.pack(fill="x", padx=12, pady=(0, 10))

        self.scroll_notes = ctk.CTkScrollableFrame(self.explorer_frame, fg_color="transparent")
        self.scroll_notes.pack(fill="both", expand=True, padx=8, pady=(0, 10))

        # =============================================================
        # COLUMN 2: EDITOR WORKSPACE (Form Inputs & Toolbar)
        # =============================================================
        self.editor_frame = ctk.CTkScrollableFrame(self, corner_radius=10, fg_color=("white", "#1E1E2E"))
        self.editor_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)

        # Editor Top Bar using Grid to guarantee the Save button stays fixed
        editor_top_bar = ctk.CTkFrame(self.editor_frame, fg_color="transparent")
        editor_top_bar.pack(fill="x", padx=15, pady=(15, 10))
        editor_top_bar.grid_columnconfigure(0, weight=1)
        editor_top_bar.grid_columnconfigure(1, weight=0)

        self.form_title_label = ctk.CTkLabel(
            editor_top_bar, 
            text="✏️ Create New Note", 
            font=("Poppins", 15, "bold"), 
            text_color=("gray10", "#FFFFFF"),
            anchor="w"
        )
        self.form_title_label.grid(row=0, column=0, sticky="ew")

        self.btn_save = ctk.CTkButton(
            editor_top_bar,
            text="SAVE",
            font=("Poppins", 11, "bold"),
            fg_color="#10B981",
            hover_color="#059669",
            width=65,
            command=self.save_note
        )
        self.btn_save.grid(row=0, column=1, sticky="e", padx=(10, 0), ipady=2)

        ctk.CTkLabel(self.editor_frame, text="SUBJECT", font=("Poppins", 10, "bold"), text_color=("gray50", "#AAAAAA")).pack(anchor="w", padx=15, pady=(5, 2))
        self.entry_subject = ctk.CTkEntry(
            self.editor_frame, 
            placeholder_text="e.g., ITE 260", 
            fg_color=("gray90", "#2B2B3D"),
            text_color=("gray10", "#FFFFFF")
        )
        self.entry_subject.pack(fill="x", padx=15, pady=(0, 10), ipady=4)

        ctk.CTkLabel(self.editor_frame, text="TITLE / TOPIC", font=("Poppins", 10, "bold"), text_color=("gray50", "#AAAAAA")).pack(anchor="w", padx=15, pady=(5, 2))
        self.entry_title = ctk.CTkEntry(
            self.editor_frame, 
            placeholder_text="e.g., Arithmetic Operator", 
            fg_color=("gray90", "#2B2B3D"),
            text_color=("gray10", "#FFFFFF")
        )
        self.entry_title.pack(fill="x", padx=15, pady=(0, 10), ipady=4)

        ctk.CTkLabel(self.editor_frame, text="NOTE CONTENT", font=("Poppins", 10, "bold"), text_color=("gray50", "#AAAAAA")).pack(anchor="w", padx=15, pady=(5, 2))
        
        toolbar = ctk.CTkFrame(self.editor_frame, fg_color=("gray85", "#2B2B3D"), corner_radius=6)
        toolbar.pack(fill="x", padx=15, pady=(0, 4))

        ctk.CTkButton(toolbar, text="B", width=32, font=("Poppins", 10, "bold"), fg_color="#3B82F6", command=lambda: self.apply_formatting("**", "**")).pack(side="left", padx=3, pady=4)
        ctk.CTkButton(toolbar, text="I", width=32, font=("Poppins", 10, "italic"), fg_color="#3B82F6", command=lambda: self.apply_formatting("*", "*")).pack(side="left", padx=3, pady=4)
        ctk.CTkButton(toolbar, text="U", width=32, font=("Poppins", 10, "underline"), fg_color="#3B82F6", command=lambda: self.apply_formatting("__", "__")).pack(side="left", padx=3, pady=4)
        ctk.CTkButton(toolbar, text="A⁺", width=32, font=("Poppins", 9, "bold"), fg_color="#8B5CF6", command=lambda: self.apply_formatting("# ", "")).pack(side="left", padx=3, pady=4)
        ctk.CTkButton(toolbar, text="📋", width=32, font=("Poppins", 9), fg_color="#F59E0B", command=lambda: self.apply_formatting("- ", "")).pack(side="left", padx=3, pady=4)

        self.textbox_content = ctk.CTkTextbox(
            self.editor_frame, 
            height=150,
            fg_color=("gray90", "#2B2B3D"),
            text_color=("gray10", "#FFFFFF"),
            font=("Poppins", 11)
        )
        self.textbox_content.pack(fill="x", padx=15, pady=(0, 10))

        att_box = ctk.CTkFrame(self.editor_frame, fg_color=("gray90", "#2B2B3D"), corner_radius=8)
        att_box.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(
            att_box, text="📎 Attach", font=("Poppins", 10, "bold"), fg_color="#3B82F6", width=90, command=self.select_files
        ).pack(side="left", padx=8, pady=8, ipady=2)

        self.lbl_attachments_count = ctk.CTkLabel(att_box, text="No files attached", font=("Poppins", 9), text_color=("gray50", "#AAAAAA"))
        self.lbl_attachments_count.pack(side="left", padx=4)

        ctk.CTkButton(
            self.editor_frame, text="Reset Form", font=("Poppins", 10), fg_color=("gray70", "#4B5563"), command=self.clear_form
        ).pack(fill="x", padx=15, pady=(12, 15), ipady=4)

        # =============================================================
        # COLUMN 3: LIVE PREVIEW PANEL (Right Pane)
        # =============================================================
        self.preview_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=("white", "#1E1E2E"))
        self.preview_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 10), pady=10)
        self.preview_frame.grid_rowconfigure(2, weight=1)
        self.preview_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.preview_frame, 
            text="👁️ Live Preview", 
            font=("Poppins", 15, "bold"), 
            text_color=("gray10", "#FFFFFF")
        ).pack(anchor="w", padx=15, pady=(15, 10))

        self.preview_card = ctk.CTkFrame(self.preview_frame, fg_color=("gray95", "#2B2B3D"), corner_radius=8)
        self.preview_card.pack(fill="both", expand=True, padx=12, pady=(0, 15))

        self.preview_meta_label = ctk.CTkLabel(
            self.preview_card, 
            text="SUBJECT • DATE", 
            font=("Poppins", 10, "bold"), 
            text_color="#10B981"
        )
        self.preview_meta_label.pack(anchor="w", padx=15, pady=(12, 2))

        self.preview_title_label = ctk.CTkLabel(
            self.preview_card, 
            text="Select a note to preview", 
            font=("Poppins", 14, "bold"), 
            text_color=("gray10", "#FFFFFF"),
            anchor="w",
            wraplength=240,
            justify="left"
        )
        self.preview_title_label.pack(anchor="w", padx=15, pady=(0, 8))

        # Scrollable container for text content AND image attachments
        self.preview_scroll_area = ctk.CTkScrollableFrame(self.preview_card, fg_color="transparent")
        self.preview_scroll_area.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.preview_content_textbox = ctk.CTkTextbox(
            self.preview_scroll_area,
            height=120,
            fg_color="transparent",
            text_color=("gray20", "#E0E0E0"),
            font=("Poppins", 11)
        )
        self.preview_content_textbox.pack(fill="x", expand=False, padx=0, pady=(0, 10))
        self.preview_content_textbox.configure(state="disabled")

        # Container specifically for rendering image preview widgets
        self.preview_images_container = ctk.CTkFrame(self.preview_scroll_area, fg_color="transparent")
        self.preview_images_container.pack(fill="both", expand=True, padx=0, pady=5)

    # =============================================================
    # LOGIC & EVENT HANDLERS
    # =============================================================

    def apply_formatting(self, prefix: str, suffix: str):
        try:
            selected = self.textbox_content.get("sel.first", "sel.last")
            self.textbox_content.delete("sel.first", "sel.last")
            self.textbox_content.insert("insert", f"{prefix}{selected}{suffix}")
        except Exception:
            self.textbox_content.insert("insert", f"{prefix}{suffix}")

    def _get_user_id(self) -> int:
        if hasattr(self.controller, "current_user") and self.controller.current_user:
            return self.controller.current_user.get("id", 1)
        return 1

    def select_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Attachments",
            filetypes=[("All Supported Files", "*.png *.jpg *.jpeg *.mp4 *.pdf *.docx *.txt")]
        )
        if file_paths:
            self.selected_file_paths = list(file_paths)
            self.lbl_attachments_count.configure(text=f"{len(self.selected_file_paths)} attached", text_color="#10B981")

    def filter_by_subject(self, subject: str):
        self.active_subject_filter = subject
        for s, btn in self.pill_buttons.items():
            if s == subject:
                btn.configure(fg_color="#3B82F6", text_color="white")
            else:
                btn.configure(fg_color=("gray85", "#2B2B3D"), text_color=("gray10", "#CCCCCC"))
        self.render_filtered_notes()

    def on_search_change(self, event=None):
        self.search_query = self.entry_search.get().strip().lower()
        self.render_filtered_notes()

    def save_note(self):
        user_id = self._get_user_id()
        subject = self.entry_subject.get().strip()
        title = self.entry_title.get().strip()
        content = self.textbox_content.get("1.0", "end-1c").strip()

        if not title:
            messagebox.showwarning("Missing Title", "Please enter a title or topic.")
            return

        new_atts = self.selected_file_paths

        if self.editing_note_id:
            success, message = self.notes_logic.update_note(
                note_id=self.editing_note_id, title=title, content=content,
                subject=subject if subject else "General",
                existing_attachments=self.current_existing_attachments, new_attachment_paths=new_atts
            )
        else:
            success, message, _ = self.notes_logic.create_note(
                user_id=user_id, title=title, content=content,
                subject=subject if subject else "General", attachment_paths=new_atts
            )

        if success:
            messagebox.showinfo("Success", message)
            self.clear_form()
            self.load_user_notes()
        else:
            messagebox.showerror("Error", message)

    def clear_form(self):
        """Resets the editor form and clears the live preview state."""
        self.editing_note_id = None
        self.current_existing_attachments = []
        self.selected_file_paths = []
        self.active_selected_note = None
        
        self.form_title_label.configure(text="✏️ Create New Note")
        self.entry_subject.delete(0, "end")
        self.entry_title.delete(0, "end")
        self.textbox_content.delete("1.0", "end")
        self.lbl_attachments_count.configure(text="No files attached", text_color=("gray50", "#AAAAAA"))

        # Reset preview pane to empty state
        self.preview_meta_label.configure(text="SUBJECT • DATE")
        self.preview_title_label.configure(text="Select a note to preview")
        self.preview_content_textbox.configure(state="normal")
        self.preview_content_textbox.delete("1.0", "end")
        self.preview_content_textbox.configure(state="disabled")

        # Clear preview images
        for widget in self.preview_images_container.winfo_children():
            widget.destroy()

    def load_user_notes(self):
        user_id = self._get_user_id()
        self.all_user_notes = self.notes_logic.get_user_notes(user_id)
        self.refresh_subject_pills()
        self.render_filtered_notes()

        # Automatically load the first note into preview if none is active
        if self.all_user_notes and not self.active_selected_note:
            self.load_note_into_preview(self.all_user_notes[0])
        elif not self.all_user_notes:
            self.clear_form()

    def refresh_subject_pills(self):
        for widget in self.pills_frame.winfo_children():
            widget.destroy()
        self.pill_buttons = {}

        unique_subjects = sorted(list(set(n.get("subject", "General") or "General" for n in self.all_user_notes)))
        subjects_list = ["ALL"] + unique_subjects

        if self.active_subject_filter not in subjects_list:
            self.active_subject_filter = "ALL"

        for subj in subjects_list:
            btn = ctk.CTkButton(
                self.pills_frame,
                text=subj,
                font=("Poppins", 10, "bold"),
                width=65,
                fg_color="#3B82F6" if subj == self.active_subject_filter else ("gray85", "#2B2B3D"),
                text_color="white" if subj == self.active_subject_filter else ("gray10", "#CCCCCC"),
                command=lambda s=subj: self.filter_by_subject(s)
            )
            btn.pack(side="left", padx=3, ipady=2)
            self.pill_buttons[subj] = btn

    def render_filtered_notes(self):
        for widget in self.scroll_notes.winfo_children():
            widget.destroy()

        filtered = []
        for note in self.all_user_notes:
            subj = note.get("subject", "General") or "General"
            title = note.get("title", "")
            content = note.get("content", "")

            if self.active_subject_filter != "ALL" and self.active_subject_filter.lower() != subj.lower():
                continue
            if self.search_query and self.search_query not in title.lower() and self.search_query not in content.lower():
                continue

            filtered.append(note)

        if not filtered:
            ctk.CTkLabel(self.scroll_notes, text="No notes found.", text_color=("gray50", "#888888"), font=("Poppins", 11)).pack(pady=20)
            return

        for note in filtered:
            card = ctk.CTkFrame(self.scroll_notes, fg_color=("gray95", "#2B2B3D"), corner_radius=8)
            card.pack(fill="x", pady=4, padx=2)

            top_r = ctk.CTkFrame(card, fg_color="transparent")
            top_r.pack(fill="x", padx=10, pady=(8, 2))

            ctk.CTkLabel(
                top_r, 
                text=f"{note.get('subject', 'General')} - {note.get('title', 'Untitled')}", 
                font=("Poppins", 11, "bold"), 
                text_color=("#059669", "#10B981")
            ).pack(side="left")

            timestamp = note.get("created_at", "")
            ctk.CTkLabel(
                top_r, 
                text=timestamp[:10] if timestamp else "", 
                font=("Poppins", 9), 
                text_color=("gray50", "#AAAAAA")
            ).pack(side="right")

            snippet = note.get("content", "")
            ctk.CTkLabel(
                card, 
                text=(snippet[:90] + "...") if len(snippet) > 90 else (snippet or "(No preview)"), 
                font=("Poppins", 10), 
                text_color=("gray30", "#CCCCCC"),
                justify="left",
                anchor="w",
                wraplength=220
            ).pack(anchor="w", padx=10, pady=(0, 6))

            act_bar = ctk.CTkFrame(card, fg_color="transparent")
            act_bar.pack(fill="x", padx=10, pady=(0, 8))

            def make_select_action(n=note):
                return lambda: self.load_note_into_preview_and_form(n)

            def make_delete_action(n=note):
                return lambda: self.delete_note_action(n)

            ctk.CTkButton(act_bar, text="View/Edit", width=65, font=("Poppins", 9, "bold"), fg_color="#3B82F6", command=make_select_action()).pack(side="left", padx=(0, 4), ipady=1)
            ctk.CTkButton(act_bar, text="Delete", width=55, font=("Poppins", 9, "bold"), fg_color="#EF4444", command=make_delete_action()).pack(side="left", ipady=1)

    def load_note_into_preview(self, note: dict):
        self.active_selected_note = note
        self.preview_meta_label.configure(text=f"{note.get('subject', 'General').upper()} • {note.get('created_at', '')[:10]}")
        self.preview_title_label.configure(text=note.get("title", "Untitled"))
        
        # Load text content
        self.preview_content_textbox.configure(state="normal")
        self.preview_content_textbox.delete("1.0", "end")
        self.preview_content_textbox.insert("1.0", note.get("content", ""))
        self.preview_content_textbox.configure(state="disabled")

        # Clear previous preview images
        for widget in self.preview_images_container.winfo_children():
            widget.destroy()

        # Load and render attached images dynamically
        attachments = note.get("attachments", [])
        for att in attachments:
            if att.get("file_type") == "image":
                saved_path = att.get("saved_path")
                if saved_path and os.path.exists(saved_path):
                    try:
                        pil_img = Image.open(saved_path)
                        img_width, img_height = pil_img.size
                        target_width = 220
                        target_height = max(100, int((target_width / img_width) * img_height))

                        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(target_width, target_height))

                        img_card = ctk.CTkFrame(self.preview_images_container, fg_color=("gray90", "#1E1E2E"), corner_radius=6)
                        img_card.pack(fill="x", pady=6, padx=2)

                        img_lbl = ctk.CTkLabel(img_card, text="", image=ctk_img)
                        img_lbl.image = ctk_img
                        img_lbl.pack(padx=5, pady=5)

                        orig_name = att.get("original_name", "Attached Image")
                        ctk.CTkLabel(
                            img_card, 
                            text=f"📷 {orig_name}", 
                            font=("Poppins", 9, "italic"), 
                            text_color=("gray50", "#AAAAAA")
                        ).pack(anchor="w", padx=8, pady=(0, 5))

                    except Exception as e:
                        print(f"[Preview] Error rendering image {saved_path}: {e}")

    def load_note_into_preview_and_form(self, note: dict):
        self.load_note_into_preview(note)
        self.editing_note_id = note["id"]
        self.current_existing_attachments = note.get("attachments", [])
        self.selected_file_paths = []
        self.form_title_label.configure(text=f"✏️ Editing: {note['title']}")
        self.entry_subject.delete(0, "end")
        self.entry_subject.insert(0, note.get("subject", ""))
        self.entry_title.delete(0, "end")
        self.entry_title.insert(0, note.get("title", ""))
        self.textbox_content.delete("1.0", "end")
        self.textbox_content.insert("1.0", note.get("content", ""))
        if self.current_existing_attachments:
            self.lbl_attachments_count.configure(text=f"{len(self.current_existing_attachments)} attached", text_color="#3B82F6")
        else:
            self.lbl_attachments_count.configure(text="No files attached", text_color=("gray50", "#AAAAAA"))

    def delete_note_action(self, note: dict):
        if messagebox.askyesno("Confirm Delete", f"Delete note '{note['title']}'?"):
            self.notes_logic.delete_note(note["id"])
            if self.active_selected_note and self.active_selected_note.get("id") == note["id"]:
                self.active_selected_note = None
            self.clear_form()
            self.load_user_notes()

    def on_show(self):
        self.load_user_notes()