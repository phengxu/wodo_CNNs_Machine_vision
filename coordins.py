import os
import sys
from pathlib import Path
from kivy.storage.jsonstore import JsonStore 
import config as cf 
import datainterface

class Coordins():
    workdir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data','prod','coordins')
    def __init__(self):
        self.coordins = None
        self.dataint = datainterface.DataInt()
        

    def check_coordin_fils_exist_otherwise_create_default_new_files(self, current_target):
        result = True
        # find if current corrding store file is exists
        path_dic = self._get_coordins_file_path(current_target)
        # current_coordin_path_dic["a"]
        for cam_id, path in path_dic.items():
            if Path(path).is_file(): # check if file is exist
                # if cam == "a":
                result &= self.load_coordins(cam_id,path)
            else: # otherwise to create file with target prod name
                Path(path).touch() # create file at path
                calistore = JsonStore(path)
                # put pos coording default values
                # bc and ad camera use different defualt coordins
                if cam_id == 'a' or cam_id == 'd': # top side view
                    calistore.put("pos", x = 12,y= 242, d = 37, h = 160, w= 141)
                    result &= self.load_coordins(cam_id, path)
                if cam_id == 'b' or cam_id == 'c': # top side view
                    calistore.put("pos", x = 12,y=242, d = 13, h = 284, w= 183)
                    result &= self.load_coordins(cam_id, path)
        return result
        
    def _get_coordins_file_path(self, pos_file_name):
        path= {}
        # dirpath = workdir#cf.store_path_cali
        # print("---------------check cordings path ---------")
        # print(dirpath)
        path["a"] =  os.path.join(Coordins.workdir,pos_file_name +'_a.json')
        path["b"] =  os.path.join(Coordins.workdir,pos_file_name +'_b.json')
        path["c"] = os.path.join(Coordins.workdir,pos_file_name +'_c.json')
        path["d"] = os.path.join(Coordins.workdir,pos_file_name +'_d.json')
        print("---------------check cordings path ---------{}".format(path["a"]))
        return path
    def load_coordins(self, cam_id, current_prod_file_name_path):
        # try:
        result = True    
        result,pos = self.dataint.get_coordins(current_prod_file_name_path)
        if not result:
            print(" return fales from get coordings")
            return False
        else:
            if cam_id == "a":
                ########## camera a pos ########################
                cf.cali_a_list = pos
                # cf.cali_a_list['y'] = pos['y']
                # cf.cali_a_list['d'] = pos['d']
                # cf.cali_a_list['h'] = pos['h']
                # cf.cali_a_list['w'] = pos['w']
            if cam_id == "b":
                ########## camera b pos ########################
                cf.cali_b_list = pos
                # cf.cali_b_list['y'] = pos['y']
                # cf.cali_b_list['d'] = pos['d']
                # cf.cali_b_list['h'] = pos['h']
                # cf.cali_b_list['w'] = pos['w']
            if cam_id == "c":
                ########## camera c pos ####################
                cf.cali_c_list = pos
                # cf.cali_c_list['y'] = pos['y']
                # cf.cali_c_list['d'] = pos['d']
                # cf.cali_c_list['h'] = pos['h']
                # cf.cali_c_list['w'] = pos['w']
            if cam_id == "d":
                ######### camera d pos ##########################
                cf.cali_d_list = pos
                # cf.cali_d_list['y'] = pos['y']
                # cf.cali_d_list['d'] = pos['d']
                # cf.cali_d_list['h'] = pos['h']
                # cf.cali_d_list['w'] = pos['w']
        return result

'''
def check_coordin_fils_exist_otherwise_create_default_new_files(self, prodname):
        result = True
        coordin_dit = {}
        coordin_dit["a"] = os.path.join(workdir,'data','prod',prodname+'_a.json')
        coordin_dit["b"] = os.path.join(workdir,'data','prod',prodname+'_b.json')
        coordin_dit["c"] = os.path.join(workdir,'data','prod',prodname+'_c.json')
        coordin_dit["d"] = os.path.join(workdir,'data','prod',prodname+'_d.json')
        print("=============coording file path---------")
        print(coordin_dic['a'])
        for camid,filepath in coordin_dit.items():
            if Path(filepath).is_file():
                result &= self.load_coordins(filepath)
            else:
                # create store file with prod name
                Path(filepath).touch()
                coordin_store = JsonStore(filepath)
                coordin_store.put("pos", x = 132, y=132,dis = 5, h = 50, w = 50)
                result &= self.load_coordins(camid, filepath)
        return result
    def load_coordins(self,camid, filepath):
        result = True
        coordins_dict = {}
        result, coordin = self.dataint.get_coordins(filepath)
        if result:
            if camid == 'a':
                config.cali_a_list = coordin
            if camid == 'b':
                config.cali_b_list = coordin
            if camid == 'c':
                config.cali_c_list = coordin
            if camid == 'd':
                config.cali_d_list = coordin
        return result
'''