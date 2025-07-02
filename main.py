import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QSizePolicy, QProgressBar, QFileDialog
)
import subprocess

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import threading
import os

from PyQt5.QtCore import pyqtSignal



class MainWindows(QWidget):
    update_status_signal = pyqtSignal(str, str)  # serial, yeni durum

    def __init__(self):
        super().__init__()
        self.update_status_signal.connect(self.on_update_status)
        self.init_ui()
        self.devices = []

    def on_update_status(self, serial, status):
        # devices listesindeki ilgili cihazın durumunu güncelle
        oran = 0
        for device in self.devices:
            if device["serial"] == serial:
                if(status == "Yüklemeye Başladı"):
                    oran = 40

                if (status == "Yükleme Tamamlandı"):
                    oran = 100

                device["durum"] = status
                device["oran"] = oran
                break

        self.populate_table(self.devices)

    def upload_to_devices(self):
        apk_path, _ = QFileDialog.getOpenFileName(
            self,
            "Bir APK dosyası seçin",
            "",
            "APK Dosyaları (*.apk);;Tüm Dosyalar (*)"
        )

        if not apk_path:
            print("APK dosyası seçilmedi.")
            return

        if not os.path.exists(apk_path):
            print("Seçilen APK dosyası bulunamadı:", apk_path)
            return

        for device in self.devices:
            serial = device["serial"]
            thread = threading.Thread(target=self.install_apk_to_device, args=(serial, apk_path))
            thread.start()

    def install_apk_to_device(self, serial, apk_path):
        self.update_status_signal.emit(serial, "Yüklemeye Başladı")
        print(f"[{serial}] Yükleme başlatıldı.")

        try:
            process = subprocess.Popen(
                ["adb", "-s", serial, "install", "-r", apk_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )

            for line in process.stdout:
                line = line.strip()
                if line:
                    print(f"[{serial}] {line}")

            process.wait()
            if process.returncode == 0:
                print(f"[{serial}] ✅ Yükleme tamamlandı.")
                self.update_status_signal.emit(serial, "Yükleme Tamamlandı")
            else:
                print(f"[{serial}] ❌ Yükleme başarısız.")
                self.update_status_signal.emit(serial, "Yükleme Başarısız")

        except Exception as e:
            print(f"[{serial}] Hata:", e)
            self.update_status_signal.emit(serial, f"Hata: {e}")

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
        self.upload_btn.clicked.connect(self.upload_to_devices)
        self.upload_btn.setEnabled(False)  # Başlangıçta kapalı

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
        self.devices = []
        try:
            result = subprocess.check_output(['adb', 'devices', '-l'], encoding='utf-8')
            lines = result.strip().split('\n')[1:]  # Başlık satırı atla

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

                self.devices.append({
                    "serial": serial,
                    "ad": (model + " " + device).strip(),
                    "port": usbport,
                    "oran": 0,
                    "durum": "Yüklemeye Hazır"
                })


        except Exception as e:
            print("ADB hatası:", e)
            self.devices = []

        self.upload_btn.setEnabled(len(self.devices) > 0)

        self.populate_table(self.devices)



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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindows()
    window.show()
    sys.exit(app.exec_())
