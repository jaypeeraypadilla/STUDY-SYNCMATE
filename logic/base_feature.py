class FeatureResult:
    def __init__(self, success: bool , message: str = "", data: dict = None):
        self.success = success
        self.message = message
        self.data = data if data is not None else {}

    def __repr__(self):
        return f"<FeatureResult success={self.success} message'{self.message}'>"

class BaseFeatureManager:
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
