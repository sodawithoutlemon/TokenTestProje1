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


class InstallerThread(threading.Thread):
    def __init__(self, serial, apk_path, callback):
        super().__init__()
        self.serial = serial
        self.apk_path = apk_path
        self.callback = callback  # callback(serial, status)

    def run(self):
        self.callback(self.serial, "Yüklemeye Başladı")
        try:
            process = subprocess.Popen(
                ["adb", "-s", self.serial, "install", "-r", self.apk_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            for line in process.stdout:
                print(f"[{self.serial}] {line.strip()}")
            process.wait()

            if process.returncode == 0:
                self.callback(self.serial, "Yükleme Tamamlandı")
            else:
                self.callback(self.serial, "Yükleme Başarısız")
        except Exception as e:
            self.callback(self.serial, f"Hata: {e}")
