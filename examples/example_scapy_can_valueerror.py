import scapy
import scapy.all as sa
sa.conf.contribs["CANSocket"] = {"use-python-can": True}
sa.conf.contribs["ISOTP"] = {"use-can-isotp-kernel-module": False}

sa.load_layer("can")
sa.load_contrib("cansocket")

import can as pycan

while True:
    
    s = CANSocket(interface='pcan', channel='PCAN_USBBUS1', bitrate=33333, fd=False)
    s.close()
