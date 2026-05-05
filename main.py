
import tkinter as tk
from tkinter import messagebox, ttk
import requests
import json
import os

# Константы
API_URL = "https://api.github.com/search/users"
FAVORITES_FILE = "favorites.json"

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("600x500")

        # Загрузка избранных пользователей
        self.favorites = self.load_favorites()

        self.setup_ui()

    def setup_ui(self):
        # Поле ввода для поиска
        tk.Label(self.root, text="Имя пользователя GitHub:").pack(pady=5)
        self.search_entry = tk.Entry(self.root, width=50)
        self.search_entry.pack(pady=5)

        # Кнопка поиска
        search_btn = tk.Button(
            self.root,
            text="Поиск",
            command=self.search_users
        )
        search_btn.pack(pady=5)

        # Список результатов поиска
        tk.Label(self.root, text="Результаты поиска:").pack(pady=5)
        columns = ("Login", "Name", "Location", "Public Repos")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=10)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        self.tree.pack(pady=5, padx=10, fill="both", expand=True)

        # Привязка события двойного клика
        self.tree.bind("<Double-1>", self.add_to_favorites)

        # Кнопка добавления в избранное
        fav_btn = tk.Button(
            self.root,
            text="Добавить в избранное",
            command=self.add_to_favorites
        )
        fav_btn.pack(pady=5)

        # Список избранных пользователей
        tk.Label(self.root, text="Избранные пользователи:").pack(pady=5)
        self.fav_listbox = tk.Listbox(self.root, height=6)
        self.fav_listbox.pack(pady=5, padx=10, fill="x")

        # Обновление списка избранных
        self.update_favorites_list()

    def search_users(self):
        query = self.search_entry.get().strip()

        if not query:
            messagebox.showerror("Ошибка", "Поле поиска не должно быть пустым!")
            return

        try:
            response = requests.get(API_URL, params={"q": query})
            response.raise_for_status()
            data = response.json()

            # Очистка предыдущего результата
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Заполнение таблицы результатами
            for user in data["items"][:10]:  # Ограничение до 10 результатов
                self.tree.insert("", "end", values=(
                    user["login"],
                    user.get("name", "N/A"),
                    user.get("location", "N/A"),
                    user["public_repos"]
                ))
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Ошибка при запросе к API: {e}")

    def add_to_favorites(self, event=None):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя из списка!")
            return

        item = selection[0]
        values = self.tree.item(item, "values")
        login = values[0]

        if login not in self.favorites:
            self.favorites[login] = {
                "name": values[1],
                "location": values[2],
                "public_repos": values[3]
            }
            self.save_favorites()
            self.update_favorites_list()
            messagebox.showinfo("Успех", f"{login} добавлен в избранное!")
        else:
            messagebox.showinfo("Информация", f"{login} уже в избранном!")

    def load_favorites(self):
        if os.path.exists(FAVORITES_FILE):
            try:
                with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def save_favorites(self):
        with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, indent=2, ensure_ascii=False)

    def update_favorites_list(self):
        self.fav_listbox.delete(0, tk.END)
        for login in self.favorites:
            self.fav_listbox.insert(tk.END, login)

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
