import sys
import requests
from bs4 import BeautifulSoup
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
    QListWidget, QListWidgetItem, QMessageBox, QGroupBox, QStackedWidget,
    QHBoxLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class StartPage(QWidget):
    def __init__(self, switch_to_search):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        font = QFont("Arial", 14)

        self.btn_search = QPushButton("Search a car")
        self.btn_search.setFont(font)
        self.btn_search.clicked.connect(switch_to_search)

        self.btn_view_all = QPushButton("View all cars (în curând)")
        self.btn_view_all.setFont(font)
        self.btn_view_all.setEnabled(False)

        for btn in [self.btn_search, self.btn_view_all]:
            btn.setFixedSize(250, 50)

        layout.addWidget(self.btn_search)
        layout.addWidget(self.btn_view_all)

        self.setLayout(layout)

class CarSearchApp(QWidget):
    def __init__(self, go_back_callback):
        super().__init__()
        self.setFixedSize(700, 550)
        self.results = []
        self.go_back_callback = go_back_callback

        self.font_label = QFont("Arial", 12)
        self.font_button = QFont("Arial", 12, QFont.Weight.DemiBold)

        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Căutare
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Caută model auto (ex: Golf 7)")
        self.input_search.setFont(self.font_label)
        layout.addWidget(self.input_search)

        btn_layout = QHBoxLayout()
        self.btn_search = QPushButton("Caută")
        self.btn_search.setFont(self.font_button)
        self.btn_search.clicked.connect(self.cauta_masini)
        btn_layout.addWidget(self.btn_search)

        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setFont(self.font_button)
        self.btn_exit.clicked.connect(self.go_back_callback)
        btn_layout.addWidget(self.btn_exit)

        layout.addLayout(btn_layout)

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

        self.setLayout(layout)

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

        self.btn_exit.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border-radius: 8px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
            QPushButton:pressed {
                background-color: #ac2925;
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
                    for span in cells[1].find_all("span"):
                        span.decompose()
                    value = cells[1].get_text(strip=True)

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
                        power = value.split('@')[0].strip()
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

class AllCarsPage(QWidget):
    def __init__(self, go_back_callback):
        super().__init__()
        self.setFixedSize(700, 550)
        self.go_back_callback = go_back_callback

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.title = QLabel("Selectează un brand")
        self.title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.layout.addWidget(self.title)

        self.list = QListWidget()
        self.layout.addWidget(self.list)
        self.list.itemClicked.connect(self.item_selected)

        self.btn_back = QPushButton("Înapoi")
        self.btn_back.setFont(QFont("Arial", 12))
        self.btn_back.clicked.connect(self.go_back_callback)
        self.layout.addWidget(self.btn_back)

        self.stack = []  # Stocăm ierarhia parcursă (tupluri: nume, link)
        self.current_level = "brand"
        self.base_url = "https://www.auto-data.net"

        self.load_brands()

    def show_error(self, message):
        QMessageBox.critical(self, "Eroare", message)

    def load_brands(self):
        self.title.setText("Selectează un brand")
        self.list.clear()
        self.current_level = "brand"
        self.stack = []

        try:
            r = requests.get(f"{self.base_url}/en/", headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()

            soup = BeautifulSoup(r.text, "html.parser")
            # brandurile sunt in tag-uri <a class="marki_blok">
            brand_links = soup.find_all("a", class_="marki_blok")
            if not brand_links:
                QMessageBox.warning(self, "Avertisment", "Nu s-au găsit branduri. S-a schimbat structura site-ului.")
                return

            for brand in brand_links:
                # numele este in <strong>
                name_tag = brand.find("strong")
                name = name_tag.text.strip() if name_tag else brand.text.strip()
                href = brand.get("href", "")
                link = self.base_url + href
                self.stack.append((name, link))
                self.list.addItem(name)

        except Exception as e:
            self.show_error(f"Eroare la încărcarea brandurilor:\n{e}")

    def item_selected(self, item):
        index = self.list.row(item)

        if self.current_level == "brand":
            name, link = self.stack[index]
            self.stack = [(name, link)]  # resetăm stiva cu brandul curent
            self.load_models(link)

        elif self.current_level == "model":
            name, link = self.stack[index]
            self.stack = self.stack[:1] + [(name, link)]
            self.load_generations(link)

        elif self.current_level == "generation":
            name, link = self.stack[index]
            self.stack = self.stack[:2] + [(name, link)]
            self.load_motorizations(link)

        elif self.current_level == "variant":
            name, link = self.stack[index]
            self.afiseaza_detalii(link)

    def load_models(self, brand_url):
        self.title.setText("Selectează un model")
        self.list.clear()
        self.current_level = "model"
        self.stack = []

        try:
            r = requests.get(brand_url, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()

            soup = BeautifulSoup(r.text, "html.parser")
            # modelele sunt in div cu clasa "modelite"
            models_ul = soup.find("ul", class_="modelite")
            if not models_ul:
                QMessageBox.warning(self, "Avertisment", "Nu s-au găsit modele pentru acest brand.")
                return

            model_links = models_ul.find_all("a", class_="modeli")
            if not model_links:
                QMessageBox.warning(self, "Avertisment", "Nu s-au găsit modele în lista modelelor.")
                return

            for model in model_links:
                name_tag = model.find("strong")
                name = name_tag.text.strip() if name_tag else model.text.strip()
                href = model.get("href", "")
                link = self.base_url + href
                self.stack.append((name, link))
                self.list.addItem(name)

        except Exception as e:
            self.show_error(f"Eroare la încărcarea modelelor:\n{e}")

    def load_generations(self, link):
        self.title.setText("Selectează o generație")
        self.list.clear()
        self.current_level = "generation"
        self.stack = self.stack[:1]  # păstrăm doar brand și model în stivă

        self.generations = []  # asigur că există lista

        try:
            response = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            outer_div = soup.find("div", id="outer")
            if not outer_div:
                self.show_error("Nu am găsit div-ul cu id='outer'")
                return

            table = outer_div.find("table")
            if not table:
                self.show_error("Nu am găsit tabelul în div-ul 'outer'")
                return

            for tr in table.find_all("tr"):
                if tr.has_attr("id") and tr.has_attr("class"):
                    th = tr.find("th", class_=True)
                    if th:
                        a = th.find("a", href=True, title=True)
                        if a:
                            gen_name = a.get_text(strip=True)
                            gen_href = a["href"]
                            gen_link = self.base_url + gen_href
                            self.generations.append((gen_name, gen_link))
                            self.list.addItem(gen_name)

            if not self.generations:
                self.show_error("Nu am găsit generații.")

            else:
                self.current_level = "generation"
                self.stack.extend(self.generations)

        except Exception as e:
            self.show_error(f"Eroare la încărcarea generațiilor:\n{e}")


    def load_motorizations(self, link):
        self.title.setText("Selectează o motorizare")
        self.list.clear()
        self.current_level = "variant"
        self.stack = self.stack[:3]  # păstrăm brand, model, generație
        self.motorizations = []

        try:
            resp = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
        except Exception as e:
            QMessageBox.critical(self, "Eroare", f"Nu am putut descărca pagina:\n{e}")
            return

        soup = BeautifulSoup(resp.text, "html.parser")
        outer_div = soup.find("div", id="outer")
        if not outer_div:
            QMessageBox.critical(self, "Eroare", "Div-ul cu id='outer' nu a fost găsit.")
            return

        # Căutăm tabelă cu clasa 'carlist'
        tables = outer_div.find_all("table")
        carlist_table = None
        for t in tables:
            if "carlist" in t.get("class", []):
                carlist_table = t
                break

        if carlist_table:
            # Dacă găsim motorizări multiple
            for tr in carlist_table.find_all("tr"):
                th = tr.find("th", class_="i")
                if th:
                    a = th.find("a", href=True, title=True)
                    if a:
                        nume = a["title"]
                        nume_curat = nume.split(" - ")[0].strip()
                        href = a["href"].strip()
                        full_link = self.base_url + href
                        self.motorizations.append((nume_curat, full_link))
                        self.list.addItem(nume_curat)

            if not self.motorizations:
                QMessageBox.information(self, "Info", "Nu am găsit motorizări în această pagină.")
            else:
                self.stack.extend(self.motorizations)
            return

        # ⚠️ Fallback: considerăm că pagina este deja o motorizare unică
        h1 = soup.find("h1")
        if h1:
            nume = h1.get_text(strip=True)
        else:
            nume = "Motorizare necunoscută"

        self.motorizations.append((nume, link))
        self.list.addItem(nume)
        self.stack.append((nume, link))

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
                    # elimină toate span-urile din celula valoare
                    for span in cells[1].find_all("span"):
                        span.decompose()
                    value = cells[1].get_text(strip=True)

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
                        power = value.split('@')[0].strip()
                    elif "Kerb Weight" in key:
                        weight = value

        self.label_brand.setText(f"Brand: {brand}")
        self.label_model.setText(f"Model: {model}")
        self.label_acc.setText(f"Accelerație 0-100 km/h: {acceleration}")
        self.label_speed.setText(f"Viteză maximă: {speed}")
        self.label_prod.setText(f"Început producție: {prod_start}")
        self.label_power.setText(f"Putere: {power}")
        self.label_weight.setText(f"Greutate (Kerb): {weight}")

def show_error(self, message):
    QMessageBox.critical(self, "Eroare", message)
    
class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cars database")
        self.setFixedSize(700, 550)

        self.start_page = StartPage(self.show_search_page)
        self.search_page = CarSearchApp(self.show_start_page)
        self.all_cars_page = AllCarsPage(self.show_start_page)

        # conectăm butonul direct aici:
        self.start_page.btn_view_all.clicked.connect(self.show_all_cars_page)
        self.start_page.btn_view_all.setEnabled(True)
        self.start_page.btn_view_all.setText("View all cars")

        self.addWidget(self.start_page)
        self.addWidget(self.search_page)
        self.addWidget(self.all_cars_page)

        self.setCurrentWidget(self.start_page)

    def show_search_page(self):
        self.setCurrentWidget(self.search_page)

    def show_all_cars_page(self):
        self.setCurrentWidget(self.all_cars_page)

    def show_start_page(self):
        self.setCurrentWidget(self.start_page)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
