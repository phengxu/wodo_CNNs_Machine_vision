from kivy.uix.gridlayout import GridLayout
# from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior
from kivy.storage.jsonstore import JsonStore
from kivy.app import App

import numpy as np
import os
import sys
from pathlib import Path


import config as cf 
import datainterface
import coordins

# get relative path of local file
workdir = os.path.dirname(os.path.abspath(__file__))
# model_file_path = os.path.abspath(os.path.join(fileDir,'data','Model'))
# model_file_path = r"d:\wodo\wodo\data\Model"

class Tslider(Slider): # adjust threshold for models
    def __init__(self, thres, name, lbl, **kwargs):
        super(Tslider, self).__init__(**kwargs)
      
        self.value = thres#float(thres)
        self.name  = name
        self.min = 0.0001
        self.max = 0.9999
        self.step = 0.01
        self.value_track = True
        self.value_track_color =  [0,1,1,1]
        self.lbl = lbl
     
    def on_touch_up(self, t): # override for set store value when touch released
        if self.collide_point(*t.pos):
            # cf.td = np.around(self.value,6)
            self.lbl.text = str(np.around(self.value,6))
            if self.name == 'a':
                cf.ta = self.value
                print(" threashold a set as {}".format(cf.ta))
            if self.name == 'bc':
                cf.tbc = self.value
                print(" threashold bc set as {}".format(cf.tbc))
            if self.name == 'd':
                cf.td = self.value
                print(" threashold d set as {}".format(cf.td))
            return False

class Sliderbox(BoxLayout):
    def __init__(self, tl, disable,**kwargs):
        super(Sliderbox, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.thres_list = tl
        self.disable = disable
        self.createwdgts()

    def createwdgts(self):
        boxa = BoxLayout(orientation = 'horizontal')
        lbla = Label(text = str(self.thres_list["a"]), size_hint = (.2,1))
        slda = Tslider(thres = self.thres_list["a"], name = 'a', lbl = lbla)
        slda.disabled = self.disable
        boxa.add_widget(lbla)
        boxa.add_widget(slda)

        boxb = BoxLayout(orientation = 'horizontal')
        lblb = Label(text = str(self.thres_list["b"]),size_hint = (.2,1))
        sldb = Tslider(thres = self.thres_list["b"], name = 'b', lbl = lblb)
        sldb.disabled = self.disable
        boxb.add_widget(lblb)
        boxb.add_widget(sldb)

        boxc = BoxLayout(orientation = 'horizontal')
        lblc = Label(text = str(self.thres_list["c"]),size_hint = (.2,1))
        sldc = Tslider(thres = self.thres_list["c"], name = 'c', lbl = lblc)
        sldc.disabled = self.disable
        boxc.add_widget(lblc)
        boxc.add_widget(sldc)

        boxd = BoxLayout(orientation = 'horizontal')
        lbld = Label(text = str(self.thres_list["d"]), size_hint = (.2,1))
        sldd = Tslider(thres = self.thres_list["d"], name = 'd', lbl = lbld)
        sldd.disabled = self.disable
        boxd.add_widget(lbld)
        boxd.add_widget(sldd)

        self.add_widget(boxa)
        self.add_widget(boxb)
        self.add_widget(boxc)
        self.add_widget(boxd)
# main body class
class Modelsprofile(BoxLayout):
    # from kivy.properties import StringProperty
    # mb = StringProperty("mb")
    def __init__(self, **kwargs):
        super(Modelsprofile, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        # self.currentmodel = currentmodel
        self.app = App.get_running_app()
        self.threshold_checking_code = ""
        self.activate_camera_code = ""
        self.dataint = datainterface.DataInt()
        self.coordins = coordins.Coordins()
        self.current_prod_name = ''#self.dataint._get_current_prod_name()
        self.createWidgts()


    def createWidgts(self):
        # create ScrollView
        scrlbox = BoxLayout(size_hint = (0.4,1))
        layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        # get all model profile jsonstore file
        from os import walk
        from os.path import basename, splitext
        f = []
        mypath = os.path.abspath(os.path.join(workdir,'data','prod'))   #r"d:\wodo\wodo\data\prod"
        for (_, _, filenames) in walk(mypath):
            f.extend(filenames)
            break
        if len(f) == 0:
            self.app.alerting("[Prod profile]没有发现产品信息！")
            # return False
        for i in f:
            # use file name as button text
            fn = splitext(i)[0]
            btn = ToggleButton(text = str(fn), group = 'mybtn', state = 'normal',size_hint_y=None, height=40)
            # temprory set this as default selection
            if btn.text == 'prod_20_5':
                btn.state = 'down'
                self.set_as_current_prod(btn)
            btn.bind(on_press = lambda x: self.set_as_current_prod(x))
            layout.add_widget(btn)
        scrl = ScrollView(size_hint=(1, None), size=(layout.width, layout.height*1.5), bar_width = 20)
        scrl.add_widget(layout)
        scrlbox.add_widget(scrl)
        self.add_widget(scrlbox)
       
    def set_as_current_prod(self, instance):
        # check if change current_prod_name
        print("called set as current prod func")
        if self.current_prod_name is '': # set current selection and check
            self.current_prod_name = str(instance.text)
            self.check_and_try_to_load_prod_settings(self.current_prod_name)
        elif self.current_prod_name == instance.text:
            pass
        elif self.current_prod_name != instance.text:
            prod_name = str(instance.text)
            self.check_and_try_to_load_prod_settings(prod_name)

    def check_and_try_to_load_prod_settings(self, prodname):
        # set temp prod to retrieve the data from store file
        # if pre condiciton checknig get error, set back to previous prod
        self.dataint.set_current_prod_name(prodname)
        
        if self._checking_target_size():
            # current_prod_name = instance.text
            # if self.check_modelfiles_exists_by_camcode(storefile):
            if self._checking_threshold_valid():
                # prod_name = instance.text
                if self.coordins.check_coordin_fils_exist_otherwise_create_default_new_files(prodname):
                    # all pre condition is meet, load configs
                    print("set config success...........")
                    self._set_config_params(prodname)
                else:
                    self.set_back_to_previous_prod()
                    print("check coordins failed")
            else:
                self.set_back_to_previous_prod()
                print("check threshold failed!")
        else:
            self.set_back_to_previous_prod()
            print("checking targe size failed!")

    def set_back_to_previous_prod(self):
        # checking condition failed! reset current pro file back to orignal
        # if self.current_prod_name is not '': 
        #     self.dataint.set_current_prod_name(self.current_prod_name)
        pass
    def alert_error(self, instance):
        instance.state = 'normal' # cancel the prod/target selection toggle button state to [no selection]
        self.app.alerting(self.error_info)

    def _set_config_params(self, prodname):
        # all pre condition is meet, set as current prod file
        self.current_prod_name = prodname
        cf.current_prod_name = prodname
        
        cf.ACTIVE_CAMERA_CODE = self.dataint.get_cam_active_code()
        cf.CAM_WORKING_MODE = self.dataint.get_cam_working_mode()
        # cf.NORMAL_WORKING_CAMERS_NUM = len(cf.ACTIVE_CAMERA_CODE)
        cf.TARGET_SIZE = self.dataint.get_target_size()
        cf.BATCH_SIZE = self.dataint.get_batch_size()
        # set batchend / camend / cutoff by active cam, targetsize and batchsize
        cf.BATCHEND = self.get_end_batch_pos(cf.TARGET_SIZE, cf.BATCH_SIZE)
        cf.CAMEND = self.get_end_cam_by_camcode(cf.ACTIVE_CAMERA_CODE)
        cf.CUTOFF_INDEX = self._get_cutoff_pos_index(cf.BATCH_SIZE, cf.TARGET_SIZE)
        
        # activate the main "start" button
        self.app.root.start_cam_usb.disabled = False
        # update the label of target size display
        self.app.root.target_size.text = str(cf.TARGET_SIZE)
        # print("{} is current target file".format(cf.current_prod_name))
        # print(" {} cameras is need to work".format(cf.NORMAL_WORKING_CAMERS_NUM))
        # print("{} camera need to be activate in system".format(activate_camera_code))
    def _checking_target_size(self):
        # result = True
        size = self.dataint.get_target_size()#storefile.get("target")["target_size"]
        if size not in [20,25,30,24,35]:
            self.app.alerting('illegal target size ' )#self.alerting("{} is illegal size!".format(size))
           
            return False
        else:
            # for f in model_file_name_list:
            # result &= self.check_files(storefile)
            cf.TARGET_SIZE = size
        #     # print("checking target size passed!")
        return True
    
    def get_end_batch_pos(self, target_size, batch_size):
        # count from 0
        if target_size % batch_size== 0:
            return int(target_size/batch_size) -1 
        else:
            return int(target_size//batch_size)
    def get_end_cam_by_camcode(self, active_camera_code):
        # get the end camid for sending usb signal for ng pos string
        if active_camera_code[-1:] == 'A':
            return 0
        if active_camera_code[-1:] == 'D': 
            return 3
        if active_camera_code[-1:] == 'C': # or active_camera_code == 'BC' or active_camera_code == 'C':
            return 2
        if active_camera_code[-1:] == 'B': # or active_camera_code == 'AB': # for test b camera only
            return 1
    def _get_cutoff_pos_index(self, batchsize,targetsize):
        # used for cutoff invalid croped img and update record ng pos
        if batchsize % targetsize ==0:
            # no need for cutoff
            return 0 #int(targetsize/batchsize)
        else:
            return ((targetsize//batchsize)+1)*batchsize - targetsize
   
    def _checking_threshold_valid(self):
        dic = self.dataint.get_predict_thresholds()
        a,b,c,d = dic['a'],dic['b'],dic['c'], dic['d']
        thresholds = {"A":a,"B": b,"C":c, "D":d }
        for k, value in thresholds.items():
            if value is not None:
                if value < 30.0 and value > -80.0:
                    pass
                else:
                    self.app.alerting("Illegal threshold found!")
                   
                    return False
        print("checking thres passed!")
        return True
    
    
    

