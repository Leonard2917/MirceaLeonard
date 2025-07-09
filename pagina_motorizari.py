import sys
import requests
from bs4 import BeautifulSoup
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QMessageBox

class MotorizationListApp(QWidget):
    def __init__(self, url):
        super().__init__()
        self.setWindowTitle("Lista Motorizări")
        self.resize(600, 400)
        self.url_base = "https://www.auto-data.net"
        self.url = url

        self.layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)
        self.setLayout(self.layout)

        self.motorizations = []  # listă de tupluri (nume, href)

        self.load_motorizations()

        self.list_widget.itemClicked.connect(self.show_link)

    def load_motorizations(self):
        try:
            resp = requests.get(self.url)
            resp.raise_for_status()
        except Exception as e:
            QMessageBox.critical(self, "Eroare", f"Nu am putut descărca pagina:\n{e}")
            return

        soup = BeautifulSoup(resp.text, "html.parser")
        outer_div = soup.find("div", id="outer")
        if not outer_div:
            QMessageBox.critical(self, "Eroare", "Div-ul cu id='outer' nu a fost găsit.")
            return

        tables = outer_div.find_all("table")
        table = None
        for t in tables:
            classes = t.get("class", [])
            if "carlist" in classes:
                table = t
                break

        if not table:
            QMessageBox.critical(self, "Eroare", "Tabela cu clasa 'carlist' nu a fost găsită.")
            return

        self.motorizations.clear()
        self.list_widget.clear()

        # Parcurgem toate rândurile din tabel
        for tr in table.find_all("tr"):
            th = tr.find("th", class_="i")
            if th:
                a = th.find("a", href=True, title=True)
                if a:
                    nume = a["title"]
                    nume_curat = nume.split(" - ")[0].strip()
                    self.motorizations.append((nume_curat, a["href"].strip()))
                    self.list_widget.addItem(nume_curat)

        if not self.motorizations:
            QMessageBox.information(self, "Info", "Nu am găsit motorizări în această pagină.")

    def show_link(self, item):
        index = self.list_widget.row(item)
        if 0 <= index < len(self.motorizations):
            nume, href = self.motorizations[index]
            full_url = self.url_base + href
            QMessageBox.information(self, nume, f"Link motorizare:\n{full_url}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Pune aici URL-ul paginii cu motorizările dorite:
    url = "https://www.auto-data.net/en/volkswagen-golf-v-5-door-generation-10007"
    window = MotorizationListApp(url)
    window.show()
    sys.exit(app.exec())
