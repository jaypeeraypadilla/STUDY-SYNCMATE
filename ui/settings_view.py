import customtkinter as ctk
from tkinter import messagebox


class SettingsViewFrame(ctk.CTkFrame):
    """Settings Workspace for managing App Theme, Language, Font Scaling, Help, About, and Terms information."""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Localization dictionary for English and Filipino
        self.translations = {
            "English": {
                "title_appearance": "🎨 Appearance & Display",
                "lbl_theme": "Interface Theme Mode:",
                "lbl_lang": "Application Language:",
                "lbl_scale": "Font Size & UI Scale:",
                "about_ver": "Study SyncMate v0.1.9",
                "about_desc": (
                    "Study SyncMate is a centralized, modular academic desktop application "
                    "designed to help students organize notes, track tasks, generate practice quizzes, "
                    "and monitor study progress seamlessly.\n\n"
                    "Developers: SilverNox(Ray), Peony(Rich Boy), Yanyan(Jarylle), Athan(Nathanael), Exil3(Aron), and Xywinn(Russel).\n\n\n\n"
                    "Developed with Python, Tkinter, CustomTkinter, and SQLite."
                ),
                "tab_about": "About",
                "tab_help": "Help & FAQ",
                "tab_terms": "Terms & Conditions",
                "terms_title": "Terms and Conditions",
                "terms_desc": (
                    "Welcome to Study SyncMate. By accessing or using this application, you agree to be bound by these terms:\n\n"
                    "1. **Acceptance of Terms**: By using Study SyncMate, you agree to use this application strictly for academic and personal productivity purposes.\n\n"
                    "2. **User Data & Privacy**: All notes, schedules, and profile details are stored locally via SQLite on your device. Ensure your login credentials and security recovery questions are kept secure.\n\n"
                    "3. **Intellectual Property**: Study SyncMate, its layout, code structure, and branding assets are developed for academic and personal projects by its designated student developers.\n\n"
                    "4. **Disclaimer of Warranties**: The software is provided 'as is' without warranties of any kind. The developers are not liable for any data loss or academic consequences arising from its usage."
                ),
                "faqs": [
                    ("How do I save notes?", "Go to 'My Notes', enter your Subject and Topic, then click 'Save Note' or 'Save Text Note Only'."),
                    ("How does Quiz Generator work?", "The AI quiz generator automatically pulls from your saved notes per subject to build practice tests and flashcards."),
                    ("How do I track study time?", "Use the interactive Schedule calendar to plan deadlines and monitor task completion status."),
                    ("Can I change my password?", "Yes! Navigate to the Profile workspace using the top header or settings to update your credentials.")
                ]
            },
            "Filipino": {
                "title_appearance": "🎨 Hitsura at Displey",
                "lbl_theme": "Tema ng Kagamitan (Theme Mode):",
                "lbl_lang": "Wika ng Aplikasyon (Language):",
                "lbl_scale": "Laki ng Teks at Sukat ng UI:",
                "about_ver": "Study SyncMate v0.1.9",
                "about_desc": (
                    "Ang Study SyncMate ay isang sentralisado at modular na desktop application "
                    "na idinisenyo upang tulungan ang mga mag-aaral na isaayos ang mga tala, subaybayan ang mga gawain, "
                    "lumikha ng mga pagsusulit, at bantayan ang kanilang progreso sa pag-aaral.\n\n"
                    "Mga Developer: SilverNox(Ray), Peony(Rich Boy), Yanyan(Jarylle), Athan(Nathanael), Exil3(Aron), at Xywinn(Russel).\n\n\n\n"
                    "Binuo gamit ang Python, Tkinter, CustomTkinter, at SQLite."
                ),
                "tab_about": "Tungkol sa App",
                "tab_help": "Tulong at FAQ",
                "tab_terms": "Mga Tuntunin at Kundisyon",
                "terms_title": "Mga Tuntunin at Kundisyon",
                "terms_desc": (
                    "Maligayang pagdating sa Study SyncMate. Sa paggamit ng aplikasyong ito, sumasang-ayon ka sa mga sumusunod:\n\n"
                    "1. **Paggamit ng Sistema**: Ang Study SyncMate ay para sa layuning akademiko at personal na produktibidad lamang.\n\n"
                    "2. **Seguridad ng Datos**: Ang lahat ng tala, iskedyul, at detalye ay lokal na nakaimbak sa iyong device gamit ang SQLite. Panatilihing ligtas ang iyong account.\n\n"
                    "3. **Karapatang Ari**: Ang disenyo, kodigo, at sistema ay binuo ng mga opisyal na developer para sa kanilang proyekto.\n\n"
                    "4. **Limitasyon ng Pananagutan**: Ang software na ito ay ibinibigay 'kung ano man ito'. Hindi pananagutan ng mga developer ang anumang pagkawala ng datos."
                ),
                "faqs": [
                    ("Paano mag-save ng mga tala?", "Pumunta sa 'My Notes', ilagay ang iyong Paksa at Paksa (Subject/Topic), pagkatapos ay i-click ang 'Save Note' o 'Save Text Note Only'."),
                    ("Paano gumagana ang Quiz Generator?", "Awtomatikong kumukuha ang AI quiz generator mula sa iyong mga nakasaved na tala bawat paksa upang bumuo ng mga pagsusulit."),
                    ("Paano ko masusubaybayan ang oras ng pag-aaral?", "Gamitin ang interactive na kalendaryo sa Schedule upang magplano ng mga deadline at suriin ang katayuan ng gawain."),
                    ("Maaari ko bang palitan ang aking password?", "Oo! Pumunta sa Profile workspace gamit ang top header o settings upang i-update ang iyong mga kredensyal.")
                ]
            }
        }

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # =============================================================
        # LEFT PANEL: APPEARANCE, THEME, LANGUAGE & FONT SIZE SETTINGS
        # =============================================================
        self.appearance_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=("white", "#1E1E1E"))
        self.appearance_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.lbl_appearance_title = ctk.CTkLabel(
            self.appearance_frame, 
            text=self.get_text("title_appearance"), 
            font=("Poppins", 16, "bold"), 
            text_color=("gray10", "#FFFFFF")
        )
        self.lbl_appearance_title.pack(anchor="w", padx=20, pady=(15, 15))

        # 1. Theme Appearance Mode (Dark / Light / System)
        self.lbl_theme_title = ctk.CTkLabel(
            self.appearance_frame, 
            text=self.get_text("lbl_theme"), 
            font=("Poppins", 12, "bold"), 
            text_color=("gray10", "#FFFFFF")
        )
        self.lbl_theme_title.pack(anchor="w", padx=20, pady=(5, 2))
        
        self.combo_theme = ctk.CTkOptionMenu(
            self.appearance_frame,
            values=["Dark", "Light", "System"],
            command=self.change_appearance_mode,
            height=35,
            fg_color=("gray85", "#2B2B3D"),
            button_color="#3B82F6",
            text_color=("gray10", "#FFFFFF")
        )
        self.combo_theme.set("Light")
        self.combo_theme.pack(fill="x", padx=20, pady=(0, 15))

        # 2. Language Feature Dropdown (English / Filipino)
        self.lbl_lang_title = ctk.CTkLabel(
            self.appearance_frame, 
            text=self.get_text("lbl_lang"), 
            font=("Poppins", 12, "bold"), 
            text_color=("gray10", "#FFFFFF")
        )
        self.lbl_lang_title.pack(anchor="w", padx=20, pady=(5, 2))

        active_lang = getattr(self.controller, "current_language", "English")
        self.combo_language = ctk.CTkOptionMenu(
            self.appearance_frame,
            values=["English", "Filipino"],
            command=self.change_language,
            height=35,
            fg_color=("gray85", "#2B2B3D"),
            button_color="#8B5CF6",
            text_color=("gray10", "#FFFFFF")
        )
        self.combo_language.set(active_lang)
        self.combo_language.pack(fill="x", padx=20, pady=(0, 15))

        # 3. Font Size / UI Scaling Modifier
        self.lbl_scale_title = ctk.CTkLabel(
            self.appearance_frame, 
            text=self.get_text("lbl_scale"), 
            font=("Poppins", 12, "bold"), 
            text_color=("gray10", "#FFFFFF")
        )
        self.lbl_scale_title.pack(anchor="w", padx=20, pady=(5, 2))
        
        self.combo_scaling = ctk.CTkOptionMenu(
            self.appearance_frame,
            values=["Small (90%)", "Normal (100%)", "Large (110%)", "Extra Large (120%)"],
            command=self.change_ui_scaling,
            height=35,
            fg_color=("gray85", "#2B2B3D"),
            button_color="#10B981",
            text_color=("gray10", "#FFFFFF")
        )
        self.combo_scaling.set("Normal (100%)")
        self.combo_scaling.pack(fill="x", padx=20, pady=(0, 20))

        # Divider line
        ctk.CTkFrame(self.appearance_frame, height=2, fg_color=("gray80", "#2B2B3D")).pack(fill="x", padx=20, pady=10)

        # =============================================================
        # RIGHT PANEL: ABOUT, HELP / FAQ & TERMS TABS
        # =============================================================
        self.info_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=("white", "#1E1E1E"))
        self.info_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.info_tabview = ctk.CTkTabview(
            self.info_frame, 
            fg_color=("gray90", "#2B2B3D"), 
            segmented_button_fg_color=("gray80", "#1E1E2E"),
            text_color=("gray10", "#FFFFFF")
        )
        self.info_tabview.pack(fill="both", expand=True, padx=15, pady=15)

        # Initialize Tabs using translation keys
        self.tab_names = ["tab_about", "tab_help", "tab_terms"]
        for key in self.tab_names:
            self.info_tabview.add(self.get_text(key))

        # --- ABOUT TAB CONTENT ---
        self.about_scroll = ctk.CTkScrollableFrame(self.info_tabview.tab(self.get_text("tab_about")), fg_color=("gray95", "#1E1E2E"))
        self.about_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        self.lbl_about_header = ctk.CTkLabel(
            self.about_scroll, 
            text=self.get_text("about_ver"), 
            font=("Poppins", 16, "bold"), 
            text_color=("#2563EB", "#60A5FA")
        )
        self.lbl_about_header.pack(anchor="w", padx=10, pady=(10, 5))

        self.lbl_about_body = ctk.CTkLabel(
            self.about_scroll, 
            text=self.get_text("about_desc"), 
            font=("Poppins", 13), 
            text_color=("gray20", "#D1D5DB"), 
            justify="left", 
            wraplength=320
        )
        self.lbl_about_body.pack(anchor="w", padx=10, pady=5)

        # --- HELP & FAQ TAB CONTENT ---
        self.help_scroll = ctk.CTkScrollableFrame(self.info_tabview.tab(self.get_text("tab_help")), fg_color=("gray95", "#1E1E2E"))
        self.help_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        self.populate_faqs()

        # --- TERMS & CONDITIONS TAB CONTENT ---
        self.terms_scroll = ctk.CTkScrollableFrame(self.info_tabview.tab(self.get_text("tab_terms")), fg_color=("gray95", "#1E1E2E"))
        self.terms_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        self.lbl_terms_header = ctk.CTkLabel(
            self.terms_scroll, 
            text=self.get_text("terms_title"), 
            font=("Poppins", 16, "bold"), 
            text_color=("#059669", "#10B981")
        )
        self.lbl_terms_header.pack(anchor="w", padx=10, pady=(10, 5))

        self.lbl_terms_body = ctk.CTkLabel(
            self.terms_scroll, 
            text=self.get_text("terms_desc"), 
            font=("Poppins", 13), 
            text_color=("gray20", "#D1D5DB"), 
            justify="left", 
            wraplength=320
        )
        self.lbl_terms_body.pack(anchor="w", padx=10, pady=5)

    def get_text(self, key: str) -> str:
        """Retrieves localized text based on the active language from the controller."""
        lang = getattr(self.controller, "current_language", "English")
        return self.translations.get(lang, self.translations["English"]).get(key, key)

    def populate_faqs(self):
        """Populates FAQ items based on selected language."""
        for widget in self.help_scroll.winfo_children():
            widget.destroy()

        faqs = self.get_text("faqs")
        for q, a in faqs:
            q_box = ctk.CTkFrame(self.help_scroll, fg_color=("white", "#1E1E2E"), corner_radius=6)
            q_box.pack(fill="x", pady=4, padx=2)
            ctk.CTkLabel(q_box, text=f"❓ {q}", font=("Poppins", 11, "bold"), text_color=("#059669", "#10B981")).pack(anchor="w", padx=8, pady=(6, 2))
            ctk.CTkLabel(q_box, text=a, font=("Poppins", 10), text_color=("gray30", "#AAAAAA"), justify="left", wraplength=300).pack(anchor="w", padx=8, pady=(0, 6))

    # =============================================================
    # EVENT HANDLERS
    # =============================================================

    def change_appearance_mode(self, new_mode: str):
        """Switches standard application appearance mode (Dark, Light, System)."""
        if new_mode in ["Dark", "Light", "System"]:
            ctk.set_appearance_mode(new_mode)

    def change_language(self, lang: str):
        """Notifies the controller to change the global language and refreshes UI."""
        if hasattr(self.controller, "set_global_language"):
            self.controller.set_global_language(lang)
        self.refresh_ui_texts()

    def refresh_ui_texts(self):
        """Updates all visible labels, headers, and tabs when language changes."""
        self.lbl_appearance_title.configure(text=self.get_text("title_appearance"))
        self.lbl_theme_title.configure(text=self.get_text("lbl_theme"))
        self.lbl_lang_title.configure(text=self.get_text("lbl_lang"))
        self.lbl_scale_title.configure(text=self.get_text("lbl_scale"))

        # Safely re-initialize or map tab view names cleanly for CTkTabview translation support
        try:
            current_tabs = list(self.info_tabview._tab_dict.keys())
            for old_tab in current_tabs:
                self.info_tabview._segmented_button.delete(old_tab)
                del self.info_tabview._tab_dict[old_tab]
            
            # Re-add translated tab names
            for key in self.tab_names:
                self.info_tabview.add(self.get_text(key))
            
            # Re-pack or re-assign contents to the corresponding tabs
            self.about_scroll.pack_forget()
            self.about_scroll = ctk.CTkScrollableFrame(self.info_tabview.tab(self.get_text("tab_about")), fg_color=("gray95", "#1E1E2E"))
            self.about_scroll.pack(fill="both", expand=True, padx=5, pady=5)
            self.lbl_about_header.pack_forget()
            self.lbl_about_header = ctk.CTkLabel(self.about_scroll, text=self.get_text("about_ver"), font=("Poppins", 16, "bold"), text_color=("#2563EB", "#60A5FA"))
            self.lbl_about_header.pack(anchor="w", padx=10, pady=(10, 5))
            self.lbl_about_body.pack_forget()
            self.lbl_about_body = ctk.CTkLabel(self.about_scroll, text=self.get_text("about_desc"), font=("Poppins", 13), text_color=("gray20", "#D1D5DB"), justify="left", wraplength=320)
            self.lbl_about_body.pack(anchor="w", padx=10, pady=5)

            self.help_scroll.pack_forget()
            self.help_scroll = ctk.CTkScrollableFrame(self.info_tabview.tab(self.get_text("tab_help")), fg_color=("gray95", "#1E1E2E"))
            self.help_scroll.pack(fill="both", expand=True, padx=5, pady=5)
            self.populate_faqs()

            self.terms_scroll.pack_forget()
            self.terms_scroll = ctk.CTkScrollableFrame(self.info_tabview.tab(self.get_text("tab_terms")), fg_color=("gray95", "#1E1E2E"))
            self.terms_scroll.pack(fill="both", expand=True, padx=5, pady=5)
            self.lbl_terms_header.pack_forget()
            self.lbl_terms_header = ctk.CTkLabel(self.terms_scroll, text=self.get_text("terms_title"), font=("Poppins", 16, "bold"), text_color=("#059669", "#10B981"))
            self.lbl_terms_header.pack(anchor="w", padx=10, pady=(10, 5))
            self.lbl_terms_body.pack_forget()
            self.lbl_terms_body = ctk.CTkLabel(self.terms_scroll, text=self.get_text("terms_desc"), font=("Poppins", 13), text_color=("gray20", "#D1D5DB"), justify="left", wraplength=320)
            self.lbl_terms_body.pack(anchor="w", padx=10, pady=5)
        except Exception as e:
            print(f"[SettingsView] Error updating tabs during language switch: {e}")

        self.lbl_about_header.configure(text=self.get_text("about_ver"))
        self.lbl_about_body.configure(text=self.get_text("about_desc"))
        self.lbl_terms_header.configure(text=self.get_text("terms_title"))
        self.lbl_terms_body.configure(text=self.get_text("terms_desc"))

    def change_ui_scaling(self, scale_str: str):
        """Changes global font and widget scaling size."""
        scaling_map = {
            "Small (90%)": 0.9,
            "Normal (100%)": 1.0,
            "Large (110%)": 1.1,
            "Extra Large (120%)": 1.2
        }
        scale_val = scaling_map.get(scale_str, 1.0)
        ctk.set_widget_scaling(scale_val)

    def on_show(self):
        """Lifecycle method when switching to Settings view."""
        active_lang = getattr(self.controller, "current_language", "English")
        self.combo_language.set(active_lang)
        self.refresh_ui_texts()