import calendar
import time

class Schedule:
    def __init__(self, year, month):
        self.year = year
        self.month = month
        self.days_in_month = calendar.monthrange(year, month)[1]
        self.schedule = {day: [] for day in range(1, self.days_in_month + 1)}

    def add_task(self, day, task):
        if 1 <= day <= self.days_in_month:
            self.schedule[day].append(task)
        else:
            raise ValueError(f"Day must be between 1 and {self.days_in_month}")

    def remove_task(self, day, task):
        if 1 <= day <= self.days_in_month:
            if task in self.schedule[day]:
                self.schedule[day].remove(task)
            else:
                raise ValueError(f"Task '{task}' not found on day {day}")
        else:
            raise ValueError(f"Day must be between 1 and {self.days_in_month}")

    def check_tasks(self, day):
        if 1 <= day <= self.days_in_month:
            return self.schedule[day]
        else:
            raise ValueError(f"Day must be between 1 and {self.days_in_month}")