#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import random
from datetime import datetime, date
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

DATA_FILE = "data.txt"
DATE_FORMAT = "%Y-%m-%d"  # نمایشی: YYYY-MM-DD


class Task:
    def __init__(self, id=None, is_done=False, priority=-1, created_date=None, due_date=None, title=""):
        self.id = id if id is not None else str(random.randint(1000, 9999))
        self.title = title
        self.is_done = is_done
        self.priority = priority
        self.created_date = created_date if created_date else datetime.now().strftime(DATE_FORMAT)
        self.due_date = due_date

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "is_done": self.is_done,
            "priority": self.priority,
            "created_date": self.created_date,
            "due_date": self.due_date,
        }

    @staticmethod
    def from_dict(d):
        return Task(
            id=d.get("id"),
            title=d.get("title", ""),
            is_done=d.get("is_done", False),
            priority=d.get("priority", -1),
            created_date=d.get("created_date"),
            due_date=d.get("due_date"),
        )

    def __str__(self):
        return f"{self.id}: {self.title} | {'انجام شد' if self.is_done else 'در انتظار'} | Pr={self.priority} | {self.created_date} | Due={self.due_date}"


class ToDoList:
    def __init__(self, file_path=DATA_FILE):
        self.tasks = []
        self.file_path = file_path
        self.load_from_file(file_path)

    def add_task(self, task: Task):
        self.tasks.append(task)
        self.save_to_file(self.file_path)

    def remove_task(self, task_id: str):
        self.tasks = [t for t in self.tasks if t.id != task_id]
        self.save_to_file(self.file_path)

    def update_task(self, task_id: str, **kwargs):
        for t in self.tasks:
            if t.id == task_id:
                for k, v in kwargs.items():
                    if hasattr(t, k):
                        setattr(t, k, v)
                break
        self.save_to_file(self.file_path)

    def list_tasks(self):
        return list(self.tasks)

    def list_by_date(self):
        return sorted(self.tasks, key=lambda t: t.created_date)

    def tasks_on_date(self, date_str: str):
        return [t for t in self.tasks if t.created_date == date_str]

    def tasks_due_on(self, date_str: str):
        return [t for t in self.tasks if t.due_date == date_str]

    def save_to_file(self, file_path: str):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump([t.to_dict() for t in self.tasks], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Error saving file:", e)

    def load_from_file(self, file_path: str):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.tasks = [Task.from_dict(item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            self.tasks = []


class ToDoGUI:
    def __init__(self, root):
        self.root = root

        # ---------------------------
        # GLOBAL FONT SIZE INCREASE
        # ---------------------------
        import tkinter.font as tkFont
        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(size=30)       # change 13 → bigger if needed
        root.option_add("*Font", default_font)
        # ---------------------------

        root.title("  main form of tasks:  ")
        root.geometry("900x600")

        self.todo = ToDoList()

        # بالا: نمایش تاریخ/زمان سیستم
        top_frame = ttk.Frame(root)
        top_frame.pack(fill=tk.X, padx=8, pady=6)
        self.time_label = ttk.Label(top_frame, text="")
        self.time_label.pack(side=tk.RIGHT)
        self.update_clock()

        # چپ: فرم افزودن/فیلتر
        left_frame = ttk.Frame(root)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=6)

        ttk.Label(left_frame, text="add new task", font=("Helvetica", 12, "bold")).pack(pady=4)
        ttk.Label(left_frame, text="title:").pack(anchor=tk.W)
        self.title_entry = ttk.Entry(left_frame, width=30)
        self.title_entry.pack(anchor=tk.W, pady=2)

        ttk.Label(left_frame, text="priority:").pack(anchor=tk.W)
        self.priority_entry = ttk.Entry(left_frame, width=10)
        self.priority_entry.pack(anchor=tk.W, pady=2)

        ttk.Label(left_frame, text="date (YYYY-MM-DD):").pack(anchor=tk.W)
        self.due_entry = ttk.Entry(left_frame, width=15)
        self.due_entry.pack(anchor=tk.W, pady=2)

        add_btn = ttk.Button(left_frame, text=" add task", command=self.on_add_task)
        add_btn.pack(fill=tk.X, pady=6)

        # فیلتر بر اساس اولویت
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)
        ttk.Label(left_frame, text="filter / sort", font=("Helvetica", 11)).pack(pady=2)
        ttk.Label(left_frame, text=" filter priority ≥").pack(anchor=tk.W)
        self.filter_priority_entry = ttk.Entry(left_frame, width=10)
        self.filter_priority_entry.pack(anchor=tk.W, pady=2)
        filter_btn = ttk.Button(left_frame, text="apply filter", command=self.on_filter_priority)
        filter_btn.pack(fill=tk.X, pady=2)
        clear_filter_btn = ttk.Button(left_frame, text="refresh", command=self.refresh_tree)
        clear_filter_btn.pack(fill=tk.X, pady=2)

        # نمایش فقط امروز
        today_btn = ttk.Button(left_frame, text="today's tasks", command=self.show_today_tasks)
        today_btn.pack(fill=tk.X, pady=6)

        # گزارش‌گیری: روز مشخص
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)
        ttk.Label(left_frame, text="get report", font=("Helvetica", 11)).pack(pady=2)
        ttk.Label(left_frame, text=" report date (YYYY-MM-DD):").pack(anchor=tk.W)
        self.report_date_entry = ttk.Entry(left_frame, width=15)
        self.report_date_entry.pack(anchor=tk.W, pady=2)
        report_btn = ttk.Button(left_frame, text="make report file", command=self.on_generate_report)
        report_btn.pack(fill=tk.X, pady=2)
        export_btn = ttk.Button(left_frame, text="export csv", command=self.export_csv)
        export_btn.pack(fill=tk.X, pady=4)

        # راست: جدول لیست کارها و دکمه‌های عملیاتی
        right_frame = ttk.Frame(root)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=6)
        style = ttk.Style()
        style.configure("Custom.Treeview", rowheight=50)
        columns = ("id", "title", "status", "priority", "created", "due")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings",style="Custom.Treeview", selectmode="browse")
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="title")
        self.tree.heading("status", text="status")
        self.tree.heading("priority", text="priority")
        self.tree.heading("created", text="created date")
        self.tree.heading("due", text="due")

        self.tree.column("id", width=70, anchor=tk.CENTER)
        self.tree.column("title", width=250)
        self.tree.column("status", width=90, anchor=tk.CENTER)
        self.tree.column("priority", width=80, anchor=tk.CENTER)
        self.tree.column("created", width=100, anchor=tk.CENTER)
        self.tree.column("due", width=100, anchor=tk.CENTER)

        vsb = ttk.Scrollbar(right_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # دکمه‌های پایین جدول
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill=tk.X, pady=6)
        del_btn = ttk.Button(btn_frame, text="delete", command=self.on_delete)
        del_btn.pack(side=tk.LEFT, padx=4)
        mark_done_btn = ttk.Button(btn_frame, text="toggle", command=self.on_toggle_done)
        mark_done_btn.pack(side=tk.LEFT, padx=4)
        edit_btn = ttk.Button(btn_frame, text="edit", command=self.on_edit)
        edit_btn.pack(side=tk.LEFT, padx=4)
        refresh_btn = ttk.Button(btn_frame, text="reload", command=self.on_reload)
        refresh_btn.pack(side=tk.LEFT, padx=4)

        # پایین: اطلاعات کمک
        bottom_frame = ttk.Frame(root)
        bottom_frame.pack(fill=tk.X, padx=8, pady=6)
        self.status_label = ttk.Label(bottom_frame, text="num of tasks:")
        self.status_label.pack(side=tk.LEFT)

        self.refresh_tree()

    # ----------------------------------------
    # متدهای رویداد/عمل
    # ----------------------------------------
    def update_clock(self):
        now = datetime.now()
        self.time_label.config(text=now.strftime("تاریخ و ساعت سیستم: %Y-%m-%d %H:%M:%S"))
        self.root.after(1000, self.update_clock)

    def on_add_task(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("خطا", "عنوان کار را وارد کنید.")
            return
        pr_text = self.priority_entry.get().strip()
        try:
            priority = int(pr_text) if pr_text else -1
        except ValueError:
            messagebox.showwarning("خطا", "اولویت باید یک عدد صحیح باشد.")
            return
        due = self.due_entry.get().strip() or None
        due_date = datetime.strptime(due, "%Y-%m-%d").date()
        today = datetime.today().date()

        if due:
            try:
                datetime.strptime(due, DATE_FORMAT)
            except ValueError:
                messagebox.showwarning("خطا", "فرمت موعد باید YYYY-MM-DD باشد.")
                return
            
        if due_date < today:
            messagebox.showerror("error", "due date should be in today or future days.")
            return 


        task = Task(title=title, priority=priority, due_date=due)
        self.todo.add_task(task)
        self.title_entry.delete(0, tk.END)
        self.priority_entry.delete(0, tk.END)
        self.due_entry.delete(0, tk.END)
        self.refresh_tree()
        messagebox.showinfo("موفق", f"کار جدید با ID={task.id} افزوده شد.")

    def on_delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("هشدار", "ابتدا یک کار انتخاب کنید.")
            return
        item = sel[0]
        task_id = self.tree.item(item, "values")[0]
        if messagebox.askyesno("تأیید حذف", f"آیا کار {task_id} حذف شود؟"):
            self.todo.remove_task(task_id)
            self.refresh_tree()

    def on_toggle_done(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("هشدار", "ابتدا یک کار انتخاب کنید.")
            return
        item = sel[0]
        vals = self.tree.item(item, "values")
        task_id = vals[0]
        # پیدا کردن و تغییر وضعیت
        t = next((x for x in self.todo.tasks if x.id == task_id), None)
        if t:
            t.is_done = not t.is_done
            self.todo.save_to_file(self.todo.file_path)
            self.refresh_tree()

    def on_edit(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("هشدار", "ابتدا یک کار انتخاب کنید.")
            return
        item = sel[0]
        vals = self.tree.item(item, "values")
        task_id = vals[0]
        t = next((x for x in self.todo.tasks if x.id == task_id), None)
        if not t:
            return

        # درخواست ورودی کاربر (عنوان، اولویت، موعد)
        new_title = simpledialog.askstring("ویرایش عنوان", "عنوان:", initialvalue=t.title)
        if new_title is None:
            return
        new_priority = simpledialog.askstring("ویرایش اولویت", "اولویت (عدد):", initialvalue=str(t.priority))
        if new_priority is None:
            return
        try:
            new_priority_val = int(new_priority)
        except ValueError:
            messagebox.showwarning("خطا", "اولویت باید عدد باشد.")
            return
        new_due = simpledialog.askstring("ویرایش موعد", "موعد (YYYY-MM-DD یا خالی):", initialvalue=(t.due_date or ""))
        if new_due:
            try:
                datetime.strptime(new_due, DATE_FORMAT)
            except ValueError:
                messagebox.showwarning("خطا", "فرمت موعد باید YYYY-MM-DD باشد.")
                return
        else:
            new_due = None

        self.todo.update_task(task_id, title=new_title, priority=new_priority_val, due_date=new_due)
        self.refresh_tree()

    def on_filter_priority(self):
        text = self.filter_priority_entry.get().strip()
        if not text:
            messagebox.showwarning("هشدار", "عدد اولویت را وارد کنید.")
            return
        try:
            threshold = int(text)
        except ValueError:
            messagebox.showwarning("خطا", "اولویت باید یک عدد صحیح باشد.")
            return
        filtered = [t for t in self.todo.tasks if t.priority >= threshold]
        self.load_into_tree(filtered)

    def on_generate_report(self):
        date_str = self.report_date_entry.get().strip()
        if not date_str:
            messagebox.showwarning("هشدار", "لطفاً یک تاریخ وارد کنید (YYYY-MM-DD).")
            return
        try:
            datetime.strptime(date_str, DATE_FORMAT)
        except ValueError:
            messagebox.showwarning("خطا", "فرمت تاریخ باید YYYY-MM-DD باشد.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt")],
                                                 initialfile=f"report_{date_str}.txt")
        if not save_path:
            return

        tasks_for_day = self.todo.tasks_on_date(date_str)
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(f"گزارش روزانه برای {date_str}\n")
                f.write("=" * 40 + "\n\n")
                if not tasks_for_day:
                    f.write("هیچ کاری در این تاریخ ایجاد نشده است.\n")
                else:
                    for t in tasks_for_day:
                        f.write(f"Task ID: {t.id}\n")
                        f.write(f"عنوان: {t.title}\n")
                        f.write(f"وضعیت: {'انجام شده' if t.is_done else 'در انتظار'}\n")
                        f.write(f"اولویت: {t.priority}\n")
                        f.write(f"ایجاد: {t.created_date}\n")
                        f.write(f"موعد: {t.due_date}\n")
                        f.write("-" * 30 + "\n")
            messagebox.showinfo("موفق", f"گزارش ساخته شد:\n{save_path}")
        except Exception as e:
            messagebox.showerror("خطا", f"نوشتن فایل گزارش با خطا مواجه شد:\n{e}")

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV files", "*.csv")],
                                            initialfile="tasks_export.csv")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("id,title,is_done,priority,created_date,due_date\n")
                for t in self.todo.tasks:
                    line = f'"{t.id}","{t.title}",{int(t.is_done)},{t.priority},"{t.created_date}","{t.due_date or ""}"\n'
                    f.write(line)
            messagebox.showinfo("موفق", f"CSV ذخیره شد:\n{path}")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ذخیره CSV:\n{e}")

    def show_today_tasks(self):
        today = date.today().strftime(DATE_FORMAT)
        todays = self.todo.tasks_on_date(today)
        self.load_into_tree(todays)

    def on_reload(self):
        self.todo.load_from_file(self.todo.file_path)
        self.refresh_tree()

    # ----------------------------------------
    # ابزارهای کمکی نمایش
    # ----------------------------------------
    def refresh_tree(self):
        self.load_into_tree(self.todo.tasks)

    def load_into_tree(self, tasks):
        # پاک کردن همه
        for i in self.tree.get_children():
            self.tree.delete(i)
        # درج
        for t in tasks:
            status = "done" if t.is_done else "pending"
            self.tree.insert("", tk.END, values=(t.id, t.title, status, t.priority, t.created_date, t.due_date or ""))
        self.status_label.config(text=f"num of tasks {len(self.todo.tasks)}")


def main():
    root = tk.Tk()
    app = ToDoGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()