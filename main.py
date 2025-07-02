import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QSizePolicy, QProgressBar, QFileDialog
)
import subprocess
import subprocess
import subprocess
import json






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
        #dosya seçmeyi sağlayan alan
        #dosya yoksa ya da farklıysa işlemi bozar
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


        #bağlı cihaz kadar thread açıp yükleme işlemini başlatan fonksiyon
        for device in self.devices:
            serial = device["serial"]
            thread = threading.Thread(target=self.install_apk_to_device, args=(serial, apk_path))
            thread.start()

    def install_apk_to_device(self, serial, apk_path):
        #adb ile apkyı yükleyen fonksiyon

        self.update_status_signal.emit(serial, "Yüklemeye Başladı")
        #update_status ile gui güncelleniyor
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
        #ui elementleri oluşturan fonksiyon
        screen = QApplication.primaryScreen().geometry()
        self.setFixedSize(screen.width() // 2, screen.height() // 2)
        #ekranın yarısı kadar büyüklükte boyu değiştirilemeyen ekran oluşturur

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Token Update Tool")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        #ana ekran yazısı


        #butonlar
        button_layout = QHBoxLayout()

        self.search_btn = QPushButton("Cihazları Ara")
        self.search_btn.clicked.connect(lambda: self.search_devices(flag=True))

        self.search_btnwo = QPushButton("Cihazları Ara (Portsuz)")
        self.search_btnwo.clicked.connect(lambda: self.search_devices(flag=False))

        self.upload_btn = QPushButton("Cihazlara Yükle")
        self.upload_btn.clicked.connect(self.upload_to_devices)
        self.upload_btn.setEnabled(False)  # Başlangıçta kapalı
        button_layout.addWidget(self.search_btn)
        button_layout.addWidget(self.upload_btn)
        button_layout.addWidget(self.search_btnwo)
        layout.addLayout(button_layout)


        #tablonun 5 column ve sınırsız row olarak oluşturulması
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Serial", "Ad", "Port", "Oran", "Durum"])
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

    def get_usb_instanceid_with_port_info(self):
        # Bu komut her USB cihaz için LocationInfo'yu detaylı şekilde alır
        ps_command = r'''
        $usbDevices = Get-PnpDevice -PresentOnly | Where-Object { $_.InstanceId -like "*USB*" }
        $results = foreach ($dev in $usbDevices) {
            $loc = Get-PnpDeviceProperty -InstanceId $dev.InstanceId -KeyName 'DEVPKEY_Device_LocationInfo' -ErrorAction SilentlyContinue
            [PSCustomObject]@{
                InstanceId = $dev.InstanceId
                Location   = if ($loc) { $loc.Data } else { $null }
            }
        }
        $results | ConvertTo-Json
        '''

        result = subprocess.check_output(['powershell', '-Command', ps_command], encoding='utf-8')

        devices = json.loads(result)
        if isinstance(devices, dict):
            devices = [devices]

        return [
            {
                "instance_id": dev.get("InstanceId"),
                "port": dev.get("Location")
            }
            for dev in devices
        ]

    # Test:



    def search_devices(self, flag):
        #hafızayı temizledikten sonra
        #command line'a adb devices -l komutunu yapıştırarak bilgisayara bağlı cihazları
        #yakalar ve önemli bilgileri kırparak ekrana yansıtır
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

                if(flag):
                    #bağlı cihazın portunu bulmak için bütün bağlı cihazların usb değerlerini alır
                    #sonrasında önceden kayıt ettiğimiz devicelerdeki seri numarasıyla karşılaştırarak
                    #doğru portu ve doğru cihazı bulur ve eşleştirir

                    def get_usb_instanceid_with_port_info():
                        # Bu komut her USB cihaz için LocationInfo'yu detaylı şekilde alır
                        ps_command = r'''
                        $usbDevices = Get-PnpDevice -PresentOnly | Where-Object { $_.InstanceId -like "*USB*" }
                        $results = foreach ($dev in $usbDevices) {
                            $loc = Get-PnpDeviceProperty -InstanceId $dev.InstanceId -KeyName 'DEVPKEY_Device_LocationInfo' -ErrorAction SilentlyContinue
                            [PSCustomObject]@{
                                InstanceId = $dev.InstanceId
                                Location   = if ($loc) { $loc.Data } else { $null }
                            }
                        }
                        $results | ConvertTo-Json
                        '''

                        result = subprocess.check_output(['powershell', '-Command', ps_command], encoding='utf-8')

                        devices = json.loads(result)
                        if isinstance(devices, dict):
                            devices = [devices]

                        return [
                            {
                                "instance_id": dev.get("InstanceId"),
                                "port": dev.get("Location")
                            }
                            for dev in devices
                        ]

                    for d in get_usb_instanceid_with_port_info():
                        if (d['instance_id'].split("\\")[2] == serial):
                            # Port_#0002.Hub_#0001

                            splited = d['port'].split(".")
                            first = splited[0].split("#")
                            second = splited[1].split("#")

                            usbport = first[0][:-1] + ": " + first[1] + " / " + second[0][:-1] + ": " + second[1]

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
        #search devicetan aldığı verileri düzenli bir şekilde tabloya düzen fonksiyon
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
