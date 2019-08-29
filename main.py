from network import LoRa
from network import Bluetooth
from LIS2HH12 import LIS2HH12
from pytrack import Pytrack
from L76GNSS import L76GNSS #GPS
from deepsleep import DeepSleep

import deepsleep
import pycom
import socket
import network
import cayenneLPP #Low power packet forwarding
import time
import gc
import math
import binascii
import struct

#Enable garbage collection:
gc.enable()
gc.collect()

#Close Unnecessary functions:
ds = DeepSleep()
#ds.enable_auto_poweroff() #enable auto power off
bt = Bluetooth()
bt.deinit() #close bluetooth
wlan = network.WLAN()
wlan.deinit()  #close WLAN


py = Pytrack()
acc = LIS2HH12()
l76 = L76GNSS(py, timeout=10)

pycom.heartbeat(False)


#Lora settings:
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.US915, adr=False, device_class=LoRa.CLASS_A, tx_power=20)

dev_addr = struct.unpack(">l", binascii.unhexlify('26021192'))[0]
nwk_swkey = binascii.unhexlify('CF3F93604C31A58A40690C98FEBB9FB4')
app_swkey = binascii.unhexlify('1863BFEE80BB7026A2A906BDF154D003')

# remove all the non-default channels
for i in range(0, 72):
    lora.remove_channel(i)

lora.add_channel(8, frequency=903900000, dr_min=0, dr_max=3)
lora.add_channel(9, frequency=904100000, dr_min=0, dr_max=3)
lora.add_channel(10, frequency=904300000, dr_min=0, dr_max=3)
lora.add_channel(11, frequency=904500000, dr_min=0, dr_max=3)
lora.add_channel(12, frequency=904700000, dr_min=0, dr_max=3)
lora.add_channel(13, frequency=904900000, dr_min=0, dr_max=3)
lora.add_channel(14, frequency=905100000, dr_min=0, dr_max=3)
lora.add_channel(15, frequency=905300000, dr_min=0, dr_max=3)
lora.add_channel(65, frequency=904600000, dr_min=4, dr_max=4) # 500KHz uplink larger dr breaks(?)


lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 3)

print ("LoRaWAN Initialized")

# enable wakeup source from INT pin
py.setup_int_pin_wake_up(False)
# enable activity and also inactivity interrupts, using the default callback handler
py.setup_int_wake_up(True,True)
# set the acceleration threshold to 2000mG (2G) and the min duration to 160ms
acc.enable_activity_interrupt(2000, 160)

while True:
        #wake_s = ds.get_wake_status()
        #print(wake_s)
    time.sleep(0.1)
    #if(acc.activity()):
    if(True):
        pycom.rgbled(0x000066) #Color blue
        coord = l76.coordinates()
        s.setblocking(True)
        lpp = cayenneLPP.CayenneLPP(size = 100, sock = s)#create socket to send messages to server

        #pitch= acc.pitch()
        #roll = acc.roll()
        #yaw = acc.yaw()

        #print('Pitch:',pitch)
        #print('Roll:' ,roll)
        #print('Roll:' ,yaw)

        coord = l76.coordinates() #Get the coordinates
        c0 =coord[0]
        c1 =coord[1]

        #volt= py.read_battery_voltage() #Read Battery Voltage

        if (str(coord[0]) != 'None'):
            pycom.rgbled(0x006600) #Color Green
            lpp.add_analog_input(volt, channel = 1)
            lpp.add_gps(c0, c1, 55,  channel = 2)
            lpp.send()
            time.sleep(1)
            print('Data sent with GPS')

        else:
            pycom.rgbled(0x660066) #Color Purpure
            #lpp.add_accelerometer(pitch,roll,0)
            lpp.add_analog_input(volt, channel = 1)
            lpp.add_gps(0,0, 55, channel = 2)
            lpp.send()
            time.sleep(1)
            print('Data sent without GPS')
        s.setblocking(False)
        time.sleep(0.1)
    else:
        pycom.rgbled(0x330000)  #color red
        print("Sleep mode actived . . .")
        time.sleep(0.2)
        # go to sleep for 20 seconds maximum if no accelerometer interrupt happens
        # py.setup_sleep(20)
        # py.go_to_sleep()
        # print(". . .")
        # ds.go_to_sleep(10)

    gc.mem_free() #Clean the memory
