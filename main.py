import sys
import os
import json
import subprocess
import threading

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QSizePolicy, QProgressBar, QFileDialog
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal, QObject

from classes.deviceManager import DeviceManager
from classes.installer import InstallerThread


class MainWindow(QWidget):
    update_status_signal = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.devices = []
        self.update_status_signal.connect(self.on_update_status)
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
        self.search_btn.clicked.connect(lambda: self.search_devices(True))
        self.search_btnwo = QPushButton("Cihazları Ara (Portsuz)")
        self.search_btnwo.clicked.connect(lambda: self.search_devices(False))
        self.upload_btn = QPushButton("Cihazlara Yükle")
        self.upload_btn.clicked.connect(self.upload_to_devices)
        self.upload_btn.setEnabled(False)

        button_layout.addWidget(self.search_btn)
        button_layout.addWidget(self.upload_btn)
        button_layout.addWidget(self.search_btnwo)
        layout.addLayout(button_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Serial", "Ad", "Port", "Oran", "Durum"])
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

    def search_devices(self, flag):
        self.devices = DeviceManager.get_connected_devices(flag)
        self.upload_btn.setEnabled(len(self.devices) > 0)
        self.populate_table()

    def upload_to_devices(self):
        apk_path, _ = QFileDialog.getOpenFileName(self, "Bir APK dosyası seçin", "", "APK Dosyaları (*.apk);;Tüm Dosyalar (*)")
        if not apk_path or not os.path.exists(apk_path):
            print("Geçersiz APK yolu.")
            return

        for device in self.devices:
            thread = InstallerThread(device["serial"], apk_path, self.update_status_signal.emit)
            thread.start()

    def on_update_status(self, serial, status):
        for device in self.devices:
            if device["serial"] == serial:
                device["durum"] = status
                device["oran"] = 40 if status == "Yüklemeye Başladı" else (100 if status == "Yükleme Tamamlandı" else 0)
                break
        self.populate_table()

    def populate_table(self):
        self.table.setRowCount(len(self.devices))
        for row, device in enumerate(self.devices):
            self.table.setItem(row, 0, QTableWidgetItem(device.get("serial", "-")))
            self.table.setItem(row, 1, QTableWidgetItem(device.get("ad", "-")))
            self.table.setItem(row, 2, QTableWidgetItem(device.get("port", "-")))

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

            self.table.setItem(row, 4, QTableWidgetItem(device.get("durum", "-")))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
