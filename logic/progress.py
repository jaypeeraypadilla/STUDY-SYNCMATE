class ProgressUpdate:
    def __init__(self, progress: float, message: str = "", number_of_notes: int = 0):
        self.progress = progress
        self.message = message
        self.number_of_notes = number_of_notes

    def __str__(self):
        return f"Progress: {self.progress*100:.2f}%, Message: {self.message}, Notes: {self.number_of_notes}"

    def quiz_score(self, score: float):
        self.progress = score
        self.message = f"Quiz completed with score: {score*100:.2f}%"

    def task_completion(self, completed: bool):
        if completed:
            self.progress = 1.0
            self.message = "Task completed successfully."
        else:
            self.progress = 0.0
            self.message = "Task not completed."

    def noteList_number(self, number: int):
        self.number_of_notes = number
        self.message = f"Number of notes updated to: {number}"