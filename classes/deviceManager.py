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


class DeviceManager:
    @staticmethod
    def get_connected_devices(flag=True):
        devices = []
        try:
            result = subprocess.check_output(['adb', 'devices', '-l'], encoding='utf-8')
            lines = result.strip().split('\n')[1:]

            usb_info = DeviceManager.get_usb_instanceid_with_port_info() if flag else []

            for line in lines:
                if not line.strip():
                    continue

                parts = line.split()
                if len(parts) < 2 or parts[1] != 'device':
                    continue

                serial = parts[0]
                device = model = "-"
                for part in parts:
                    if part.startswith("device:"):
                        device = part.split(":")[1]
                    elif part.startswith("model:"):
                        model = part.split(":")[1]

                port = "-"
                if flag:
                    for d in usb_info:
                        if d['instance_id'].split("\\")[2] == serial:
                            splited = d['port'].split(".")
                            first = splited[0].split("#")
                            second = splited[1].split("#")
                            port = first[0][:-1] + ": " + first[1] + " / " + second[0][:-1] + ": " + second[1]
                            break

                devices.append({
                    "serial": serial,
                    "ad": (model + " " + device).strip(),
                    "port": port,
                    "oran": 0,
                    "durum": "Yüklemeye Hazır"
                })
        except Exception as e:
            print("ADB hatası:", e)
        return devices

    @staticmethod
    def get_usb_instanceid_with_port_info():
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
        return [{"instance_id": d["InstanceId"], "port": d["Location"]} for d in devices]
