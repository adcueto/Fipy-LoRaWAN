from network import LoRa
from LIS2HH12 import LIS2HH12
from pytrack import Pytrack
from L76GNSS import L76GNSS #GPS

import pycom
import socket
import binascii
import struct
import pycom
import network
import cayenneLPP
import time
import gc

gc.enable()
py = Pytrack()
acc = LIS2HH12()
l76 = L76GNSS(py, timeout=10)
pycom.heartbeat(False)

#lora_packet.decrypt(packet, AppSKey, NwkSKey).toString('hex')
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.US915,adr=False, device_class=LoRa.CLASS_A, tx_power=20)

dev_addr = struct.unpack(">l", binascii.unhexlify('26021A86'))[0]
nwk_swkey = binascii.unhexlify('CF3F93604C31A58A40690C98FEBB9FB4')
app_swkey = binascii.unhexlify('6AC2D09B77EFECF43E9CC0A2607D41D9')

# remove all the non-default channels
for i in range(0, 72):
    lora.remove_channel(i)

# set the 3 default channels to the same frequency
lora.add_channel(0, frequency=903900000, dr_min=0, dr_max=3)
lora.add_channel(1, frequency=903900000, dr_min=0, dr_max=3)
lora.add_channel(2, frequency=903900000, dr_min=0, dr_max=3)


lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 3)

print ("LoRa Initialized")

py.setup_int_pin_wake_up(False)
py.setup_int_wake_up(True,True)
acc.enable_activity_interrupt(150, 160)

while True:
    #wake_s = ds.get_wake_status()
    #print(wake_s)
    time.sleep(0.1)
    #if(acc.activity()):
    if(True):
        pycom.rgbled(0x11fff1)
        coord = l76.coordinates()
        s.setblocking(True)
        lpp = cayenneLPP.CayenneLPP(size = 100, sock = s)
        pitch= acc.pitch()
        roll = acc.roll()
        #print('Pitch:',pitch)
        #print('Roll:' ,roll)
        volt= py.read_battery_voltage() #Read Battery Voltage
        c0 =coord[0]
        c1 =coord[1]

        if (str(coord[0]) != 'None'):

            lpp.add_analog_input(volt, channel = 114)
            lpp.add_gps(c0, c1, 55)
            lpp.send()
            time.sleep(0.3)
            print('Data sent: GPS')

        else:
            pycom.rgbled(0x7fff00)
                #lpp.add_accelerometer(pitch,roll,0)
            lpp.add_analog_input(volt, channel = 114)
            lpp.add_gps(0,0, 55, channel = 124)
            lpp.send()
            time.sleep(0.3)
            print('Data sent: No GPS')

    else:
        pycom.rgbled(0x111111)
        print("SLEEP MODE ACTIVATED . . .")

    gc.collect()
    gc.mem_free()
    py.setup_sleep(100)
