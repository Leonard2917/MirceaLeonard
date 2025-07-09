import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox

def cauta_masini():
    lista.delete(0, tk.END)  # curăță lista anterioară

    cautare = entry.get().strip()
    if not cautare:
        messagebox.showwarning("Atenție", "Introduceți un termen de căutare.")
        return

    cautare = cautare.replace(" ", "+")
    url = f"https://www.auto-data.net/en/results?search={cautare}"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
    except requests.RequestException as e:
        messagebox.showerror("Eroare", f"Nu s-a putut accesa site-ul.\n{e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # div-ul care conține rezultatele
    masini = soup.find_all("div", class_="down down2")

    rezultate.clear()
    for masina in masini:
        link_tag = masina.find("a")
        if link_tag and "href" in link_tag.attrs and "title" in link_tag.attrs:
            titlu = link_tag["title"].strip()
            link = "https://www.auto-data.net" + link_tag["href"]
            rezultate.append((titlu, link))
            lista.insert(tk.END, titlu)

def afiseaza_link(event):
    selectie = lista.curselection()
    if selectie:
        index = selectie[0]
        titlu, link = rezultate[index]
        messagebox.showinfo(titlu, link)

# ---------- Interfață ----------
root = tk.Tk()
root.title("Căutare mașini auto-data.net")

entry = tk.Entry(root, width=50)
entry.pack(pady=10)

buton = tk.Button(root, text="Caută", command=cauta_masini)
buton.pack()

lista = tk.Listbox(root, width=80, height=20)
lista.pack(pady=10)
lista.bind("<<ListboxSelect>>", afiseaza_link)

rezultate = []

root.mainloop()
