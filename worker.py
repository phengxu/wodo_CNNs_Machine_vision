# wraping all predict func here for prediction task 
# import predict
# , Measurement,Markimage, Sample, dataframe 
# from predict import Predict 


# import measurement
import markimage
import sample 
import dataframe 
import predict
# import multiprocessing as Pool 
# from multiprocessing.pool import ThreadPool
# from multiprocessing import cpu_count as cpu_count
# import concurrent.futures

import config 
from imageProcess import crop_img
import threading 
import numpy as np 
import copy
# import serial_rx_tx as serialPort

import plccom
from kivy.app import App

class Worker():
    def __init__(self, callback_update_stastic):
        # self.serialPort = serialusb
        # create task module instance
        self.plccom = plccom.Plccom(self.trigger_operation_callback)
        self.predicting = predict.Predict() # prediction task
        self.sampling = sample.Sample(coordins = self.load_coordins(), callback = self.callback_update_image ) # sample collecting task
        # self.measuring = measurement.Measurement() # measurement task with px and sqc inspections
        self.markimage = markimage.Markimage(self.callback_update_image)
        self.dataframe = dataframe.Dataframe(callback_update_stastic)
      
        self.reset_record_of_cameras()       
        
        # self.serialPort = usbserial
        self.coordins = self.load_coordins()
        
        # threading pool for prediction task
        # self.threadpool = ThreadPool(processes=cpu_count()) # only use 1 bz gil
       
        self.app = App.get_running_app()#.alerting("")
        # update prod output number
        self.total_checked = 0
        self.checked_ng_total = 0
        # self.e = concurrent.futures.ThreadPoolExecutor(4)
    def reset_record_of_cameras(self):
         # pred and dect ng result holdings
        self.re_c0 = [1]*config.TARGET_SIZE # camera 0 postion
        # print("initing target size in prediction is {}".format(config.TARGET_SIZE))
        self.re_c1 = [1]*config.TARGET_SIZE # camera 1 position
        self.re_c2 = [1]*config.TARGET_SIZE
        self.re_c3 = [1]*config.TARGET_SIZE

    def get_ng_count_total(self, ngstr):
        ng_count = 0
        for item in ngstr:
            if item == '0': # ng flag
                ng_count += 1
        self.checked_ng_total += ng_count
        return self.checked_ng_total
        
    ''' drive by usb func to trigger working '''
    """
    Call back funcs
    """
    def trigger_operation_callback(self,cam_batch_code,error_code):
        # fired by usb readloop from plccom object
        if cam_batch_code is None:
            if error_code == 1:
                self.app.alerting("Read incoming data error!")
            if error_code == 2:
                self.app.alerting("usb com port is not open!")
        else:
            # cb_update_image = self.callback_update_image
            # cb_update_stastice_grah = self.callback_upate_stastic
            # me = self.me # opencv measurement instance
            working_data = self._set_working_data(cam_batch_code) 
            working_data["callback_img"] = self.callback_update_image
            # for predict
            if working_data["img"] is None:
                print('image is not exist!.....')
            else:
                mode =  working_data["mode"]
                if config.SYSTEM_WORKING_MODE == "WORK":
                    if "m" in mode and "p" not in mode: # only measure
                        # working_data["pred_after_measure"] = False
                        # just call func of starting multi process for measurement operations
                        # working_data = self.measure(working_data)
                        # self.process_after_measurement(working_data)
                        pass
                       
                    if "p" in mode and "m" not in mode: # only predict
                        # working_data["pred_after_measure"] = False
                        # just start thread in prediction operations
                        self.start_predict(working_data, self.callback_send_predic_result)
                        # self.process_after_prediction(working_data)
                        # pass

                    if "p" in mode and "m" in mode: # measure and predict together
                        # set a flag for prediction after measurement
                        # working_data["pred_after_measure"] = True
                        # call measurement and then call predict to combine results
                        # call measurement first 
                        self.measure_and_predict(working_data)
                        # and then call predict.....
                        # self.worker.predict(working_data)
                                  
                if config.SYSTEM_WORKING_MODE == 'TRAIN':
                    self.sample_collecting(working_data)

    def callback_update_image(self, img, camid):
        if config.different_camera_pos_display:
            # waiting for top and side img completed and assambly together
            if camid == 0 or camid == 3: # top view img
                self.topview = img
                # print("---------------------------------------top view assigned----------------------------------")
            if camid == 1 or camid == 2: # side view img
                self.sideview = img
                # config.startblit = False
                # print("---------------------------------------side view assigned----------------------------------")
                # img for top side arrived, show both top and sidd
                # bz top and side grouped as some position
                config.V_STACK_IMGS = np.vstack((self.topview, self.sideview))
                # config.startblit = True
                # print("---------after vstack operation----------------")
        else:
            config.V_STACK_IMGS = img
    
       
    ''' main task func '''
    def sample_collecting(self, working_data):
        # threading.Thread(target = self.sampling.collecting,\
        #     args = (working_data,),daemon = True).start()
        self.sampling.collecting(working_data)

    def start_predict(self, working_data,send_back_results):
        imageptr = working_data["img"]
        cam_id = working_data["cam"]
        #crop image for prediction
        croped_imgs = crop_img(imageptr, self.coordins[cam_id], config.BATCH_SIZE)
        # prediction = []
        # time_cost_for_prediction = []
        working_data["img"] = croped_imgs
        # threading.Thread(target = self.predicting.predict, \
        #                     args = (working_data, send_back_results),\
        #                     daemon = False).start()
        # call predict module's predict method
        self.predicting.predict(working_data, send_back_results)
    
    def callback_send_predic_result(self, working_data):
        self.process_after_prediction(working_data)
      
    

    #######sub func '''
    
    def _set_working_data(self, cam_batch_code):
        cam_working_code = {}
        cm = config.CAM_WORKING_MODE # load from modelfile module
        # print("cam working mode".format(cm))
        if cam_batch_code[0] == "A":
            cam_working_code["cam"] = 0
            cam_working_code["batch"] = cam_batch_code[1]
            cam_working_code["img"]  = config.IMAGE0
            cam_working_code["mode"] = cm["a"]
           
        if cam_batch_code[0] == "B":
            cam_working_code["cam"] = 1
            cam_working_code["batch"] = cam_batch_code[1]
            cam_working_code["img"]  = config.IMAGE1
            cam_working_code["mode"] = cm["b"]
           
        if cam_batch_code[0] == "C":
            cam_working_code["cam"] = 2
            cam_working_code["batch"] = cam_batch_code[1]
            cam_working_code["img"]  = config.IMAGE2
            cam_working_code["mode"] = cm["c"]
           
        if cam_batch_code[0] == "D":
            cam_working_code["cam"] = 3
            cam_working_code["batch"] = cam_batch_code[1]
            cam_working_code["img"]  = config.IMAGE3
            cam_working_code["mode"] = cm["d"]
           
        return cam_working_code
   
    def process_after_prediction(self, working_data):
        predictions = working_data["predictions"]
        cam_id = working_data["cam"]
        batch_id = working_data["batch"]
        ng_pos = working_data["ng_pos"] #self.get_ng_pos(cam_id, predictions)
        # working_data["ng_pos"] = ng_pos
        # process ng results for usb communication
        self._update_ng_record(ng_pos,cam_id, batch_id)
        self.send_usb_info_if_end(cam_id, batch_id)
        # draw dataframe and updating img to wodo main screen
        self.markimage.send_image_back_to_update_after_predict(working_data)
        # prediction data to draw statistics table
        self.dataframe.make_graph_data(predictions, cam_id, batch_id)
    
    def _update_ng_record(self, ng_pos, cam_id,batch_id):
        batch_id_int = int(batch_id)
        # update ng_pos by step offset that decide by camera pos also
        if len(ng_pos) >0:
            # cutoff invalid ng pos by batchend and cutoff index
            if batch_id == config.BATCHEND:
                # need to cutoff invalid ng
                if config.CUTOFF_INDEX >0:
                    # delet invalide ng pos index
                    ng_pos = [index for index in ng_pos if index < config.CUTOFF_INDEX]
                                        
            for ngp in ng_pos:
                # map current batchid to all target pos puls offset pos
                # if batch_id == config.BATCHEND:
                all_ng_pos = ngp+ batch_id_int*config.BATCH_SIZE
                print("ng pos in udate 353 is {}".format(all_ng_pos))
                if cam_id == 0:
                    self.re_c0[all_ng_pos] = 0 #set as ng
                if cam_id == 1:
                    self.re_c1[all_ng_pos] = 0 #set as ng
                if cam_id == 2:
                    self.re_c2[all_ng_pos] = 0 #set as ng
                if cam_id == 3:
                    self.re_c3[all_ng_pos] = 0 #set as ng
    def send_usb_info_if_end(self,cam_id, batch_id):
        # print("----------cam code: {}, targetsize {}".format(config.ACTIVE_CAMERA_CODE,config.TARGET_SIZE))
        # cam_end_pos, batch_end_pos = self.get_end_cam_batch_pos(config.ACTIVE_CAMERA_CODE, config.TARGET_SIZE, config.BATCH_SIZE)
        if cam_id == config.CAMEND and batch_id == config.BATCHEND: # last batch and last camera positon
            self.send_usb_ng(self.re_c0,self.re_c1,self.re_c2,self.re_c3)
            self.reset_record_of_cameras()
    def send_usb_ng(self, r0, r1,r2,r3):
        # summary all cam record_update
        record_list =  []# reset record list as empty
        record_list.append(r0)
        record_list.append(r1)
        record_list.append(r2)
        record_list.append(r3)
        # convert to string and ready to send to serial usb
        ngflag = []
        for rec in record_list:
            count = 0
            for flag in rec:
                if int(flag) == 0:# this is ng flagship
                    ngflag.append(count)# add ng pos from all positon and all cam
                count += 1
        # delete duplicate ng position
        ng_flag_no_duplicate = list(dict.fromkeys(ngflag))
        #sort results ascend order and make string
        ng_flag_no_duplicate.sort()
        ng_flag_list = [1]*config.TARGET_SIZE# convert to plc process, 1 -- ok, 0-- ng
        for i in ng_flag_no_duplicate:
            ng_flag_list[i] = 0# 0 represent ng for plc program
        str_ng_s = ''.join(str(e) for e in ng_flag_list)
        # str_ng.insert(0,"02") # read string of ng
        # str_ng_s = ''.join(('02',str_ng,'03'))
        # send ng count and total checked to wodo cnt
        self.total_checked += len(str_ng_s)
        self.app.cnt.caculate(self.total_checked, self.get_ng_count_total(str_ng_s))
        # inform plc read string of ng eg. 020101010001000...02003
        print('----------'+str_ng_s+'----------------------')
        # test plc receiver, after test, comment it
        #str_ng_s = '00111100000011100010'
        #print('fake ng string 00111100000011100010')
        self.plccom.send(str_ng_s)#
    
    def load_coordins(self):
        #  global cali list had load in model profile setting
        coordins = []
        coordins_cam_0 = (
        config.cali_a_list["x"],\
        config.cali_a_list["y"],\
        config.cali_a_list["d"],\
        config.cali_a_list["h"],\
        config.cali_a_list["w"]
        )
        coordins.append(coordins_cam_0)
        ######## CAM1 (B) #####################
        # store save pos as bottom left origin
        # self.pos_b = config.store_cali_b
        coordins_cam_1 = (
        config.cali_b_list["x"],\
        config.cali_b_list["y"],\
        config.cali_b_list["d"],\
        config.cali_b_list["h"],\
        config.cali_b_list["w"]
        )
        coordins.append(coordins_cam_1)
        ######## CAM2 (C) #####################
        # store save pos as bottom left origin
        # self.pos_c = config.store_cali_c
        coordins_cam_2 = (
        config.cali_c_list["x"],\
        config.cali_c_list["y"],\
        config.cali_c_list["d"],\
        config.cali_c_list["h"],\
        config.cali_c_list["w"]
        )
        coordins.append(coordins_cam_2)
        ######## CAM3 (D) #####################
        # store save pos as bottom left origin
        # self.pos_d = config.store_cali_d
        coordins_cam_3 = (
        config.cali_d_list["x"],\
        config.cali_d_list["y"],\
        config.cali_d_list["d"],\
        config.cali_d_list["h"],\
        config.cali_d_list["w"]
        )
        coordins.append(coordins_cam_3)
        return coordins
     
   

from kivy.factory import Factory
Factory.register('worker',cls = Worker)

