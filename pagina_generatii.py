import sys
import requests
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QLabel, QMessageBox
from bs4 import BeautifulSoup
from PyQt6.QtCore import Qt

class GenModelApp(QWidget):
    def __init__(self, url):
        super().__init__()
        self.url_base = "https://www.auto-data.net"
        self.url = url
        self.setWindowTitle("Lista Generații Model")
        self.resize(400, 600)

        self.layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.info_label = QLabel("Selectează o generație pentru detalii...")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(self.list_widget)
        self.layout.addWidget(self.info_label)
        self.setLayout(self.layout)

        self.generations = []  # listă tupluri (nume, href)
        self.load_generations()
        self.list_widget.currentRowChanged.connect(self.on_item_selected)

    def load_generations(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
        except Exception as e:
            self.info_label.setText(f"Eroare la descărcare: {e}")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        outer_div = soup.find("div", id="outer")
        if not outer_div:
            self.info_label.setText("Nu am găsit div-ul cu id='outer'")
            return

        table = outer_div.find("table")
        if not table:
            self.info_label.setText("Nu am găsit tabelul în div-ul 'outer'")
            return

        self.generations.clear()
        self.list_widget.clear()

        for tr in table.find_all("tr"):
            if tr.has_attr("id") and tr.has_attr("class"):
                th = tr.find("th", class_=True)
                if th:
                    a = th.find("a", href=True, title=True)
                    if a:
                        gen_name = a.get_text(strip=True)
                        gen_href = a["href"]
                        self.generations.append((gen_name, gen_href))
                        self.list_widget.addItem(gen_name)

        if not self.generations:
            self.info_label.setText("Nu am găsit generații.")

    def on_item_selected(self, index):
        if index < 0 or index >= len(self.generations):
            self.info_label.setText("Selectează o generație pentru detalii...")
            return
        name, href = self.generations[index]
        full_url = self.url_base + href
        self.info_label.setText(f"URL: {full_url}")

        msg = QMessageBox(self)
        msg.setWindowTitle("Detalii generație")
        msg.setText(f"Generație selectată: {name}\nURL: {full_url}")
        msg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    url = "https://www.auto-data.net/en/volkswagen-golf-model-896"  # poți schimba URL-ul aici
    window = GenModelApp(url)
    window.show()
    sys.exit(app.exec())
