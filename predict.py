# call predict with argument name, eg, x = input, verbose = 0 etc.

# __all__ = ('Predict', )
from kivy.app import App
from kivy.storage.jsonstore import JsonStore
import numpy as np

#from keras.models import load_model
#import keras
import tensorflow as tf
from tensorflow import keras,image, convert_to_tensor 

# from tensorflow import Grahp, Session
from time import time
import os
from pathlib import Path
# import sys
# sys.path.insert(0, '/docs/')
import config
import datainterface
import pdb

workdir = os.path.join(os.path.dirname(os.path.abspath(__file__)))

class Predict(object):
    def __init__(self):
        '''
        # each model use its own session
        self.session_a = tf.Session()
        self.session_b = tf.Session()
        self.session_c = tf.Session()
        self.session_d = tf.Session()
        # each model as its own graph and sessions
        self.graph_a = tf.get_default_graph()
        self.graph_b = tf.get_default_graph()
        self.graph_c = tf.get_default_graph()
        self.graph_d = tf.get_default_graph()
        # set inference parameters
        self.opt_adam = keras.optimizers.Adam(lr=0.001,beta_1=0.9,beta_2=0.999,epsilon=1e-08,decay=0.0)
        '''
        self.model = None
        self.dataint = datainterface.DataInt()
        self.app = App.get_running_app()     
        # laod model file 
        result, filename = self._check_models()
        if result: # model file check ok
            # load thresholds after model is load success
            self._load_thresholds()
        else:
            msg =  "Model file %s not exist! " % filename
            self.app.alerting(msg)
                
       
    ''' main only predicton func and sub func '''
    def predict(self, working_data, cb_send_back_results):
        cam_id = working_data["cam"]
        croped_imgs = working_data["img"]
        start_time = time()
        predictions = self.model.predict_on_batch(self._make_tensor_from_croped_image(croped_imgs))
        end_time = time()
        elapsed = end_time - start_time
        _, rest = divmod(elapsed,3600)
        _, seconds = divmod(rest, 60)
        working_data["time"] = str(np.around(seconds*1000/int(config.TARGET_SIZE),3))
        #print(predictions)
        #pdb.set_trace()
        working_data["ng_pos"] = self._get_ng_pos(cam_id, predictions)
        working_data["predictions"] = predictions
        cb_send_back_results(working_data)
          

    def _make_tensor_from_croped_image(self, croped_imgs):
        imglist = []
        for croped_img in croped_imgs:
            # convert each img to tensor
            img = convert_to_tensor(croped_img)#np.expand_dims(croped_img, axis=0))
            # change to 3 channel gray to rgb
            tensor_3_channel = image.grayscale_to_rgb(img)
            # scale to [0,1] range
            scale_tensor = image.convert_image_dtype(tensor_3_channel,tf.float32) #tensor_3_channel /255.
            #print('tensor of image:{}'.format(scale_tensor))
            imglist.append(scale_tensor)
        return tf.stack(imglist) # pack to batch tensor
    
    def _get_ng_pos(self, cam_id, predict_results):
        # i=0
        ng_pos=[]
        #threshold = 1
        for i, prob in enumerate(predict_results):
            print("show prob from tensor using enumerate {}".format(*prob))
            #pdb.set_trace()
            if cam_id == 0 :# top surface
                if float(*prob) < float(self.threshold_top_surface):
                    ng_pos.append(i)
            if cam_id == 1:# side back
                if float(*prob) < float(self.threshold_side_front):
                    ng_pos.append(i)
            if cam_id == 2:# top surface
                if float(*prob) < float(self.threshold_side_back):
                    ng_pos.append(i)
            
            # detecting by measurement method
            if cam_id == 3:# top inside
                if float(*prob) < float(self.threshold_top_inside):
                    ng_pos.append(i)
            
        return ng_pos
       
    def _load_thresholds(self):
        # get cameras threshold value from model selection
        dic_threshold = self.dataint.get_predict_thresholds()
        self.threshold_side_front = dic_threshold['a']#storefile.get('predict')['threshold']['a']
        self.threshold_side_back =  dic_threshold['b']#storefile.get('predict')['threshold']['b']
        self.threshold_top_inside =  dic_threshold['c']#storefile.get('predict')['threshold']['c']
        self.threshold_top_surface =  dic_threshold['d']#storefile.get('predict')['threshold']['d']
        # self.px_threshold = config.px_threshold
        # self.sqc_threshold = config.sqc_threshold
   
    def _check_models(self):
        model_name = self.dataint.get_model_file_name()
        print("---------------model name from dataint ------{}".format(model_name))
        if  model_name is not "":
            return self._check_model_file_exist(model_name),'Model exist!'
        else:
            # self.error_info("[Predict]: model file name a is not found!")
            return False, 'Model file is not exist!'

    def _check_model_file_exist(self, file):
        result = True
        model_file_os_path = os.path.join(workdir,'data','Model',file)
        model_file_path = Path(model_file_os_path) #"d:",os.sep,"wodo","data","Model"
        print("---------------CHECKING MODEL FILE PATH---------------------------")
        print(model_file_path)
        if model_file_path.is_file(): # model file is exists
            result &= self.load_will_working_models(model_file_os_path)
        return result #self._get_model_file(camid,model_file)
            
                
    def load_will_working_models(self, model_path):
        try:
            self.model = keras.models.load_model(model_path)
            return True
        except:
            self.app.alerting("Load model file failed!")
            return False


    

from kivy.factory import Factory
Factory.register('predict',cls = Predict)
