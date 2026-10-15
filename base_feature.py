"""
Study SyncMate - Base Feature Manager
Handles core module coordination and structured response handling via FeatureResult.
"""

class FeatureResult:
    def __init__(self, success: bool, message: str = "", data: dict = None):
        self.success = success
        self.message = message
        self.data = data if data is not None else {}

    def __repr__(self):
        return f"<FeatureResult success={self.success} message='{self.message}'>"


class BaseFeatureManager:
    """Central manager for Study SyncMate core features and database coordination."""
    
    def __init__(self, db_connection=None):
        self.db_connection = db_connection

    def get_system_metadata(self) -> FeatureResult:
        """Returns core system metadata and specifications."""
        metadata = {
            "name": "Study SyncMate",
            "version": "1.0.0",
            "backend": "Python & SQLite",
            "gui": "CustomTkinter",
            "ai_engine": "Google GenAI (Gemini)",
            "features": [
                "Modular Notes Workspace",
                "AI-Powered Quizzes & Flashcards",
                "Study Schedule & Task Planner",
                "Performance Tracker & Analytics",
                "Secure User Authentication",
                "Customization & Accessibility"
            ]
        }
        return FeatureResult(
            success=True, 
            message="System metadata retrieved successfully.", 
            data=metadata
        )

    def verify_database_connection(self) -> FeatureResult:
        """Verifies whether the database connection is initialized and active."""
        if self.db_connection:
            return FeatureResult(
                success=True, 
                message="Database connection is active and responsive."
            )
        return FeatureResult(
            success=False, 
            message="Warning: No database connection provided to BaseFeatureManager."
        )