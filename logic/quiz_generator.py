class QuizGenerator:
    def __init__(self, questions: list):
        self.questions = questions
        self.current_question_index = 0
        self.score = 0.0

    def get_next_question(self):
        if self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            self.current_question_index += 1
            return question
        else:
            return None

    def submit_answer(self, answer: str):
        if self.current_question_index == 0:
            raise ValueError("No question has been asked yet.")
        
        current_question = self.questions[self.current_question_index - 1]
        if answer.lower() == current_question['answer'].lower():
            self.score += 1.0
            return True
        else:
            return False