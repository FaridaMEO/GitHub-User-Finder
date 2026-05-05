import tkinter as tk
from tkinter import messagebox, ttk
import requests
import json
import os

# Конфигурация
GITHUB_API_URL = "https://api.github.com/users/"
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
        # Поле ввода
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=10, padx=20, fill="x")

        ttk.Label(input_frame, text="GitHub Username:").pack(side="left")
        self.search_entry = ttk.Entry(input_frame, width=40)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search_user())

        search_btn = ttk.Button(input_frame, text="Search", command=self.search_user)
        search_btn.pack(side="left")

        # Кнопки управления избранным
        favorites_frame = ttk.Frame(self.root)
        favorites_frame.pack(pady=5, padx=20, fill="x")

        add_btn = ttk.Button(favorites_frame, text="Add to Favorites", command=self.add_to_favorites)
        add_btn.pack(side="left", padx=5)

        remove_btn = ttk.Button(favorites_frame, text="Remove from Favorites", command=self.remove_from_favorites)
        remove_btn.pack(side="left", padx=5)

        refresh_btn = ttk.Button(favorites_frame, text="Refresh Favorites", command=self.refresh_favorites)
        refresh_btn.pack(side="left", padx=5)

        # Область результатов
        result_frame = ttk.LabelFrame(self.root, text="Search Results")
        result_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.result_text = tk.Text(result_frame, height=10)
        self.result_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Список избранных
        favorites_frame_list = ttk.LabelFrame(self.root, text="Favorite Users")
        favorites_frame_list.pack(pady=10, padx=20, fill="both", expand=True)

        self.favorites_listbox = tk.Listbox(favorites_frame_list)
        self.favorites_listbox.pack(fill="both", expand=True, padx=5, pady=5)

        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken")
        status_bar.pack(side="bottom", fill="x")

        # Обновление списка избранного
        self.refresh_favorites()

    def search_user(self):
        username = self.search_entry.get().strip()

        if not username:
            messagebox.showerror("Error", "Search field cannot be empty!")
            return

        try:
            response = requests.get(f"{GITHUB_API_URL}{username}")

            if response.status_code == 200:
                user_data = response.json()
                self.display_user_info(user_data)
                self.status_var.set(f"User {username} found")
            else:
                messagebox.showerror("Error", f"User not found (Status: {response.status_code})")
                self.result_text.delete(1.0, tk.END)
                self.status_var.set("User not found")

        except requests.RequestException as e:
            messagebox.showerror("Error", f"Network error: {e}")
            self.status_var.set("Network error")

    def display_user_info(self, user_data):
        info = f"""
Name: {user_data.get('name', 'N/A')}
Username: {user_data['login']}
Location: {user_data.get('location', 'N/A')}
Public Repos: {user_data['public_repos']}
Followers: {user_data['followers']}
Following: {user_data['following']}
Bio: {user_data.get('bio', 'N/A')}
Profile URL: {user_data['html_url']}
        """
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, info)

    def add_to_favorites(self):
        username = self.search_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "No user to add!")
            return

        if username not in self.favorites:
            self.favorites.append(username)
            self.save_favorites()
            self.refresh_favorites()
            messagebox.showinfo("Success", f"{username} added to favorites!")
        else:
            messagebox.showwarning("Warning", f"{username} is already in favorites!")

    def remove_from_favorites(self):
        selection = self.favorites_listbox.curselection()
        if selection:
            username = self.favorites_listbox.get(selection[0])
            self.favorites.remove(username)
            self.save_favorites()
            self.refresh_favorites()
            messagebox.showinfo("Success", f"{username} removed from favorites!")

    def refresh_favorites(self):
        self.favorites_listbox.delete(0, tk.END)
        for user in self.favorites:
            self.favorites_listbox.insert(tk.END, user)

    def load_favorites(self):
        if os.path.exists(FAVORITES_FILE):
            try:
                with open(FAVORITES_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save_favorites(self):
        with open(FAVORITES_FILE, 'w') as f:
            json.dump(self.favorites, f, indent=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
