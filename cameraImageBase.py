# for calibrate box to get image of camera 
# import kivy 
from kivy.uix.image import Image
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock, mainthread
from kivy.graphics.texture import Texture

import os
import numpy as np
import time
import cv2
import copy

import config
import calibrate
import datainterface
# get relative path of local file
# this_this_file_path = os.path.abspath(__file__)
workdir = os.path.dirname(os.path.abspath(__file__))

class CameraImageBase(Image):
    
    def __init__(self, coordins, cam_id):
        super(CameraImageBase, self).__init__()
        self.b5_p2 = (1224,200) # displied image size box border position
        self.cam_id = cam_id
        self.coordins = coordins
        self.load_coordins(self.coordins)
        self.setimage(self.cam_id)
        self.height_global_img = None
        self.dataint = datainterface.DataInt()


    def load_coordins(self,coordins):
        self._x = coordins['x'] # Image class has its own attribute x
        self._y = coordins['y']
        self.d = coordins['d']
        self.w = coordins['w']
        self.h = coordins['h']
    def setimage(self, camid):
        if camid == 'cam0':
            self.image = config.IMAGE0
        if camid == 'cam1':
            self.image = config.IMAGE1
        if camid == 'cam2':
            self.image = config.IMAGE2
        if camid == 'cam3':
            self.image = config.IMAGE3

    def minusDistance(self):
        if self.image is not None:
            if self.d >= -50:
                self.d -= config.sliderCalibrate
    def addDistance(self):
        if self.b5_p2 is not None and self.image is not None:
            if self._x + self.d*4+self.w*5 +20<1210.0:
                self.d += config.sliderCalibrate
    def moveleft(self):
        if self.image is not None:
            if self._x >10:
                self._x -= config.sliderCalibrate
    def moveright(self):
        # the 5th box leftmost point pos over imagesize width
        if self.image is not None:
            if self._x + self.d*4+self.w*5<1210.0:
                self._x += config.sliderCalibrate
    def moveup(self): # button move down
        
        if self.image is not None:
            if self._y + self.h + 10 < self.height_global_img:
                self._y += config.sliderCalibrate
                print("-----------move down----------{}".format(self._y + self.h))
                print("----------global height--------{}".format(self.height_global_img))
            # sleep(100/1000.0)
    def movedown(self): # button move up
        if self.image is not None:
            if self._y >10:
                self._y -= config.sliderCalibrate
    def add_box_width(self):
        if self.image is not None:
            if self._x + self.d*4 + self.w*5 +20 <1210.0:
                self.w += config.sliderCalibrate
    def reduce_box_width(self):
        if self.image is not None:
            if self.w >=2:
                self.w -= config.sliderCalibrate
    def add_box_height(self):
        if self.image is not None:
            if self._y + self.h + 10< 479.0:
                self.h += config.sliderCalibrate
    def reduce_box_height(self):
        if self.image is not None:
            if self.h > 2.0:
                self.h -= config.sliderCalibrate

    def savePos(self):
        # update current global cali value
        self.update_coordins(self.cam_id)
        # # change data through data interface
        # pos = {}
        # pos['x'] = int(self.x)
        # pos['y'] = int(self.y)
        # pos['d'] = int(self.d)
        # pos['h'] = int(self.h)
        # pos['w'] = int(self.w)

        # save change to store file

        # pos_storefile = self.get_current_store_file(self.cam_id)
        self.dataint.save_cali_pos_to_storefile(self.cam_id)
        # self.update_jsonstore_file(self.get_current_store_file(self.cam_id))

    def update_coordins(self, camid):
        if camid == "cam0":
            config.cali_a_list['x'] = int(self._x)
            config.cali_a_list['y'] = int(self._y)
            config.cali_a_list['d'] = int(self.d)
            config.cali_a_list['h'] = int(self.h)
            config.cali_a_list['w'] = int(self.w)
        if camid == "cam1":
            config.cali_b_list['x'] = int(self._x)
            config.cali_b_list['y'] = int(self._y)
            config.cali_b_list['d'] = int(self.d)
            config.cali_b_list['h'] = int(self.h)
            config.cali_b_list['w'] = int(self.w)
        if camid == "cam2":
            config.cali_c_list['x'] = int(self._x)
            config.cali_c_list['y'] = int(self._y)
            config.cali_c_list['d'] = int(self.d)
            config.cali_c_list['h'] = int(self.h)
            config.cali_c_list['w'] = int(self.w)
        if camid == "cam3":
            config.cali_d_list['x'] = int(self._x)
            config.cali_d_list['y'] = int(self._y)
            config.cali_d_list['d'] = int(self.d)
            config.cali_d_list['h'] = int(self.h)
            config.cali_d_list['w'] = int(self.w)


    # def get_current_store_file(self, cam):
    #     if cam == "cam0":
    #         current_target = config.current_prod_name + "_a.json"
    #         path= os.path.join(workdir,'data','prod','coordins', current_target)
    #         return JsonStore(path)
    #     if cam == "cam1":
    #         current_target = config.current_prod_name + "_b.json"
    #         path= os.path.join(workdir,'data','prod','coordins', current_target)
    #         return JsonStore(path)
    #     if cam == "cam2":
    #         current_target = config.current_prod_name + "_c.json"
    #         path= os.path.join(workdir,'data','prod','coordins', current_target)
    #         return JsonStore(path)
    #     if cam == "cam3":
    #         current_target = config.current_prod_name + "_d.json"
    #         path= os.path.join(workdir,'data','prod','coordins', current_target)
    #         return JsonStore(path)

    # def update_jsonstore_file(self, store):
    #     store.put('pos', x= int(self._x),\
    #                     y= int(self._y),\
    #                     dis =int(self.d),\
    #                     h= int(self.h),\
    #                     w = int(self.w))

    def _start(self):
        # img_c = copy.deepcopy(self.image.GetNDArray())
        img_nparr = np.array(copy.deepcopy(self.image.GetNDArray()))
        h,w = img_nparr.shape
        self.height_global_img = int(h*config.CameraBaseImageRatio) 
        # print("get image shape :{} ".format(img_nparr.shape))
        self.texture =Texture.create(size =(int(w*config.CameraBaseImageRatio),int(h*config.CameraBaseImageRatio)))# get half size to fit screen resolution
        #print('starting call updating interval')
        Clock.schedule_interval(self._update, 1/config.FPS)
    #stop display img
    def stop(self):
        Clock.unschedule(self._update)
    
    # @mainthread
    def _update(self,dt):
       
        # img, self.b5_p2 = calibrate(self.image, self.w, \
        #     self.h,self.d,self._x, self._y)
        if self.cam_id == 'cam0':
            if config.IMAGE0 is not None:
                img, self.b5_p2 = calibrate.calibrate(config.IMAGE0, self.w, \
                    self.h,self.d,self._x, self._y)
        if self.cam_id == 'cam1':
            if config.IMAGE1 is not None:
                img, self.b5_p2 = calibrate.calibrate(config.IMAGE1, self.w, \
                    self.h,self.d,self._x, self._y)
        if self.cam_id == 'cam2':
            if config.IMAGE2 is not None:
                img, self.b5_p2 = calibrate.calibrate(config.IMAGE2, self.w, \
                    self.h,self.d,self._x, self._y)
        if self.cam_id == 'cam3':
            if config.IMAGE3 is not None:
                img, self.b5_p2 = calibrate.calibrate(config.IMAGE3, self.w, \
                    self.h,self.d,self._x, self._y)


        ## add coordis to image
        '''
        font = cv2.FONT_HERSHEY_SIMPLEX
        coordingsTag = "x: "+str(self._x)+" y: "+str(self._y)+" d: " + str(self.d)\
                        + " h: " + str(self.h) + " w: " + str(self.w)
        cv2.putText(img,coordingsTag,(380,450), font,0.7,(255,100,0),1,cv2.LINE_AA)
        # FLIP IMAGE
        # flip_h_img = cv2.flip(img,1)
        # r_img = cv2.rotate(flip_h_img,cv2.ROTATE_180)
        '''
        v_img = cv2.flip(img, 0)

        if img is not None and self.b5_p2 != None:
            self.texture.blit_buffer(bytes(v_img), colorfmt='rgb', bufferfmt='ubyte')
            self.canvas.ask_update()
            del v_img