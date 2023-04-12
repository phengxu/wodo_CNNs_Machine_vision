#！Users\11327\Anaconda3\envs\wodo python
import kivy
kivy.require('1.11.1')
from kivy.config import Config
Config.set('graphics','resizable',1)
# Config.set('graphics', 'resizable', 1)
Config.set('graphics','width',1920)
Config.set('graphics','height',1080)
Config.set('kivy','log_level','debug')# ‘trace’, ‘debug’, ‘info’, ‘warning’, ‘error’ or ‘critical’
Config.set('kivy','log_enable', 1)
Config.set('kivy','log_maxfiles',10)
Config.set('kivy', 'log_dir', r'd:\wodo\logs')
Config.set('kivy', 'window_icon', '/data/icons/icn.ico')
''' local module '''
import config
import worker
import cameras
from cameraImageBase import CameraImageBase
''' kivy module import '''
import kivy.core.text
from kivy.app import App
from kivy.base import EventLoop

from kivy.graphics import Color, Line, Rectangle
from kivy.clock import Clock, mainthread
from kivy.graphics.texture import Texture

from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
# from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, ListProperty,NumericProperty, BoundedNumericProperty
from kivy.event import EventDispatcher
# from kivy.storage.jsonstore import JsonStore

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.image import Image

from kivy.uix.behaviors import ToggleButtonBehavior
#for string name generation

import matplotlib.pyplot as plt #conda install -c conda-forge matplotlib
import matplotlib.patches as mpatches

''' build in module '''
from datetime import datetime
import sys
from time import sleep
import os
from pathlib import Path
import copy
import threading, queue
import time
''' third party module '''
import cv2
import numpy as np
import PySpin
# get working dir
absFilePath = os.path.abspath(__file__)
workdir = os.path.dirname(os.path.abspath(__file__))

# Declare class reference in kv file before load kv file
class MenuScreen(Screen):
    # as root class to create instance first
    qtbtn = ObjectProperty()
    btncalia = ObjectProperty()
    btncalib = ObjectProperty()
    btncalic = ObjectProperty()
    btncalid = ObjectProperty()
    circlepro = ObjectProperty()
    graphab = ObjectProperty()
    graphc = ObjectProperty()
    graphd = ObjectProperty()
    def __init__(self, **args):
        super(MenuScreen, self).__init__(**args)
        file = os.path.join(workdir, 'data','stastics','defaultgraph.png')
        self.grapha.source = file
        self.graphb.source = file
        self.graphc.source = file
        self.graphd.source = file

from time import gmtime, strftime
class Timer(Label):
    # ts = StringProperty()
    from datetime import datetime
    def __init__(self, **args):
        super(Timer, self).__init__(**args)
        self.text = ''
        self.font_size = 26
        self.start_time = time.time()
        self.start()
    def start(self):
        Clock.schedule_interval(self.count,1/30)

    def count(self, dt):
        timelapse = time.time() - self.start_time
        timelapse_format = time.strftime("%H:%M:%S", time.gmtime(timelapse))
        self.text = datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " | " +str(timelapse_format)
        # self.text = strftime("%Y-%m-%d %H:%M:%S", gmtime())
class Counting(Label):
    # counting current target passing
    def __init__(self, **args):
        super(Counting, self).__init__(**args)
        # self.totalcount = 0
        # self.ngcount = 0
        self.text = "0/0 0.0%"
        self.font_size = 22
    def caculate(self, t, ng):
        if t > 0:
            self.text = str(t) + " / " + str(ng) + "  "+ str(np.around(ng/t, 4)*100) + "%"


from kivy.uix.textinput import TextInput
from kivy.app import App

from kivy.uix.progressbar import ProgressBar
from kivy.core.text import Label as CoreLabel
from kivy.lang.builder import Builder
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.clock import Clock

class SliderCalibrate(Slider): # horizontal slider adjuster for move distance by one click
    def __init__(self, **kwargs):
        super(SliderCalibrate, self).__init__(**kwargs)
        self.min = 1
        self.max = 10
        self.step = 1
        self.orientation = 'horizontal'
        self.value = 1
        self.value_track = True
        self.value_track_color =  [0,1,1,1]
        config.sliderCalibrate = 1
    def on_touch_up(self, t): # override for set store value when touch released
        if self.collide_point(*t.pos):
            config.sliderCalibrate = self.value
            return False

"""
Button class
"""
class TrainButton(ToggleButtonBehavior, Button):
    btn_st = StringProperty()
    def __init__(self, **kwargs):
        super(TrainButton, self).__init__(**kwargs)
        # self.source = r'm:\wodo2-a\icons\checkbox_off.jpg'
        self.text = '检测模式'
        self.font_size = 28
        # self.text = 'train off'
        self.state = 'normal'
        self.background_color = 0,0,1,1

    def on_touch_down(self, t):
        # filter pos within button box
        if self.collide_point(*t.pos):
            # print(t)
            self.state = 'down' if self.state == 'normal' else 'normal'#root.ids.trainbtn.on_state()
            self.on_state(self, self.state)
            return False#set only  this button handle touch event

    def on_state(self, widget, value):
        # global WORKING_MODE
        if value == 'down':
            # self.source = r'm:\wodo2-a\icons\checkbox_on.jpg'
            # self.state = "down"
            self.text = '图像采集模式'
            self.background_color = 1,0,0,1
            # self.state = 'down'
            config.SYSTEM_WORKING_MODE = 'TRAIN'
            # print(self.text)
        else:
            # self.source = r'm:\wodo2-a\icons\checkbox_off.jpg'
            self.text = '检测模式'
            # self.state = 'normal'
            self.background_color = 0,0,1,1
            config.SYSTEM_WORKING_MODE = 'WORK'
            # print(self.text)
            # print('Current state is {}'.format(self.state))
        print('Current state is {}'.format(self.state))

class PauseButton(ToggleButtonBehavior, Button):
    btn_st = StringProperty()
    def __init__(self, **kwargs):
        super(PauseButton, self).__init__(**kwargs)
        # self.source = r'm:\wodo2-a\icons\checkbox_off.jpg'
        self.text = '暂停'
        self.font_size = 28
        # self.text = 'train off'
        self.pausecolor = 0,0,1,1
        self.conticolor = 1.0,0.0,0.0,1.0
        self.state = 'normal'
        #self.background_normal = './data/icons/btn_image.png'
        global usb_stop_event
        usb_stop_event.clear()
        self.app = App.get_running_app()
        # self.app.setQuitBtnDisabled(True)
        #self.background_color = self.pausecolor

    def on_touch_down(self, t):
        # filter pos within button box
        if self.collide_point(*t.pos):
            # print(t)
            self.state = 'down' if self.state == 'normal' else 'normal'#root.ids.trainbtn.on_state()
            self.on_state(self, self.state)
            return False#set only  this button handle touch event

    def on_state(self, widget, value):
        global usb_stop_event
        # global APPSTATE
        if value == 'down':
            # self.source = r'm:\wodo2-a\icons\checkbox_on.jpg'
            # self.state = "down"
            self.text = '暂停中'
            self.background_color = self.conticolor
            usb_stop_event.set()
            self.app.setQuitBtnDisabled(False)
            self.app.set_reboot_button_disabled(False)
            self.app.set_test_signal_Disabled(False)
            # print(self.text)
        else:
            # self.source = r'm:\wodo2-a\icons\checkbox_off.jpg'
            self.text = '暂停'
            # self.state = 'normal'
            self.background_color = self.pausecolor
            usb_stop_event.clear()
            self.app.setQuitBtnDisabled(True)
            self.app.set_reboot_button_disabled(True)
            self.app.set_test_signal_Disabled(True)
        print('Current state is {}'.format(self.state))

# Button control if 
class TriggerOnOffButton(ToggleButtonBehavior, Button):
    btn_st = StringProperty()
    def __init__(self, **kwargs):
        super(TriggerOnOffButton, self).__init__(**kwargs)
        # self.source = r'm:\wodo2-a\icons\checkbox_off.jpg'
        self.text = '工程模式'
        self.font_size = 28
        # self.text = 'train off'
        self.pausecolor = 0,0,1,1
        self.conticolor = 1.0,0.0,0.0,1.0
        self.state = 'normal'
        self.background_color = self.pausecolor
        self.app = App.get_running_app()

    def on_touch_down(self, t):
        # filter pos within button box
        if self.collide_point(*t.pos):
            # print(t)
            self.state = 'down' if self.state == 'normal' else 'normal'#root.ids.trainbtn.on_state()
            self.on_state(self, self.state)
            return False#set only  this button handle touch event

    def on_state(self, widget, value):
        global usb_stop_event
        # global APPSTATE
        if value == 'down':
            # self.source = r'm:\wodo2-a\icons\checkbox_on.jpg'
            #self.state = "down"
            self.text = '工厂模式'
            config.camera_trigger_on = True
            self.background_color = self.conticolor
            #usb_stop_event.set()
            self.app.set_test_signal_Disabled(True)
            #print(self.text)
        else:
            # self.source = r'm:\wodo2-a\icons\checkbox_off.jpg'
            self.text = '工程模式'
            #self.state = 'normal'
            config.camera_trigger_on = False
            self.background_color = self.pausecolor
            #usb_stop_event.clear()
            self.app.set_test_signal_Disabled(False)
        print('Current state is {}'.format(self.text))

class StartButton(Button):
    b_color = ListProperty()
    def __init__(self, **kwargs):
        super(StartButton, self).__init__(**kwargs)
        self.work = 'await'


"""
DISPALY CAMERA MODULE
"""
###### PREDICTION IMAGE #####
class TargetImages(Image):
    def __init__(self, **kwargs):
        super(TargetImages, self).__init__(**kwargs)
        self.texture = None
        self.size = (0,0)
        with self.canvas:
             # Rectangle(pos=self.pos, size=self.size, texture=self.texture)
             self.background_color = (151/255, 157/255, 159/255, .9)
        self._start()
    def _start(self):
        # global FPS
        #self.texture =Texture.create(size=(256*4,256))
        print('starting updating target images interval')
        Clock.schedule_interval(self._update, 1/config.FPS)
        # Clock.schedule_interval(self._update_image,1/FPS)
    def stop(self):
        Clock.unschedule(self._update)
    def _update(self,dt):
        # global V_STACK_IMGS
        if config.V_STACK_IMGS is not None:# and config.startblit:
            w,h =config.V_STACK_IMGS.shape[1],config.V_STACK_IMGS.shape[0]
            # print("------------texture size-----------------")
            # print("{}{}".format(w,h))
            self.texture =Texture.create(size=(w,h))
            self.texture.blit_buffer(bytes(config.V_STACK_IMGS), colorfmt='rgb', bufferfmt='ubyte')
###### CALIBRATE IMIAGE #
from calibrate import calibrate

'''
POP UP WIDGET
'''

class CalibratePop(Popup):# calibrating image
    
    cameraimage = ObjectProperty()
    btn_mvp = ObjectProperty()
    btn_disPlus = ObjectProperty()
    btn_disMinus = ObjectProperty()
    btn_mvl = ObjectProperty()
    btn_mvr = ObjectProperty()
    btn_mvd = ObjectProperty()
    btn_startCamera = ObjectProperty()
    btn_close = ObjectProperty()
    btn_pos_save = ObjectProperty()

    def __init__(self, title,cam,auto_dismiss):
        super(CalibratePop,self).__init__()
        self.title = title
        self.title_size = 28
        self.auto_dismiss = auto_dismiss
        #self.cam = cam
        if cam == 'cam0':
            self.cameraimage = CameraImageBase(config.cali_a_list, 'cam0') # cali list hand load in predict module
        if cam == 'cam1':
            self.cameraimage = CameraImageBase(config.cali_b_list, 'cam1')
        if cam == 'cam2':
            self.cameraimage = CameraImageBase(config.cali_c_list, 'cam2')
        if cam == 'cam3':
            self.cameraimage = CameraImageBase(config.cali_d_list, 'cam3')
        self.content = BoxLayout()
        self.box_outside = BoxLayout(orientation='vertical')
        # assembly calibrate button group
        self.box_calibrate_buttons=BoxLayout(orientation='vertical', size_hint=(.2,1))
        self.btn_mvp = Button(text = '下移', font_size = 22) # move down
        self.btn_disPlus = Button(text = '增加间距', font_size = 22) # dis +
        self.btn_disMinus = Button(text = '减少间距', font_size = 22) # dis -
        self.btn_mvl = Button(text = '左移', font_size = 22) # move left
        self.btn_mvr = Button(text = '右移', font_size = 22) # move right
        self.btn_mvd = Button(text = '上移', font_size = 22) # move up
        self.btn_add_box_width = Button(text = '增加宽度', font_size = 22) # add box width
        self.btn_reduce_box_width = Button(text = '减少宽度', font_size = 22)# reduce box width
        self.btn_add_box_height = Button(text = '增加高度', font_size = 22) # add box height
        self.btn_reduce_box_height = Button(text = '减少高度', font_size = 22)
        self.box_calibrate_buttons.add_widget(self.btn_mvp)
        self.box_calibrate_buttons.add_widget(self.btn_mvd)
        self.box_calibrate_buttons.add_widget(self.btn_disPlus)
        self.box_calibrate_buttons.add_widget(self.btn_disMinus)
        self.box_calibrate_buttons.add_widget(self.btn_mvl)
        self.box_calibrate_buttons.add_widget(self.btn_mvr)
        self.box_calibrate_buttons.add_widget(self.btn_add_box_width)
        self.box_calibrate_buttons.add_widget(self.btn_reduce_box_width)
        self.box_calibrate_buttons.add_widget(self.btn_add_box_height)
        self.box_calibrate_buttons.add_widget(self.btn_reduce_box_height)

        # assembly the manager button
        self.box_manager = BoxLayout(orientation='horizontal',size_hint=(1,.1))
        self.btn_startCamera = Button(text='显示', font_size = 28)
        self.btn_pos_save = Button(text = '保存坐标', font_size = 28)
        self.btn_close = Button(text = '关闭', font_size = 28)
        self.box_manager.add_widget(self.btn_startCamera)
        self.box_manager.add_widget(self.btn_pos_save)
        self.box_manager.add_widget(self.btn_close)

        self.box_cam_slider_calibtn = BoxLayout(size_hint=(1,.9),orientation = 'horizontal')# holding cam,slider and cali btns
        self.box_cam_calibrate = BoxLayout(size_hint=(1,.9), orientation='vertical')#holding image and slider
        # create slider tool in a box
        self.sliderBox = BoxLayout(size_hint=(.5,.2),pos_hint = {'x':.25,'y':1},orientation = 'vertical')
        self.sliderCali = SliderCalibrate()
        self.sliderBox.add_widget(self.sliderCali)
        # combine slider and camera image
        self.box_cam_calibrate.add_widget(self.cameraimage)
        self.box_cam_calibrate.add_widget(self.sliderBox)
        # combine cam/slider with cali btns horizontally
        self.box_cam_slider_calibtn.add_widget(self.box_cam_calibrate)
        self.box_cam_slider_calibtn.add_widget(self.box_calibrate_buttons)
        # self.box_cam_calibrate.add_widget(self.box_calibrate_buttons)
        # combine cam/slider + cali btns with manager btns
        self.box_outside.add_widget(self.box_cam_slider_calibtn)
        self.box_outside.add_widget(self.box_manager)

        # bind callback to buttons
        self.btn_startCamera.bind(on_press=lambda x: self.cameraimage._start())
        self.btn_mvp.bind(on_press = lambda x: self.cameraimage.moveup())
        self.btn_disPlus.bind(on_press = lambda x: self.cameraimage.addDistance())
        self.btn_disMinus.bind(on_press = lambda x: self.cameraimage.minusDistance())
        self.btn_mvl.bind(on_press = lambda x: self.cameraimage.moveleft())
        self.btn_mvr.bind(on_press = lambda x: self.cameraimage.moveright())
        self.btn_mvd.bind(on_press = lambda x: self.cameraimage.movedown())
        self.btn_add_box_width.bind(on_press = lambda x: self.cameraimage.add_box_width())
        self.btn_reduce_box_width.bind(on_press = lambda x: self.cameraimage.reduce_box_width())
        self.btn_add_box_height.bind(on_press = lambda x: self.cameraimage.add_box_height())
        self.btn_reduce_box_height.bind(on_press = lambda x: self.cameraimage.reduce_box_height())


        self.btn_pos_save.bind(on_press = lambda x: self.cameraimage.savePos())
        self.btn_close.bind(on_press = lambda x:  App.get_running_app().closeCameraImagePopup())
        # self.box.add_widget(self.btn_mvp)
        # self.box.add_widget(self.btn_startCamera)
        self.content.add_widget(self.box_outside)

    def on_dismiss(self):
        self.cameraimage.stop()
        print('on dismiss of popup is called!')

# load kv file after referenced class define scope
# from pathlib import Path
# kivy_folder_path = Path("d:/wodo/wodo/")
# kivyfile = kivy_folder_path / "wodo.kv"
kv = os.path.join(r'd:/wodo/wodo/wodo.kv')
with open(kv, encoding='utf8') as f:
    Builder.load_string(f.read())
"""
APP MAIN BODY
"""
usb_stop_event = threading.Event() # control if trigger predicting porcess by usb singals
# APPSTATE = 'START' # reflect on/off of usb_stop_event
camera_stop_event = threading.Event() # clear register holding reference
# predict_stop_event = threading.Event()
# app_state = 'READY'
class WodoApp(App):
    
    title = 'WODO MachineVsion Pro 2.0'
    cameraImagePopup= ObjectProperty()
    timecount = ObjectProperty()
    startwork = ObjectProperty()
    cameranum = ObjectProperty()
    csi = ObjectProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.count_total_inspected_number = 0
        self.count_total_ng_number = 0
        self.cameras = None
        self.worker = None
        self.click_cameras_button_once = False
   
    def showCameraImage(self, title, cam):
        self.cameraImagePopup = CalibratePop(title = title, cam = cam, auto_dismiss = False)
        self.cameraImagePopup.open()
        print('there are {} threading running!'.format(threading.active_count()))
    def closeCameraImagePopup(self):
        if self.cameraImagePopup:
            self.cameraImagePopup.dismiss()# close popup
            self.cameraImagePopup.cameraimage.stop()
    def build(self):
        ms = MenuScreen()
        self.icon = 'd:/wodo/wodo/data/icons/icn.ico'
        return ms # return root class with hiearchy widget
    # called before drawing root widget(screen) when run app
    # record program performanc profile
    def on_start(self):
        ''' profile code performance
            for analysis uncomment below code
        '''
        # record the executing log profiles
        #for log func performance
        # import cProfile
        # self.profile = cProfile.Profile()
        # self.profile.enable()

        
        # add time indicator
        self.root.timecount.add_widget(Timer())
        self.cnt = Counting()
        self.root.timecount.add_widget(self.cnt)
        # add model profile selector
        from modelprofiles import Modelsprofile
        self.mdp = Modelsprofile()
        self.root.modelsprofiles.add_widget(self.mdp)

        # valide sytem
        import subprocess
        # get platform type
        import platform
        if platform.system() == "Windows":
            current_machine_id = subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()
            self.valid(current_machine_id)

    '''
    def save_input_serial(self, btn):
        camstore = JsonStore(config.store_path_cam)
        camstore.put("cam", a = config.ca, b = config.cb, c = config.cc, d = config.cd)
        print("camera serial saved!")
    '''
    def setQuitBtnDisabled(self, onoff):
        # when usb_stop_event is set, to disable quit btn
        # preventing quit by accidents pressed
        self.root.qtbtn.disabled = onoff
    # switch test signal button on/off
    def set_test_signal_Disabled(self,onoff):
        self.root.btn_trigger_test_signal.disabled = onoff
    # set reboot button activate or not
    def set_reboot_button_disabled(self, onoff):
        self.root.rbtbtn.disabled = onoff
    def test_send_usb_drive_code(self): # test send usb drive code for camera capture image
        # test func 
        # warmup inference engine:
        cam_batch_code = ["B",0]
        error_code = 0
        self.worker.trigger_operation_callback(cam_batch_code,error_code)
        from time import time
        # try:
        print("------------START TEST ------------------------")
        # if config.test:
            # cam_batch_code = ["A",0]
            # error_code = 0
            # self.worker.trigger_operation_callback(cam_batch_code,error_code)
            # sleep(800/1000)
            
        start_time = time()
        for i in range(4):    
            cam_batch_code = ["B",i]
            error_code = 0
            self.worker.trigger_operation_callback(cam_batch_code,error_code)
            sleep(10/1000)

        print("-------------START END -------------------------")
        end_time = time()
        elapsed_time = end_time - start_time
        _,rest = divmod(elapsed_time,3600)
        _, senconds = divmod(rest,60)
        print("One batch inferenced time: {} s".format(senconds))
        # except:
        #     msg  = '设备没有准备好！请检查相机和USB是否启动！'
        #     self.alerting(msg, [])
        
        
         

    # main button func called    
    def start_camera_usb(self):# button camera click
        if not self.click_cameras_button_once:
            #self.root.start_cam_usb.background_color = (0,1, 0,1) # change green color
            self.root.startwork.disabled = False
            self.click_cameras_button_once = True
            if self.cameras is None:
                self.cameras = cameras.Cameras()
    # def reset_cameras(self):
    #     print("-----------reset cameras is called!-----------------")
    #     if self.cameras is not None:
    #         self.cameras = None

    def start_working(self):# button 'connecting' start usb connection
        if self.worker is None:
            #self.root.startwork.background_color = (0,1, 0,1)
            self.worker = worker.Worker(self.callback_update_stastic)
       
    def reboot(self):
        '''
        # reflesh or restart the CAMERA UPDATING IMAGES
        # print('start camera button is pressed!!')
        # config.testvalue = '1111'
        # print('i change global value as {}'.format(config.testvalue))
        sourcepath = r"d:\\wodo\\0100.png"
        # sourcepath = os.path.join(os.sep, "D:" + os.sep,"wodo",filename)
        # time.sleep(2000/1000.0)
        # cbg(sourcepath)
        # app = App.get_running_app()
        img = self.root.graph
        # img.source = ''
        img.source = sourcepath
        img.reload()
        '''
        # restart system for reloading cameras
        os.execv(sys.executable, ['python'] + sys.argv)
        
    
    def on_stop(self):
        ''' profile close '''
        # self.profile.disable()
        # self.profile.dump_stats('myapp.profile')
        global camera_stop_event
        camera_stop_event.set()
        # self.save_com_setting_to_storefile()
        sleep(3.0)#wait system to save sth
    '''
    def save_com_setting_to_storefile(self):
        # save camera serial numbers
        self.store_cam.put('cam',a=config.ca,\
            b = config.cb,c= config.cc,d=config.cd)
        self.store_com.put('com', port = config.comport,  brd = config.braudrate)
    # '''
   
    '''
    alerting handling
    '''
    def alerting(self, msg,*args):
        # Test camera alerting to plc
        # uncomments below line if needed
        # self.serialPort.Send('CA')
        if len(args) >0:
            if len(args) == 2:
                if args[1] == 'remove':
                    print('camera {} is lost...'.format(args[0]))
                    self.alert_plc_camera_lost(args[0])
                if args[1] == 'arrival':
                    # running single camera thread
                    print('camera {} arrival now!........'.format(args[0]))
            if len(args) == 1:
                if args[0] == 'cameraerror':
                    # change start main button color to red
                    self.root.startwork.background_color = (1,0,0,1)
                # self.runing_single_camera(args[0])
        global usb_stop_event
        # global ALERT
        # config.ALERT = True # do not excute event.set() in predict process
        usb_stop_event.set()# stop predict and train
        # self.setQuitBtnDisabled(False)
        # print('on open trigger')
        ctn_box = FloatLayout()
        # with ctn_box.canvas:
        #     Color(255, 0, 0, 1)
        #     Rectangle(pos=ctn_box.pos, size=ctn_box.size)

        ctn_msg = Label(text=str(msg),size_hint=(None,None),pos_hint={'x':0.5,'y':0.2})

        cls_btn = Button(text='知道了！',size_hint=(.25,.25),pos_hint={'x':0.35,'y':0})
        ctn_box.add_widget(ctn_msg)
        ctn_box.add_widget(cls_btn)

        def _update_rect(instance, value):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size
        alert = Popup(title='警告!',content= ctn_box, auto_dismiss=False,\
                        size_hint=(None,None), size=(1000,200))
        with alert.canvas.after:
            Color(255, 0, 0, .3)
            alert.rect = Rectangle(size=ctn_box.size, pos=ctn_box.pos)
            alert.bind(pos=_update_rect, size=_update_rect)

        cls_btn.bind(on_press=alert.dismiss)
        # cls_btn.bind(on_open=lambda x: alerting_cb_open())
        # cls_btn.bind(on_dismiss=lambda x: alerting_cb_dismiss())
        alert.open()

    def alert_plc_camera_lost(self, serial_number):
        for cam_id, serial in self.devices.items():
            if serial_number == serial:
                self.serialPort.Send(cam_id)
                print('Infored to plc {}'.format(cam_id))


    """
    Call back funcs
    """
    
    def callback_update_stastic(self, dataframe_list, cam_id ):# predict: cbg

        
        dataframe = np.array(dataframe_list)

        fig = plt.figure( dpi = 45) #figsize=(8, 8),

        plt.rcParams.update({'font.size': 22})

        grid = plt.GridSpec(4, 4, hspace=0.2, wspace=0.4)
        main_ax = fig.add_subplot(grid[:, 1:])
        y_hist = fig.add_subplot(grid[:, 0:1], xticklabels=['t-sn'], sharey=main_ax,title = 'Cam: '+ str(cam_id))
        # scatter points on the main axes
        # print(" shape monitor ------------------------------------")
        # print("data shape x: {} y: {} ".format( len(dataframe[0]), dataframe[1:].shape ))
        # for data in dataframe[1:]:
        try:
            main_ax.plot(dataframe[0], dataframe[1:].T, 'ok', markersize=3, alpha=0.2, color = 'red')
       
            color_set = ['red']* len(list(dataframe[1:]))
            y_hist.hist( dataframe[1:].T, 40, histtype='stepfilled', orientation='horizontal', color=color_set)
            y_hist.invert_xaxis()
            # convert plot image to variable
            fig = plt.gcf() # get current figure
            fig.set_size_inches(16, 8, forward=True)
        except:
            print("plot data error !!")
        #horizontal line as threshold reference line
        '''
        import matplotlib.lines
        import matplotlib.transforms as transforms
        lw=4 # line width
        offset2 = transforms.ScaledTranslation(0,lw/72./2., fig.dpi_scale_trans)
        trans2 = transforms.blended_transform_factory(
            fig.transFigure, main_ax.transAxes+offset2)
        l2 = matplotlib.lines.Line2D([0, 1], [1,1], transform=trans2,
                    figure=fig, color="#dd0000", linewidth=4, zorder=0)
        
        #add lines to canvas
        fig.lines.extend([l2,])
        '''

        # save buffer img file to data\
        filename = "graph_image_buffer" + str(cam_id) + ".png"
        filepath = os.path.join(workdir,'data', 'stastics',filename)
        plt.savefig(filepath, format = "png")
        # close fig after savefile for clear occupied memo
        plt.close(fig)
        # sourcepath = os.path.join(workdir,'data', filename)
        # sourcepath = r"d:\\wodo\\0100.png"
        time.sleep(500/1000.0)# left time for save file
        Clock.schedule_once(lambda *args: self._updatag(filepath,cam_id),1.0)
    def _updatag(self, sourcepath, camid): # update statistica graphs
        imga = self.root.grapha
        imgb = self.root.graphb
        imgc = self.root.graphc
        imgd = self.root.graphd
        # img.source = ''
        if camid == 0:
            imga.source = sourcepath
            imga.reload()
        if camid == 1: # cam id 1 and 2 (bc) has same view for target, share same threshold
            imgb.source = sourcepath
            imgb.reload()
        if camid == 2: # cam id 1 and 2 (bc) has same view for target, share same threshold
            imgc.source = sourcepath
            imgc.reload()
        if camid == 3:
            imgd.source = sourcepath
            imgd.reload()
         
    def callback_update_working_counter(self, ng_pos):
        # call back in if usb end info
        # calcu the ng number and inspected number after usb end info send
        # if end string 0001111000111000 send
        
        self.count_total_inspected_number += config.TARGET_SIZE
        self.count_total_ng_number += len(ng_pos)
        # update the ng pertentage
        self.cnt.caculate(self.count_total_inspected_number, self.count_total_ng_number)
        # self.cnt.ngcount = self.count_total_ng_number
        # global working_mode
        
    def callback_update_sample_counter(self):
        # if config.WORKING_MODE == 'TRAIN':
        config.sampleCount += 5
        if config.sampleCount < config.sample_current_Count_max + 5:
            self.cpb.set_value(config.sampleCount)
            print('called circle progress.........')
    def valid(self, machineid): # check local machine id fit predefined one
        machine_dev_id = '4C4C4544-0042-3410-8034-C4C04F385832' # my home pc 
        machine_test_id = '4C4C4544-0030-3410-8035-C6C04F4C5632' # dell device for custommer
        # '0A95CAEF-37EB-4711-BE61-94A357FC6CF1'
        if machineid == machine_dev_id:
            pass
        else:
            print("Illegal copy???")
            # sleep(10.0)
            App.get_running_app().stop()
''' APP MAIN ENTRY '''
if __name__ == '__main__':
    WodoApp().run()
