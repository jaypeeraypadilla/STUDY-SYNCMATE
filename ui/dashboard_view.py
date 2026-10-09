import tkinter as tk


class DashboardView(tk.Frame):

  def __init__(self, parent, controller):
    super().__init__(parent, bg="#1E1E1E")
    self.controller = controller

    # Grid configuration: Row 0 (Top Bar), Row 1 (Main Workspace)
    self.grid_columnconfigure(1, weight=1)
    self.grid_rowconfigure(1, weight=1)

    # =============================================================
    # 1. TOP NAVBAR / HEADER
    # =============================================================
    self.header_frame = tk.Frame(self, height=60, bg="#1E1E2E")
    self.header_frame.grid(
        row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5)
    )
    self.header_frame.pack_propagate(False)

    # Dynamic Welcome Label
    self.welcome_label = tk.Label(
        self.header_frame,
        text="Welcome to Study SyncMate",
        font=("Poppins", 18, "bold"),
        bg="#1E1E2E",
        fg="#FFFFFF",
    )
    self.welcome_label.pack(side="left", padx=20)

    # Header Action Buttons
    self.btn_logout = tk.Button(
        self.header_frame,
        text="Logout",
        font=("Poppins", 11, "bold"),
        bg="#8B0000",
        fg="#FFFFFF",
        activebackground="#550000",
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        width=8,
        command=self.handle_logout,
    )
    self.btn_logout.pack(side="right", padx=(5, 15), ipady=3)

    self.btn_profile = tk.Button(
        self.header_frame,
        text="Profile",
        font=("Poppins", 11, "bold"),
        bg="#000080",
        fg="#FFFFFF",
        activebackground="#000055",
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        width=8,
        command=self.open_profile,
    )
    self.btn_profile.pack(side="right", padx=5, ipady=3)

    # =============================================================
    # 2. LEFT SIDEBAR NAVIGATION
    # =============================================================
    self.sidebar_frame = tk.Frame(self, width=180, bg="#2B2B2B")
    self.sidebar_frame.grid(
        row=1, column=0, sticky="nsew", padx=(10, 5), pady=5
    )
    self.sidebar_frame.pack_propagate(False)

    tk.Label(
        self.sidebar_frame,
        text="NAVIGATION",
        font=("Poppins", 11, "bold"),
        bg="#2B2B2B",
        fg="#AAAAAA",
    ).pack(anchor="w", padx=15, pady=(15, 10))

    # Navigation Links
    nav_buttons = [
        ("Home", self.nav_home),
        ("My Notes", self.nav_notes),
        ("Quizzes", self.nav_quizzes),
        ("Schedule", self.nav_schedule),
        ("Progress", self.nav_progress),
    ]

    for text, command_fn in nav_buttons:
      btn = tk.Button(
          self.sidebar_frame,
          text=f"  {text}",
          font=("Poppins", 12),
          anchor="w",
          bg="#2B2B2B",
          fg="#FFFFFF",
          activebackground="#3A3A3A",
          activeforeground="#FFFFFF",
          relief="flat",
          bd=0,
          cursor="hand2",
          command=command_fn,
      )
      btn.pack(fill="x", padx=8, pady=3, ipady=4)

      # Optional: Add hover highlights for navigation buttons
      btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#3A3A3A"))
      btn.bind("<Leave>", lambda e, b=btn: b.configure(bg="#2B2B2B"))

    # =============================================================
    # 3. MAIN WORKSPACE CONTENT AREA
    # =============================================================
    self.main_content = tk.Frame(self, bg="#1E1E1E")
    self.main_content.grid(
        row=1, column=1, sticky="nsew", padx=(5, 10), pady=5
    )

    self.content_title = tk.Label(
        self.main_content,
        text="Dashboard Overview",
        font=("Poppins", 20, "bold"),
        bg="#1E1E1E",
        fg="#FFFFFF",
    )
    self.content_title.pack(anchor="nw", padx=25, pady=20)

    # Quick Stats Cards Grid
    self.stats_container = tk.Frame(self.main_content, bg="#1E1E1E")
    self.stats_container.pack(fill="x", padx=20, pady=10)

    self._create_stat_card(
        self.stats_container, "Total Notes", "12 Notes", "#4A90E2"
    )
    self._create_stat_card(
        self.stats_container, "Upcoming Tasks", "5 Pending", "#4CAF50"
    )
    self._create_stat_card(
        self.stats_container, "Quiz Score Avg.", "92%", "#E57373"
    )

  def _create_stat_card(self, parent, title, value, color):
    card = tk.Frame(parent, width=170, height=90, bg="#2B2B2B")
    card.pack(side="left", padx=8, expand=True, fill="x")
    card.pack_propagate(False)

    tk.Label(
        card,
        text=title,
        font=("Poppins", 11),
        bg="#2B2B2B",
        fg="#AAAAAA",
    ).pack(anchor="w", padx=12, pady=(12, 2))

    tk.Label(
        card,
        text=value,
        font=("Poppins", 18, "bold"),
        bg="#2B2B2B",
        fg=color,
    ).pack(anchor="w", padx=12)

  # =============================================================
  # CONTROLLER INTERACTION & LIFECYCLE
  # =============================================================
  def on_show(self):
    """Runs automatically when switching to DashboardView."""
    if hasattr(self.controller, "current_user") and self.controller.current_user:
      user = self.controller.current_user
      name = user.get("full_name", "Student")
      course = user.get("course", "")
      year = user.get("year_level", "")

      sub_info = f" ({course} - {year})" if course else ""
      self.welcome_label.configure(text=f"Welcome back, {name}{sub_info}!")

  def handle_logout(self):
    self.controller.logout()

  def open_profile(self):
    print("Opening user profile...")

  def nav_home(self):
    self.content_title.configure(text="Dashboard Overview")

  def nav_notes(self):
    self.content_title.configure(text="My Notes Workspace")

  def nav_quizzes(self):
    self.content_title.configure(text="Quizzes & Flashcards")

  def nav_schedule(self):
    self.content_title.configure(text="Study Schedule & Planner")

  def nav_progress(self):
    self.content_title.configure(text="Academic Progress Analytics")