import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QSizePolicy, QProgressBar
)
import subprocess

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import threading
import os


class MainWindows(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        screen = QApplication.primaryScreen().geometry()
        self.setFixedSize(screen.width() // 2, screen.height() // 2)

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Token Update Tool")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        button_layout = QHBoxLayout()
        self.search_btn = QPushButton("Cihazları Ara")
        self.search_btn.clicked.connect(self.search_devices)
        self.upload_btn = QPushButton("Cihazlara Yükle")
        button_layout.addWidget(self.search_btn)
        button_layout.addWidget(self.upload_btn)
        layout.addLayout(button_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Serial", "Ad", "Port", "Oran", "Durum"])
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

    def search_devices(self):
        devices = get_android_devices()
        self.populate_table(devices)

    def populate_table(self, device_list):
        self.table.setRowCount(len(device_list))
        for row, device in enumerate(device_list):
            self.table.setItem(row, 0, QTableWidgetItem(str(device.get("serial", "-"))))

            self.table.setItem(row, 1, QTableWidgetItem(str(device.get("ad", "-"))))
            self.table.setItem(row, 2, QTableWidgetItem(str(device.get("port", "-"))))

            progress = QProgressBar()
            progress.setValue(device.get("oran", 0))
            progress.setAlignment(Qt.AlignCenter)
            progress.setStyleSheet("""
                QProgressBar {
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    width: 10px;
                }
            """)

            self.table.setCellWidget(row, 3, progress)

            self.table.setItem(row, 4, QTableWidgetItem(str(device.get("durum", "-"))))


def get_android_devices():
    try:
        result = subprocess.check_output(['adb', 'devices', '-l'], encoding='utf-8')
        lines = result.strip().split('\n')[1:]  # Başlık satırı atla
        devices = []


        for line in lines:

            if not line.strip():
                continue

            parts = line.split()
            if len(parts) < 2 or parts[1] != 'device':
                continue

            serial = parts[0]
            device = "-"
            model = "-"
            usbport = "-"

            for part in parts:
                if part.startswith("device:"):
                    device = part.split(":")[1]
                elif part.startswith("model:"):
                    model = part.split(":")[1]


            devices.append({
                "serial": serial,
                "ad": (model+" "+device).strip(),
                "port": usbport,
                "oran": 0,
                "durum": "Yüklemeye Hazır"
            })

        return devices

    except Exception as e:
        print("ADB hatası:", e)
        return []


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindows()
    window.show()
    sys.exit(app.exec_())
