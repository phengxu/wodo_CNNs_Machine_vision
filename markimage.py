# mark image with tag and reference line after task
import numpy as np
import cv2
import config 
from imageProcess import flip_image, change_img_color_format

# debug use, after debuging comments below import and setting 
import pdb

class Markimage():
    def __init__(self, callback):
        self.callback_update_img = callback
        # text on image arguments
         # set color arguments
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_size = 0.38
        self.distance = 18
        self.x = 10
        self.y = 200
        self.color = (255,255,255)
    ##### main func for worker to calling
    # mark image after perditions
    def send_image_back_to_update_after_predict(self, working_data):
        cam_id = working_data["cam"]
        h_imgs = np.hstack(tuple(img for img in self._mark_prediction(working_data)))
        self.callback_update_img(h_imgs, cam_id)  
    '''sub func'''
    def _mark_prediction(self, working_data):
        imgs = working_data["img"]
        # mark image with tag of time cost and probs
        color_imgs = change_img_color_format(imgs)
        working_data["img"] = color_imgs
        # imgs_box_added 
        working_data["img"] = self.add_box_if_ng(working_data)
        working_data["img"] = self.add_cam_batch(working_data)
        working_data["img"] = self.add_time_result(working_data)
        working_data["img"] = self.add_prediction_results(working_data)
        return flip_image(working_data)
    def add_box_if_ng(self, working_data):    
        # bgr_format_imgs = []
        imgs = working_data["img"]

        ng_pos = working_data["ng_pos"]
        print("----------------ng pos ---------")
        print(ng_pos)
        imgs_border_white =[]
        RED = [255,0,0]
        WHITE=[0,0,0]
        for img in imgs:
            img_border_white= cv2.copyMakeBorder(img,5,5,5,5,cv2.BORDER_CONSTANT,value=WHITE)
            imgs_border_white.append(img_border_white)

        # mark ng image with red border
        if len(ng_pos)>0:
            for index in ng_pos:
                img_border_red= cv2.copyMakeBorder(imgs[index],5,5,5,5,cv2.BORDER_CONSTANT,value=RED)
                # replace white border with red border
                imgs_border_white[index] = img_border_red
        return imgs_border_white
    def _mark_measurement(self, working_data):    
        type = working_data["measure_type"]
        mark_info = working_data["mark_info"]
        if type == "sqc":
            # mark image as sqc reference
            working_data["img"] = self._mark_sqc_images(mark_info)
        if type == "px":
            # mark image as px circle and rectangle
            working_data["img"] = self._mark_px_images(mark_info)
        # mark tag of camid and batch id and ng box
        working_data["img"] = self.add_box_if_ng(working_data)
        working_data["img"] = self.add_cam_batch(working_data)
        return working_data
        
    def add_cam_batch(self, working_data):
        # unpack working data
        cam_id = working_data["cam"]
        batch_id = working_data["batch"]
        imgs = working_data["img"]
       
        # start draw each img with tag
        taged_imgs = []
        # i = 0
        for img in imgs:
            tag1 = 'Cm/Btch: ' + str(cam_id) + "/" + str(batch_id)
            img1 = cv2.putText(img,tag1,(self.x,self.y), self.font,self.font_size,self.color,1,cv2.LINE_AA)
            taged_imgs.append(img1)
            # i += 1
        return taged_imgs
    def add_prediction_results(self, working_data):
       
        prob_added_imgs = []
        predictions = working_data["predictions"]
        # covert tensor to numpy array
        prob_list = predictions.numpy()
        
        # mark images
        i = 0
        imgs = working_data["img"]
        for img in imgs:
            prob_tag = 'Pro: ' + str(*prob_list[i])#[:8]
            img2 = cv2.putText(img,prob_tag,(self.x,self.y+self.distance),\
                 self.font,self.font_size,self.color,1,cv2.LINE_AA)
            prob_added_imgs.append(img2)
            i += 1
        return prob_added_imgs
    def add_time_result(self, working_data):
        time_add_imgs = []
        time = working_data["time"] # average time cost
        tag_time = 'Avg Time elapsed: ' + time
        imgs = working_data["img"]
        for img in imgs:
            # add time cost mark
            img_add_time = cv2.putText(img,tag_time,(self.x,self.y+2*self.distance),\
                 self.font,self.font_size,self.color,1,cv2.LINE_AA)
            time_add_imgs.append(img_add_time)
            
        return time_add_imgs
 