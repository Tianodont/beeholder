import json
import time
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font
import threading
import sv_ttk  # Стиль Windows 11

class LessonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Math Lessons")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Настройка стиля Windows 11
        sv_ttk.set_theme("light")
        
        self.lessons = []
        self.current_lesson = None
        self.answers = []
        self.start_time = 0
        
        # Шрифты
        self.title_font = Font(family="Segoe UI", size=24, weight="bold")
        self.lesson_font = Font(family="Segoe UI", size=12)
        self.countdown_font = Font(family="Segoe UI", size=72, weight="bold")
        self.task_font = Font(family="Segoe UI", size=36)
        self.result_font = Font(family="Segoe UI", size=18)
        
        self.load_lessons()
        self.create_main_menu()
    
    def load_lessons(self):
        try:
            with open('lessons.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.lessons = data.get('lessons', [])
        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Файл lessons.json не найден")
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка", "Ошибка при чтении файла lessons.json")
    
    def refresh_lessons(self):
        self.load_lessons()
        self.create_main_menu()
    
    def create_main_menu(self):
        # Очищаем текущее содержимое
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Главный фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Заголовок
        ttk.Label(main_frame, text="Math Lessons", font=self.title_font).pack(pady=(0, 20))
        
        # Кнопка обновления
        refresh_btn = ttk.Button(
            main_frame, 
            text="Обновить уроки", 
            command=self.refresh_lessons,
            style='Accent.TButton'
        )
        refresh_btn.pack(pady=10, ipadx=10, ipady=5)
        
        # Фрейм для списка уроков
        lessons_frame = ttk.Frame(main_frame)
        lessons_frame.pack(expand=True, fill=tk.BOTH, pady=10)
        
        # Список уроков
        if not self.lessons:
            ttk.Label(lessons_frame, text="Нет доступных уроков").pack()
            return
        
        for i, lesson in enumerate(self.lessons):
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
        
        # Очищаем текущее содержимое
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Фрейм для обратного отсчета
        countdown_frame = ttk.Frame(self.root)
        countdown_frame.pack(expand=True, fill=tk.BOTH)
        
        # Обратный отсчет
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
        # Очищаем текущее содержимое
        for widget in self.root.winfo_children():
            widget.destroy()
        
        if task_index >= len(self.current_lesson['tasks']):
            self.finish_lesson()
            return
        
        # Главный фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=40, pady=20)
        
        # Прогресс бар
        progress = (task_index + 1) / len(self.current_lesson['tasks']) * 100
        progress_bar = ttk.Progressbar(
            main_frame, 
            orient=tk.HORIZONTAL, 
            length=100, 
            mode='determinate', 
            value=progress
        )
        progress_bar.pack(fill=tk.X, pady=(0, 20))
        
        # Номер задания
        ttk.Label(
            main_frame, 
            text=f"Задание {task_index + 1} из {len(self.current_lesson['tasks'])}",
            font=self.lesson_font
        ).pack(pady=(0, 20))
        
        # Получаем текущее задание
        task = list(self.current_lesson['tasks'].items())[task_index]
        question, answer = task
        
        # Вопрос
        ttk.Label(
            main_frame, 
            text=question, 
            font=self.task_font,
            anchor='center'
        ).pack(expand=True, pady=20)
        
        # Поле ввода
        entry_frame = ttk.Frame(main_frame)
        entry_frame.pack(fill=tk.X, pady=20)
        
        entry = ttk.Entry(
            entry_frame, 
            font=self.task_font,
            justify='center'
        )
        entry.pack(fill=tk.X, ipady=10)
        entry.focus()
        
        # Обработка нажатия Enter
        entry.bind('<Return>', lambda e: self.save_answer_and_continue(entry.get(), answer, task_index))
        
        # Кнопка далее
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
        
        # Очищаем текущее содержимое
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Главный фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=40, pady=40)
        
        # Заголовок
        ttk.Label(
            main_frame, 
            text="Урок завершен!", 
            font=self.title_font
        ).pack(pady=(0, 30))
        
        # Результаты
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
        
        # Кнопка возврата
        return_btn = ttk.Button(
            main_frame, 
            text="Вернуться в меню", 
            command=self.create_main_menu,
            style='Accent.TButton'
        )
        return_btn.pack(ipady=8, ipadx=30, pady=30)

if __name__ == "__main__":
    root = tk.Tk()
    
    # Настройка стиля для больших кнопок
    style = ttk.Style()
    style.configure('Large.TButton', font=('Segoe UI', 12))
    style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'))
    
    app = LessonApp(root)
    root.mainloop()
