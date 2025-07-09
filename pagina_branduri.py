import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox

# URL-ul tău cu toate mărcile
URL = "https://www.auto-data.net/en/"

# 1. Descarcă pagina
response = requests.get(URL)
soup = BeautifulSoup(response.text, 'html.parser')

# 2. Caută div-ul cu clasa "markite"
markite_div = soup.find('div', class_='markite')

# 3. Găsește toate <a> din acel div
brand_links = markite_div.find_all('a')

# 4. Creează o listă cu toate mărcile și URL-urile
brands = [(a.text.strip(), a['href']) for a in brand_links]

# 5. Afișare grafică cu tkinter
def on_select(event):
    selected = listbox.curselection()
    if selected:
        name, url = brands[selected[0]]
        messagebox.showinfo("Marcă selectată", f"{name}\nLink: {url}")

root = tk.Tk()
root.title("Lista Mărci Auto")

listbox = tk.Listbox(root, width=40, height=20)
listbox.pack(padx=10, pady=10)

for brand_name, _ in brands:
    listbox.insert(tk.END, brand_name)

listbox.bind('<<ListboxSelect>>', on_select)

root.mainloop()
