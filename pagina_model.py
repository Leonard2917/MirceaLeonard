import sys
import requests
from bs4 import BeautifulSoup
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QGroupBox,
    QHBoxLayout, QLineEdit, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class CarInfoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Car Info")
        self.setFixedSize(500, 300)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Input link + label
        link_layout = QHBoxLayout()
        self.link_label = QLabel("Enter URL:")
        self.link_label.setFont(QFont("Arial", 12))
        link_layout.addWidget(self.link_label)

        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText("Paste car data URL here...")
        self.link_input.setFont(QFont("Arial", 11))
        link_layout.addWidget(self.link_input)

        main_layout.addLayout(link_layout)

        # Titlu
        self.title_label = QLabel("Car Info")
        title_font = QFont("Arial", 18, QFont.Weight.Bold)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.title_label)

        # GroupBox cu date
        self.group_box = QGroupBox("Car Details")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(10)

        label_font = QFont("Arial", 12)

        self.label_brand = QLabel("Brand: N/A")
        self.label_brand.setFont(label_font)
        group_layout.addWidget(self.label_brand)

        self.label_model = QLabel("Model: N/A")
        self.label_model.setFont(label_font)
        group_layout.addWidget(self.label_model)

        self.label_acceleration = QLabel("Acceleration 0 - 100 km/h: N/A")
        self.label_acceleration.setFont(label_font)
        group_layout.addWidget(self.label_acceleration)

        self.group_box.setLayout(group_layout)
        main_layout.addWidget(self.group_box)

        # Butonul
        self.button_load = QPushButton("Load Car Info")
        self.button_load.setFixedHeight(40)
        self.button_load.setFont(QFont("Arial", 12, QFont.Weight.DemiBold))
        self.button_load.clicked.connect(self.load_car_info)
        main_layout.addWidget(self.button_load)

        self.setLayout(main_layout)

        # Stilizare buton
        self.button_load.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004080;
            }
        """)

        # Stilizare groupbox
        self.group_box.setStyleSheet("""
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

    def load_car_info(self):
        url = self.link_input.text().strip()
        if not url:
            self.show_error("Please enter a valid URL.")
            return

        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except Exception as e:
            self.show_error(f"Failed to get data:\n{e}")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        tables = soup.find_all("table")

        brand = None
        model = None
        acceleration = None

        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    if key == "Brand":
                        brand = value
                    elif key == "Model":
                        model = value
                    elif "Acceleration 0 - 100 km/h" in key:
                        acceleration = value

        self.label_brand.setText(f"Brand: {brand if brand else 'N/A'}")
        self.label_model.setText(f"Model: {model if model else 'N/A'}")
        self.label_acceleration.setText(f"Acceleration 0 - 100 km/h: {acceleration if acceleration else 'N/A'}")

    def show_error(self, message):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Error")
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setText(message)
        msg_box.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CarInfoApp()
    window.show()
    sys.exit(app.exec())
