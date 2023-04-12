# manage usb to plc sending and receiving singals 
import threading
import time
from time import sleep
import re
import serial
import serial.tools.list_ports as listports
import sys
import os
import config
import datainterface
from kivy.app import App
from kivy.storage.jsonstore import JsonStore
import datainterface

class Plccom(object):
    """ DESCRIPTION
    Read usb port and get drive command from plc
    """

    def __init__(self,callback):
        # callback = trigger_operation_callback
        self.app = App.get_running_app()
        self.dataint = datainterface.DataInt()
       
        comport = self.dataint.get_com_port()#JsonStore(com_store_file).get("com")["port"]
        braudrate = self.dataint.get_com_bdr()#JsonStore(com_store_file).get("com")["brd"]
            # self.comportName = ""
        # self.baud = 0
        # self.timeout = None
        # self.ReceiveCallback = None
        self.isopen = False
        # self.receivedMessage = None
        # check if call in batch id is valid
        self.valid_batch_id = self.get_valid_batch_id()
        # checking if setting port is exist in current system
        if self.check_com_port(comport, braudrate):
            
            # run loop threading reas usb
            self.run(self.serialport, callback)
        else:
            self.app.alerting("[plccom]: 没有发现设备USB端口，请确认COM设置或检查连接是否松动!")
        # except:
        #     self.app.alerting("plccom: System com port file is corrupted!!")
        

    def check_com_port(self, comport, bdr):
        # result = True
        # if comport exist
        available_ports = [tuple(p) for p in list(listports.comports())]
        for ports in available_ports:
            if comport in ports:
                # open comport
                # setting port arguments 
                self.serialport = serial.Serial(port= None,\
                    bytesize=serial.EIGHTBITS,\
                    parity=serial.PARITY_NONE, \
                    stopbits=serial.STOPBITS_ONE,\
                    
                    xonxoff=0,\
                    rtscts=0)
                # try:
                self.serialport.port = comport
                self.serialport.baudrate = int(bdr)
                self.serialport.open()
                self.isopen = True
                # except:
                #     self.app.alerting("Open com port failed!")

                return True # foud port stop continue searching
        return False
        # run usb looping thread


    def run(self, serialport, callback):
        threading.Thread(target=self._readusb,\
                        name = 'usbthread',\
                        kwargs=dict(serial = serialport,callback=callback),\
                        daemon = True).start()


    def _readusb(self, serial, callback):
        print('read usb loop now.............')
        while True:
            # if serial.IsOpen():
            try:
                # if not ALERT:
                # pyserial receive data in ascii by default
                reads = serial.read(2)
                results = reads.decode('utf-8')
                
                if re.match("^[A-D][0-5]$", results):# filter legal usb signal
                    char_code = [char for char in results] #self.split_usb_received(results)
                    #print('read msg from usb:{}'.format(readResult))
                    if char_code[0] != b'\r\n':
                        print('current camera is {}, current batch_pos is{}'.format(char_code[0], char_code[1]))
                        # when first batch of new rank to go, set step as 0
                        cam = char_code[0]
                        # action_code = []
                        self.get_legal_cam_id(cam,char_code[1], callback)
            
            
            except Exception as e:
                print('read msg from plc is failed! for {}'.format(e))
                callback(None,1) # 1 --  read usb failled action
                self.app.alerting("USB读取错误，请确保端口波特率设置一致！")
                break
            # else:
            #     msg = 'serial port is not open!'
            #     callback(msg,2) # 2-- connceton to usb lost
    def __del__(self):
        try:
            if self.serialport.is_open():
                self.serialport.close()
        except:
            print("Destructor error closing COM port: ", sys.exc_info()[0] )
    
    def send(self,message):
        if self.isopen:
            try:
                # Ensure that the end of the message has both \r and \n, not just one or the other

                newmessage = message.strip()
                newmessage += '\r\n'
                self.serialport.write(newmessage.encode("utf-8"))

            except:
                print("Error sending message: ", sys.exc_info()[0] )
            else:
                return True
        else:
            return False
    # check if the cam id is consistent with  cam working code
    def get_legal_cam_id(self, cam, batchid, callback):
        if cam in config.ACTIVE_CAMERA_CODE:
            action_code = []
            action_code.append(cam)
            if self.is_legal_batch_id(batchid):
                action_code.append(int(batchid))
                # if not e.is_set():
                callback(action_code,0)
                # acton_code = [] # reset after send code
    # Check batch id is whin the target size range
    def is_legal_batch_id(self,batchid_str):
        batchid = int(batchid_str)
        return True  if batchid <= self.valid_batch_id else False
    def get_valid_batch_id(self):
        return (config.TARGET_SIZE//config.BATCH_SIZE) + 1
    
from kivy.factory import Factory
Factory.register('plccom',cls = Plccom)
