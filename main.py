import json
import os
import platform
import time
import requests
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font
import sv_ttk
import random  # Добавлен импорт модуля random

class LessonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Math Lessons")
        self.root.geometry("900x650")
        self.root.minsize(700, 500)
        
        sv_ttk.set_theme("light")
        self.init_styles()
        
        self.system_lessons_path = self.get_system_lessons_path()
        self.lessons = []
        self.current_lesson = None
        self.answers = []
        self.start_time = 0
        self.selected_tasks = []  # Для хранения выбранных случайных вопросов
        
        self.load_lessons()
        self.create_main_menu()
    
    def init_styles(self):
        self.title_font = Font(family="Segoe UI", size=24, weight="bold")
        self.lesson_font = Font(family="Segoe UI", size=12)
        self.countdown_font = Font(family="Segoe UI", size=72, weight="bold")
        self.task_font = Font(family="Segoe UI", size=36)
        self.result_font = Font(family="Segoe UI", size=18)
        
        style = ttk.Style()
        style.configure('Large.TButton', font=('Segoe UI', 12))
        style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('TFrame', background='#f3f3f3')
        style.configure('TLabel', background='#f3f3f3')
    
    def get_system_lessons_path(self):
        system = platform.system()
        if system == "Windows":
            appdata = os.getenv('LOCALAPPDATA') or os.path.expanduser('~\\AppData\\Local')
            dir_path = os.path.join(appdata, "MathLessons")
        else:
            dir_path = os.path.join(os.path.expanduser("~"), ".config", "mathlessons")
        os.makedirs(dir_path, exist_ok=True)
        return os.path.join(dir_path, "lessons.json")
    
    def download_lessons_from_github(self):
        url = "https://raw.githubusercontent.com/Tianodont/beeholder/main/lessons.json"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            with open(self.system_lessons_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            return response.json()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить уроки с GitHub:\n{str(e)}")
            return None
    
    def load_lessons(self):
        try:
            if os.path.exists(self.system_lessons_path):
                with open(self.system_lessons_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.lessons = data.get('lessons', [])
            else:
                data = self.download_lessons_from_github()
                if data:
                    self.lessons = data.get('lessons', [])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке уроков:\n{str(e)}")
            self.lessons = []
    
    def refresh_lessons(self):
        data = self.download_lessons_from_github()
        if data:
            self.lessons = data.get('lessons', [])
            self.create_main_menu()
    
    def prepare_random_tasks(self, lesson):
        """Выбирает случайные вопросы (максимум 40)"""
        tasks = list(lesson['tasks'].items())
        if len(tasks) > 40:
            self.selected_tasks = random.sample(tasks, 40)
        else:
            self.selected_tasks = tasks.copy()
        random.shuffle(self.selected_tasks)  # Перемешиваем вопросы
    
    def create_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        ttk.Label(main_frame, text="Math Lessons", font=self.title_font).pack(pady=(0, 20))
        
        refresh_btn = ttk.Button(
            main_frame, 
            text="Обновить уроки", 
            command=self.refresh_lessons,
            style='Accent.TButton'
        )
        refresh_btn.pack(pady=10, ipadx=10, ipady=5)
        
        lessons_frame = ttk.Frame(main_frame)
        lessons_frame.pack(expand=True, fill=tk.BOTH, pady=10)
        
        if not self.lessons:
            ttk.Label(lessons_frame, text="Нет доступных уроков").pack()
            return
        
        for lesson in self.lessons:
            lesson_btn = ttk.Button(
                lessons_frame, 
                text=f"{lesson['name']} ({lesson['tasknum']} заданий)", 
                command=lambda l=lesson: self.start_lesson(l),
                style='Large.TButton'
            )
            lesson_btn.pack(fill=tk.X, pady=5, ipady=8)
    
    def start_lesson(self, lesson):
        self.current_lesson = lesson
        self.answers = []
        self.prepare_random_tasks(lesson)  # Подготавливаем случайные вопросы
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        countdown_frame = ttk.Frame(self.root)
        countdown_frame.pack(expand=True, fill=tk.BOTH)
        
        for i in range(3, 0, -1):
            countdown_label = ttk.Label(
                countdown_frame, 
                text=str(i), 
                font=self.countdown_font,
                anchor='center'
            )
            countdown_label.pack(expand=True, fill=tk.BOTH)
            self.root.update()
            time.sleep(1)
            countdown_label.destroy()
        
        self.start_time = time.time()
        self.show_next_task(0)
    
    def show_next_task(self, task_index):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        if task_index >= len(self.selected_tasks):
            self.finish_lesson()
            return
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=40, pady=20)
        
        progress = (task_index + 1) / len(self.selected_tasks) * 100
        progress_bar = ttk.Progressbar(
            main_frame, 
            orient=tk.HORIZONTAL, 
            length=100, 
            mode='determinate', 
            value=progress
        )
        progress_bar.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(
            main_frame, 
            text=f"Задание {task_index + 1} из {len(self.selected_tasks)}",
            font=self.lesson_font
        ).pack(pady=(0, 20))
        
        question, answer = self.selected_tasks[task_index]
        
        ttk.Label(
            main_frame, 
            text=question, 
            font=self.task_font,
            anchor='center'
        ).pack(expand=True, pady=20)
        
        entry_frame = ttk.Frame(main_frame)
        entry_frame.pack(fill=tk.X, pady=20)
        
        entry = ttk.Entry(
            entry_frame, 
            font=self.task_font,
            justify='center'
        )
        entry.pack(fill=tk.X, ipady=10)
        entry.focus()
        entry.bind('<Return>', lambda e: self.save_answer_and_continue(entry.get(), answer, task_index))
        
        next_btn = ttk.Button(
            main_frame, 
            text="Далее", 
            command=lambda: self.save_answer_and_continue(entry.get(), answer, task_index),
            style='Accent.TButton'
        )
        next_btn.pack(ipady=8, ipadx=20, pady=10)
    
    def save_answer_and_continue(self, user_answer, correct_answer, task_index):
        self.answers.append(user_answer == correct_answer)
        self.show_next_task(task_index + 1)
    
    def finish_lesson(self):
        end_time = time.time()
        time_spent = end_time - self.start_time
        minutes = int(time_spent // 60)
        seconds = int(time_spent % 60)
        correct_answers = sum(self.answers)
        total_questions = len(self.answers)
        percentage = (correct_answers / total_questions) * 100
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=40, pady=40)
        
        ttk.Label(
            main_frame, 
            text="Урок завершен!", 
            font=self.title_font
        ).pack(pady=(0, 30))
        
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(
            results_frame, 
            text=f"Правильных ответов: {correct_answers} из {total_questions}",
            font=self.result_font
        ).pack(pady=10)
        
        ttk.Label(
            results_frame, 
            text=f"Процент правильных: {percentage:.1f}%",
            font=self.result_font
        ).pack(pady=10)
        
        ttk.Label(
            results_frame, 
            text=f"Затраченное время: {minutes:02d}:{seconds:02d}",
            font=self.result_font
        ).pack(pady=10)
        
        return_btn = ttk.Button(
            main_frame, 
            text="Вернуться в меню", 
            command=self.create_main_menu,
            style='Accent.TButton'
        )
        return_btn.pack(ipady=8, ipadx=30, pady=30)

if __name__ == "__main__":
    root = tk.Tk()
    app = LessonApp(root)
    root.mainloop()
