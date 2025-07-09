import sys
import requests
from bs4 import BeautifulSoup
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
    QListWidget, QListWidgetItem, QMessageBox, QGroupBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class CarSearchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto-Data Car Search")
        self.setFixedSize(700, 550)

        self.results = []

        # Fonts
        self.font_label = QFont("Arial", 12)
        self.font_button = QFont("Arial", 12, QFont.Weight.DemiBold)

        # Layout principal
        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Căutare
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Caută model auto (ex: Golf 7)")
        self.input_search.setFont(self.font_label)
        layout.addWidget(self.input_search)

        self.btn_search = QPushButton("Caută")
        self.btn_search.setFont(self.font_button)
        self.btn_search.clicked.connect(self.cauta_masini)
        layout.addWidget(self.btn_search)

        # Listă rezultate
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.afiseaza_detalii)
        layout.addWidget(self.list_widget)

        # Detalii mașină
        self.group_details = QGroupBox("Detalii mașină")
        group_layout = QVBoxLayout()

        self.label_brand = QLabel("Brand: N/A")
        self.label_model = QLabel("Model: N/A")
        self.label_acc = QLabel("Accelerație 0-100 km/h: N/A")
        self.label_speed = QLabel("Viteză maximă: N/A")
        self.label_prod = QLabel("Început producție: N/A")
        self.label_power = QLabel("Putere: N/A")
        self.label_weight = QLabel("Greutate (Kerb): N/A")

        for lbl in [self.label_brand, self.label_model, self.label_acc,
                    self.label_speed, self.label_prod, self.label_power, self.label_weight]:
            lbl.setFont(self.font_label)
            group_layout.addWidget(lbl)

        self.group_details.setLayout(group_layout)
        self.group_details.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #0078d7;
                border-radius: 10px;
                margin-top: 10px;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
        """)
        layout.addWidget(self.group_details)

        # Setare layout
        self.setLayout(layout)

        # Stil buton
        self.btn_search.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 8px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004080;
            }
        """)

    def cauta_masini(self):
        query = self.input_search.text().strip()
        self.results.clear()
        self.list_widget.clear()

        if not query:
            self.show_error("Introduceți un termen de căutare.")
            return

        query_encoded = query.replace(" ", "+")
        url = f"https://www.auto-data.net/en/results?search={query_encoded}"

        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
        except Exception as e:
            self.show_error(f"Eroare la descărcarea rezultatelor:\n{e}")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        masini = soup.find_all("div", class_="down down2")

        for masina in masini:
            link_tag = masina.find("a")
            if link_tag and "href" in link_tag.attrs and "title" in link_tag.attrs:
                titlu = link_tag["title"].strip()
                link = "https://www.auto-data.net" + link_tag["href"]
                self.results.append((titlu, link))
                self.list_widget.addItem(QListWidgetItem(titlu))

        if not self.results:
            self.show_error("Nicio mașină găsită pentru termenul introdus.")

    def afiseaza_detalii(self, item: QListWidgetItem):
        index = self.list_widget.row(item)
        _, link = self.results[index]

        try:
            response = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
        except Exception as e:
            self.show_error(f"Eroare la accesarea paginii:\n{e}")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        tables = soup.find_all("table")

        brand = model = acceleration = speed = prod_start = power = weight = "N/A"

        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True).split("\n")[0]

                    if key == "Brand":
                        brand = value
                    elif key == "Model":
                        model = value
                    elif "Acceleration 0 - 100 km/h" in key:
                        acceleration = value
                    elif "Maximum speed" in key:
                        speed = value
                    elif "Start of production" in key:
                        prod_start = value
                    elif key == "Power":
                        power = value
                    elif "Kerb Weight" in key:
                        weight = value

        self.label_brand.setText(f"Brand: {brand}")
        self.label_model.setText(f"Model: {model}")
        self.label_acc.setText(f"Accelerație 0-100 km/h: {acceleration}")
        self.label_speed.setText(f"Viteză maximă: {speed}")
        self.label_prod.setText(f"Început producție: {prod_start}")
        self.label_power.setText(f"Putere: {power}")
        self.label_weight.setText(f"Greutate: {weight}")

    def show_error(self, message):
        QMessageBox.critical(self, "Eroare", message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CarSearchApp()
    window.show()
    sys.exit(app.exec())
