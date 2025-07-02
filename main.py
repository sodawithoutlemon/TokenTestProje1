import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QSizePolicy, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

class MainWindows(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Ekran boyutu ayarı
        screen = QApplication.primaryScreen().geometry()
        self.setFixedSize(screen.width() // 2, screen.height() // 2)

        # Ana layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Başlık
        title = QLabel("Token Update Tool")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Butonlar
        button_layout = QHBoxLayout()
        self.search_btn = QPushButton("Cihazları Ara")
        self.search_btn.clicked.connect(self.search_devices)
        self.upload_btn = QPushButton("Cihazlara Yükle")
        button_layout.addWidget(self.search_btn)
        button_layout.addWidget(self.upload_btn)
        layout.addLayout(button_layout)

        # Cihaz listesi (table)
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Ad", "Oran", "Durum"])
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # Test için 5 cihaz verisi ekle
        test_data = [
            {"ad": "Cihaz A", "oran": 10, "durum": "yükleniyor"},
            {"ad": "Cihaz B", "oran": 20, "durum": "hazır"},
            {"ad": "Cihaz C", "oran": 5,  "durum": "başarısız"},
            {"ad": "Cihaz D", "oran": 75, "durum": "yükleniyor"},
            {"ad": "Cihaz E", "oran": 100,"durum": "tamamlandı"},
        ]

    from PyQt5.QtWidgets import QProgressBar

    def search_devices(self):
        # Gerçek cihaz arama yerine örnek veriler:
        

        test_data = [
            {"ad": "Cihaz A", "oran": 10, "durum": "yükleniyor"},
            {"ad": "Cihaz B", "oran": 20, "durum": "hazır"},
            {"ad": "Cihaz C", "oran": 5, "durum": "başarısız"},
            {"ad": "Cihaz D", "oran": 75, "durum": "yükleniyor"},
            {"ad": "Cihaz E", "oran": 100, "durum": "tamamlandı"},
        ]
        self.populate_table(test_data)

    def populate_table(self, device_list):
        self.table.setRowCount(len(device_list))
        for row, device in enumerate(device_list):
            self.table.setItem(row, 0, QTableWidgetItem(str(device["ad"])))

            # Yüzdelik oran için progress bar ekle
            progress = QProgressBar()
            progress.setValue(device["oran"])
            progress.setAlignment(Qt.AlignCenter)
            progress.setStyleSheet("""
                QProgressBar {
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;  /* Yeşil */
                    width: 10px;
                }
            """)
            self.table.setCellWidget(row, 1, progress)

            self.table.setItem(row, 2, QTableWidgetItem(str(device["durum"])))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindows()
    window.show()
    sys.exit(app.exec_())