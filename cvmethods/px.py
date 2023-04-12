import cv2
from kivy.app import App
from kivy.storage.jsonstore import JsonStore
import numpy as np

import math
import os 
import time

import config
import datainterface

class Px():
    def __init__(self):
         self.app = App.get_running_app()
         self._load_working_params(self.dataint) 
         self._load_houghcircle_params()

    def _load_working_params(self, dataint):
        self.px_metric, _ = dataint.get_measurement_metric_ratio()
        self.px_diameter, _ = dataint.get_measured_reference_value()
        self.px_threshold, _ = dataint.get_measured_threshold_value() 
        # load template
        self.template = self.dataint.load_template_for_px()
    
    def _load_houghcircle_params(self):
         # load param for px circle and rect matching
        px_cv_args = self.datatint.get_px_circle_arguments()

        self.mindist = px_cv_args["mindist"]
        self.param1 = px_cv_args["param1"]
        self.param2 = px_cv_args["param2"]
        self.minradius = px_cv_args["minradius"]
        self.maxradius = px_cv_args["maxradius"]
        # rectangle of center of reflective calvity of led frame
        self.minscale = px_cv_args["minscale"]
        self.maxscale = px_cv_args["maxscale"]
        self.number_of_template = self.px_cv_args["number_of_template"]   
    
    def detecting_px(self, working_data):#, cb_update_img, cb_update_ng,cb_update_usb): 
        
        imgs = working_data["img"]
        cam_id = working_data["cam"]
        batch_id = working_data["batch"]
        results = [] # holding the measured data for judging if ng or pass
        # results= []
        results_pos = []
        single_time_list = []
        for img in imgs:
            result = self.run_pianxin_inspection(img)
            results.append(result)
       
        # decide if ng
        ng_pos = []
        diffs = []
        print(results)
        for i, r in enumerate([re["diff"] for re in results]):
            diffs.append(r)
            if r > self.px_threshold:
                ng_pos.append(i)
        # update ng pos
        working_data["ng_pos"] = ng_pos
        # get result position of circle and rect 
        circle_poses = []
        circle_radius = []
        for _, circle_pos in enumerate([result["circle_coordin"] for result in results]):
            circle_poses.append(circle_pos["xy"])
            circle_radius.append(circle_pos["radius"])
        # get rectangle pos and w,h
        rect_poses = []
        rect_size = []
        for _, r in enumerate([result["rect"] for result in results]):
            rect_poses.append(r["xy"])
            rect_w = r["w"]
            rect_h = r["h"]
            rect_size.append([rect_w, rect_h])
        # define mark image data structure
        mark_dict ={
            "imgs":imgs,
            "ngpos": ng_pos,
            "single_time": single_time_list,
            "cam_id": cam_id,
            "batch_id": batch_id,
            "rect_pos": rect_poses,
            "rect_size": rect_size,
            "radius": circle_radius,
            "circle_pos": circle_poses,
            "results": diffs
        }
        return mark_dict
       
    def run_pianxin_inspection(self, img):
        # create few template for better matching effects
        resized_tmps, n_tmps = self.process_temp(self.template)
        # normalize src img for better match
        normalized_img = np.float32((img - np.mean(img))/np.std(img))
        # loop using template with diff size to get highest vote matching
        w, h, pt =self.get_matched_box(resized_tmps, normalized_img, n_tmps)
        
        # smooth for better detecting
        img = cv2.GaussianBlur(img, (3, 3), 1)
        # center_coording, r = find_circle(img, cimg)
        circles = cv2.HoughCircles(image = img,method = cv2.HOUGH_GRADIENT,\
            dp = 2,minDist = self.mindist,\
            param1=self.param1,\
            param2=self.param2,\
            minRadius=self.minradius,\
            maxRadius=self.maxradius)
        circles_np = np.uint16(np.around(circles))
        # print("---------------get circle np data------------")
        # print(circles_np)
        if circles_np is not None:
            # type_of_circle_radius = type(circles_np)
            # if type_of_circle_radius is int or type_of_circle_radius is float:
            for i in circles_np[0]: # error bz of treating an integer as an array
                # for i in j:
                if i[2]< 250: # radius of circle max permited 
                    center_points = i[0], i[1]
                    r = i[2]
            # calcu the diff y circle center to rect center
            # import math
            diff_pixel = abs(pt[1] - center_points[1] + math.ceil(h/2))
            if self.px_metric is not None and self.px_metric > 0:
                diff = diff_pixel/self.px_metric # pixel per metirc
            # return result and coordins of circle and rect for further draw mark on image
            results = {
                "diff": diff, 
                "circle_coordin":{"xy":center_points,"radius":r},
                "rect":{"xy":pt,"w":w,"h":h}}
            print("----------before return in px func-------------------")
            print(results)
            return results
        else:
            self.app.alerting("no circle found in px inspection")

         
    def process_temp(self, template):
       
        # normalize template and src img for better matching
        temp = np.float32((template - np.mean(template))/np.std(template))
        # resize template by diff size for better matching
        sz_ranges = np.linspace(self.minscale, self.maxscale, self.number_of_template)
        resized_tmps = [cv2.resize(temp, None, fx=i, fy=j)
                        for i in sz_ranges for j in sz_ranges]
        n_tmps = len(resized_tmps)

        return resized_tmps, n_tmps
    
    def get_matched_box(self, resized_tmps, normalized_img, n_tmps):
        
        for rs_tmp, k in zip(resized_tmps, range(n_tmps)):
            # print("--------match imgs shape ----------------")
            # print(rs_tmp.shape)
            # print(m_img.shape)
            
            ccorr = cv2.matchTemplate(normalized_img, rs_tmp, cv2.TM_CCOEFF_NORMED) # ccorr cost more time, but bad results? CCOEFF,CCORR
            # match_val, match_loc = cv2.minMaxLoc(ccorr)[1::2]
            _, match_val, _, match_loc = cv2.minMaxLoc(ccorr)
            best_match = 0
            if k == 0:
                best_match_val = match_val
                pt = match_loc
            if match_val > best_match_val:
                best_match_val = match_val
                best_match_loc = match_loc
                best_match = k
                pt = best_match_loc
        # get the best fit tmplt's height
        temp_best_fit = resized_tmps[best_match]
        w, h = temp_best_fit.shape[::-1]
        return w,h,pt
