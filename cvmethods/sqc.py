# func to use cv2 for measure size of target
import cv2
from kivy.app import App
from kivy.storage.jsonstore import JsonStore
import numpy as np

import math
import os 
import time

import config

# get store file by current prod setting 
# use store file data to config working cv2 params 
# sotre file name format:
#  prod file name xx_xx_xx, type -px , sqc
#  xx_xx_xx_type.json
# eg: pro_20_10_px.json

class Sqc():
    # workdir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data')
    def __init__(self):
        self.app = App.get_running_app()
        self.dataint = datainterface.DataInt()
        self._load_working_params(self.dataint)

    def _load_working_params(self, dataint)
        _, self.sqc_metric = dataint.get_measurement_metric_ratio()
        _, self.sqc_width = dataint.get_measured_reference_value()
        _, self.sqc_threshold = dataint.get_measured_threshold_value()
       
       
       
    ''' main only opence detecting method '''
    def detecting_sqc(self, working_data):#, cb_update_img, cb_update_ng,cb_update_usb):
        imgs = working_data["img"]
        cam_id = working_data["cam"]
        batch_id = working_data["batch"]
        results = [] # holding the measured data for judging if ng or pass
        # results= []
        results_pos = []
        single_time_list = []
        print("-----------imgs numbers----------{}".format(len(imgs)))
        for img in imgs:
            # process img and return results
            start = time.time()
            diff, top_point, y_highest = self.run_shenqiancha_inspection(img)
            end = time.time()
            timecost = end -start
            single_time_list.append(timecost)
            results.append(diff)
            results_pos.append([top_point, y_highest])
        # decide if ng
        ng_pos = []
        diffs = []
        print("-------------results from run shenqiancha--------------")
        print(results)
        if None in results:
            print("There are empty results")#len(results)>0:
            return False
        else:
            for i, r in enumerate(results):
                diffs.append(r)
                if r > self.sqc_threshold:
                    ng_pos.append(i)
        # define mark image data structure
        mark_dict ={
            "imgs":imgs,
            "results": results,
            "ngpos": ng_pos,
            "single_time": single_time_list,
            "cam_id": cam_id,
            "batch_id": batch_id,
            "measured_pos": results_pos
        }
        return mark_dict
    def run_shenqiancha_inspection(self, img):
        # print("------------sqc is called-------------")
        # print("pixel ratio metric: {}".format(pixelsPerMetric))
         
        if self.sqc_metric != 0.0:
            # get reference head dot and leadframe platform's horizontal line
            top_point, y_h = self.get_platform_point_line(img)
            # caculate differ between lines and dot
            diff_abs = abs(top_point - y_h)
            if diff_abs != 0 and self.sqc_metric != 0 and self.sqc_metric is not None:
                diff = diff_abs/self.sqc_metric
                return diff, top_point, y_h
            else:
                print("no diff found!") 
                return None, None, None 
    
   
    ''' sub func '''
    def get_platform_point_line(self, img):
        # get target top point and arc platform horizontal line
        # and calculate the distance between them
       
        # parameters for houglines
        horizontal_line_threshold = 5
        horizontal_line_min = 3 #5
        horizontal_line_max = 0
        kernel = (7,7)
        cnn_threshold = 100,200
        edges, cnts = get_contours_edges(img,kernel,cnn_threshold)
        # get top point on target body
        '''
        y_p  = []
        for e in cnts:
            for c in e:
                # print("get y cordin x/y:{},".format(c[0]))
                _, y = c[0]
                y_p.append(y)
                # print("x:{}, y:{}".format(x,y))
        # get highest y point
        top_point = min(y_p)
        '''
        # use circle to locate the top point of target
        # for circle shape of head
       
        circle = cv2.HoughCircles(image = img,method = cv2.HOUGH_GRADIENT,dp = 2,minDist = 20,\
                                param1=50,param2=100,minRadius=40,maxRadius=80)
        if circle is None:
            self.app.alerting("can not found circle target, pls check box position of calibration!")
            return
        top_point = self.find_top_point_of_head_circle_of_target(circle)
        # find all lines of horizontal
        # parameter: threshold get vote number for meet the conditons 
        lines_h = cv2.HoughLinesP(edges, rho = 1, theta = 1*np.pi/180, threshold = horizontal_line_threshold, \
            minLineLength = horizontal_line_min, maxLineGap = horizontal_line_max)
       
        # find the line represent top platform of mental bowl 
        highest_line = []
        # side_line = []
        for line in lines_h:
            for _,y1,_,y2 in line:
                if y1 == y2: # horizontal line 
                    highest_line.append(y1)
            
        # cut off duplicate value 
        y_value = list(dict.fromkeys(highest_line))
        y_value.sort()
        # print("---------sorted value--------------")
        # print(y_value)
       
        if len(y_value)>=2:
            for v in y_value:
                if v - top_point > 25.0: # dist small than 25 px, top side doubel line
                    print("-------------top point v return------------->{}/{}".format(top_point, v))    
                    return top_point, v
        if len(y_value) == 1:
            print("-------------top point v return------------->{}/{}".format(top_point, v))    
            return top_point, y_value[0]
        else:
            print("No line found!")
            return 0,0
    def find_top_point_of_head_circle_of_target(self, circle):
        circles_np = np.uint16(np.around(circle))
        print("------circles np----------------")
        print(circles_np)
        cp = []
        if circles_np is not None:
            for c in circles_np[0,:]:
                # for c in pts:
                print("------geting circle vaulue c in circle----------")
                print(c)
                if c[1] > 10: # get center y point and relative r value
                    cp.append([c[1], c[2]])
        # make to list for y point and r 
        y_list = []
        r_list = []
       
        for e in cp:
            y_list.append(e[0])
            r_list.append(e[1])
        # find the mininum y poit
        print("-----------r list element -------------")
        print(r_list)
        y_min_point = min(y_list)
        # get the r index from y point list
        index_for_r = 0
        for ypoint in y_list:
            if ypoint == y_min_point:
                index_for_r = index_for_r
                break
            else:
                index_for_r += 1
        # get r value of minimun y point
        r_value_of_min_y_point = r_list[index_for_r]
        # center point y + radius equal to top point
        return int(y_min_point- r_value_of_min_y_point)

    def get_contours_edges(img, kernel, canny_threshold):
        # Otsu's thresholding after Gaussian filtering
        # the image is first filtered with a 5x5 gaussian kernel to 
        # remove the noise, then Otsu thresholding is applied.
        blur = cv2.GaussianBlur(img,kernel,0)
        _,th3 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        # get edges
        edges = cv2.Canny(th3,canny_threshold[0],canny_threshold[1])
        # plt.imshow(cv2.cvtColor(edges, cv2.COLOR_BGR2RGB))
        # plt.show()
        # from edges to get contour points
        cnts, _ = cv2.findContours(edges.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        return edges, cnts 
