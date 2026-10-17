import os
import sys
import tkinter as tk

# Ensure proper relative import paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
  sys.path.insert(0, BASE_DIR)

from logic.user_auth import AuthManager
from ui.welcome_view import WelcomeView
from ui.login_view import LoginView
from ui.signup_view import SignUpView
from ui.recovery_ui import RecoveryView
from ui.dashboard_view import DashboardView


class StudySyncMateApp(tk.Tk):

  def __init__(self):
    super().__init__()

    self.title("Study SyncMate")
    self.geometry("800x650")
    self.minsize(720, 600)

    # Replicate CTk dark background in standard Tkinter
    self.configure(bg="#1E1E1E")

    # App Icon
    try:
      self.iconbitmap(os.path.join(BASE_DIR, "logo_dark.ico"))
    except Exception as e:
      print(f"Failed to load application icon: {e}")

    # Initialize Logic Backend & Global Settings State
    self.auth_manager = AuthManager()
    self.current_user = None
    self.current_language = "English"  # Default global language

    # Container Frame
    self.container = tk.Frame(self, bg="#1E1E1E")
    self.container.pack(fill="both", expand=True)

    self.container.grid_rowconfigure(0, weight=1)
    self.container.grid_columnconfigure(0, weight=1)

    self.frames = {}
    self.init_views()
    
    # Launch the Welcome Screen first!
    self.show_frame("WelcomeView")

  def init_views(self):
    """Instantiates all UI views."""
    for ViewClass in (WelcomeView, LoginView, SignUpView, RecoveryView):
      page_name = ViewClass.__name__
      frame = ViewClass(parent=self.container, controller=self)
      self.frames[page_name] = frame
      frame.grid(row=0, column=0, sticky="nsew")

  def show_frame(self, page_name: str):
    """Switches display frame instantly."""
    frame = self.frames.get(page_name)
    if frame:
      if hasattr(frame, "on_show"):
        frame.on_show()
      frame.tkraise()

  def set_active_user(self, user_data: dict):
    """Sets active user session and redirects to Dashboard."""
    self.current_user = user_data

    # Instantiate DashboardView dynamically if it hasn't been instantiated yet
    if "DashboardView" not in self.frames:
      frame = DashboardView(parent=self.container, controller=self)
      self.frames["DashboardView"] = frame
      frame.grid(row=0, column=0, sticky="nsew")

    self.show_frame("DashboardView")

  def set_global_language(self, lang: str):
    """Updates the global language and notifies all active views/sub-views to refresh."""
    if lang in ["English", "Filipino"]:
      self.current_language = lang
      
      # Broadcast language change to DashboardView and its sub-views if active
      dashboard = self.frames.get("DashboardView")
      if dashboard and hasattr(dashboard, "refresh_language"):
        dashboard.refresh_language()

  def logout(self):
    self.current_user = None
    # Returns to LoginView upon logout
    self.show_frame("LoginView")


if __name__ == "__main__":
  app = StudySyncMateApp()
  app.mainloop()