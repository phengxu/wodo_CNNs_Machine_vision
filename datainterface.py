# data interface for store file data
# all other moduel file get jsonstore data 
# from this interface

# when change current prod in prod profile module, update config.current_prod_name
# put path with config.current_prod_name in each store getting functions for updating 
# the path for prod store

# lock the prod selection when working(predicting or measureing)
import os
import sys
import cv2
from kivy.storage.jsonstore import JsonStore
from kivy.app import App 
import config

workdir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data')

# get this file's current dir d:/wodo/wodo
class DataInt():
    current_prod_name = '' # for instance to get current 
    # current_prod_name = ''
    def __init__(self):
        self.sys = self._get_sys_store_file()
        self.current_prod_name = DataInt.current_prod_name
        self.app = App.get_running_app()
        # self.comstore = None
        # self.current_prod_store_name = self._get_current_prod_name()
        # storefile = self._get_current_prod_file()
    # def _get_current_prod_name(self):
    #     # each func get prod data must use this to get
    #     if self.current_prod_name is "":
    #         # get from store file
    #         fp = os.path.join(DataInt.workdir,'sys', 'current_prod.json')
    #         self.current_prod_name = JsonStore(fp).get('data')['current_prod']
    #         return self.current_prod_name

    #     else:
    #         return self.current_prod_name
    def set_current_prod_name(self, name):
        self.current_prod_name = name
        DataInt.current_prod_name = name

    def _get_current_prod_file(self):
        prod_name = self.current_prod_name +'.json'
        store_file_path = os.path.join(workdir,'prod', prod_name)
        print("------------prod file path for get current ----------{}".format(store_file_path))
        return JsonStore(str(store_file_path))
    def _get_sys_store_file(self):
        sys_store_file_path = os.path.join(workdir,'sys','sys.json')
        return JsonStore(sys_store_file_path)
    
    def get_template(self):
        pass

    def get_com_info(self):
        # storefile = self._get_current_prod_file()
        storefile = self._get_current_prod_file()
        return storefile.get('info')['com']
    def get_version_info(self):
        storefile = self._get_current_prod_file()
        return storefile.get('info')['version']
    def get_cam_active_code(self):
        storefile = self._get_current_prod_file()
        return storefile.get('active_cam')['cam_code']
    def get_cam_working_mode(self):
        storefile = self._get_current_prod_file()
        dic = {}
        dic['a'] = storefile.get('cam_mode')['a']
        dic['b'] = storefile.get('cam_mode')['b']
        dic['c'] = storefile.get('cam_mode')['c']
        dic['d'] = storefile.get('cam_mode')['d']
        return dic
    def get_target_size(self):
        storefile = self._get_current_prod_file()
        print("-----------store file type ---------------------")
        print(type(storefile))
        return storefile.get('target')['target_size']

    def get_batch_size(self):
        storefile = self._get_current_prod_file()
        return storefile.get('target')['batch_size']

    def get_model_file_name(self):
        storefile = self._get_current_prod_file()
        #dic = {}

        return storefile.get('model')
        # dic['b'] = storefile.get('model')['b']
        # dic['c'] = storefile.get('model')['c']
        # dic['d'] = storefile.get('model')['d']
        # return dic
    # def _get_model_file_name_for_camera_a(self,prodstore):
        
    #     try:
    #         name = prodstore.get('model')['a']
    #     except:
    #         return False, None
    #     return True, name


    def get_predict_thresholds(self):
        storefile = self._get_current_prod_file()
        dic = {}
        dic['a'] = storefile.get("predict")["threshold"]["a"]
        dic['b'] = storefile.get('predict')['threshold']['b']
        dic['c'] = storefile.get('predict')['threshold']['c']
        dic['d'] = storefile.get('predict')['threshold']['d']
        return dic

    ''' MEASUREMENT PARAMS '''
    def get_measure_metric_ratio(self):
        storefile = self._get_current_prod_file()
        # dic = {}
        px = storefile.get('measurement')['metric_ratio']['px']
        sqc = storefile.get('measurement')['metric_ratio']['sqc']
        return px, sqc
    def load_template_for_px(self):
        path= os.path.join(workdir, 'cv2template','temp1.png')
        # print(path)
        try:
            tmp = cv2.imread(path,0)
        except:
            print("temp file is not exist!")

        return tmp
    def get_px_circle_arguments(self):
        storefile = self._get_current_prod_file()
        dic = {}
        dic['mindist'] = storefile.get('measurement')['px_circle_arguments']['mindist']
        dic['param1'] = storefile.get('measurement')['px_circle_arguments']['param1']
        dic['param1'] = storefile.get('measurement')['px_circle_arguments']['param2']
        dic['minradius'] = storefile.get('measurement')['px_circle_arguments']['minradius']
        dic['maxradius'] = storefile.get('measurement')['px_circle_arguments']['maxradius']
        return dic
    def get_measure_template_scale(self):
        storefile = self._get_current_prod_file()
        pass
    def get_measure_diameter_width(self):
        storefile = self._get_current_prod_file()
        diameter = storefile.get('measurement')['physic_reference_value']['px_diameter']
        width = storefile.get('measurement')['physic_reference_value']['sqc_width']
        return diameter, width

    def get_measure_threshold(self):
        storefile = self._get_current_prod_file()
        pass
    
    ''' GET SYS INFO '''
    def get_com_port(self):
        sys_store = self.sys
        return sys_store.get('data')['port']
    def get_com_bdr(self):
        return self.sys.get('data')['brd']
    def get_cam_ser(self):# get camera register serials 
        dic = {}
        dic['a'] = self.sys.get('data')['cam']['a']
        dic['b'] = self.sys.get('data')['cam']['b']
        dic['c'] = self.sys.get('data')['cam']['c']
        dic['d'] = self.sys.get('data')['cam']['d']
        return dic
    ''' COORDINS '''
    def get_coordins(self, path):
        # called by prodfile to give path of specific pos file
        result = True
        dic = {}
        print("----get coordins path -------{}".format(path))
        # try:
        path = str(path)
        x = JsonStore(path).get('pos')['x']
        y = JsonStore(path).get('pos')['y']
        d = JsonStore(path).get('pos')['d']
        h = JsonStore(path).get('pos')['h']
        w = JsonStore(path).get('pos')['w']
        # except:
        #     self.app.alerting("Read json coordins file erros!")
        #     result = False
        #     return result, dic
        dic['x'] = x
        dic['y'] = y
        dic['d'] = d
        dic['h'] = h
        dic['w'] = w
        return result,dic

    def save_cali_pos_to_storefile(self, camid):
        storefile = self._get_current_cali_storefile(camid)
        if camid == 'cam0':
            
            self._save_pos_value_to_jsonstore_file(config.cali_a_list,storefile)
        if camid == 'cam1':
            # storefile = self.get_current_cali_storefile("1"):
            self._save_pos_value_to_jsonstore_file(config.cali_b_list,storefile)
        if camid == 'cam2':
            # storefile = self.get_current_cali_storefile("2"):
            self._save_pos_value_to_jsonstore_file(config.cali_c_list,storefile)
        if camid == 'cam3':
            # storefile = self.get_current_cali_storefile("3"):
            self._save_pos_value_to_jsonstore_file(config.cali_d_list,storefile)
    def _get_current_cali_storefile(self, cam):
        if cam == "cam0":
            current_target = config.current_prod_name + "_a.json"
            # path= os.path.join(workdir,'data','prod','coordins', current_target)
            # return JsonStore(path)
        if cam == "cam1":
            current_target = config.current_prod_name + "_b.json"
            # path= os.path.join(workdir,'data','prod','coordins', current_target)
            # return JsonStore(path)
        if cam == "cam2":
            current_target = config.current_prod_name + "_c.json"
            # path= os.path.join(workdir,'data','prod','coordins', current_target)
            # return JsonStore(path)
        if cam == "cam3":
            current_target = config.current_prod_name + "_d.json"
        path= os.path.join(workdir,'prod','coordins', current_target)
        return JsonStore(path)

    def _save_pos_value_to_jsonstore_file(self, pos_value, store):

        try:
            store.put('pos', x = pos_value["x"],\
                            y = pos_value["y"],\
                            d = pos_value["d"],\
                            h = pos_value["h"],\
                            w = pos_value["w"])
        except:
            print("Save pos value to json failed!")

