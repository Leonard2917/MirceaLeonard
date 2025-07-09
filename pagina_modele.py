import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox

BASE_URL = "https://www.auto-data.net"
URL = "https://www.auto-data.net/en/volkswagen-brand-80"  # înlocuiește după nevoie

try:
    response = requests.get(URL)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print("Eroare la cererea HTTP:", e)
    exit()

soup = BeautifulSoup(response.text, "html.parser")

outer_div = soup.find("div", id="outer")
modelite_ul = outer_div.find("ul", class_="modelite") if outer_div else None

models = []

if modelite_ul:
    # găsim toate linkurile <a> cu clasa "modeli" în interiorul acestui ul
    for a_tag in modelite_ul.find_all("a", class_="modeli"):
        model_name = a_tag.find("strong").text.strip() if a_tag.find("strong") else a_tag.text.strip()
        href = a_tag.get("href")
        models.append((model_name, BASE_URL + href))
else:
    print("Nu am găsit lista de modele.")

# GUI Tkinter
root = tk.Tk()
root.title("Modele Volkswagen")

listbox = tk.Listbox(root, width=50, height=30)
listbox.pack(padx=10, pady=10)

for model_name, _ in models:
    listbox.insert(tk.END, model_name)

def on_select(event):
    sel = listbox.curselection()
    if sel:
        idx = sel[0]
        model_name, url = models[idx]
        messagebox.showinfo("Model selectat", f"{model_name}\nURL: {url}")

listbox.bind("<<ListboxSelect>>", on_select)

root.mainloop()
