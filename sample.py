# collecting sample by usb sending code
import scipy.misc as sm
from datetime import datetime
from imageProcess import crop_img, flip_image, change_img_color_format
import config
import os
import numpy as np
from numpy import newaxis
import datainterface

workdir = os.path.join(os.path.dirname(os.path.abspath(__file__)))

class Sample():
    def __init__(self,coordins, callback):
        self.savepath = os.path.join(workdir,'data','samples')#r'd:\wodo\sample_img'
        self.coordins = coordins
        self.callback = callback

    ''' main sampling function '''    
    def collecting(self, working_data):
        #imageptr, cam_id, batch_id, callback):
        imageptr = working_data["img"]
        cam_id = working_data["cam"]
        # batch_id = working_data["batch"]
        callback = working_data["callback_img"]
        # from PIL import Image as imgPro # alias name for preventing kivycamera Image class name conflict
       
        # working_data["img"] =  
        imgs= crop_img(imageptr,self.coordins[cam_id],config.BATCH_SIZE)
        imgs_expand_dims = []
        # saving img to specific diretory
        # try:
        # print("current sample count {}, count max {}".format(config.sampleCount, config.sample_current_Count_max))
        if config.sampleCount < config.sample_current_Count_max:
            for i,img in enumerate(imgs):
                fileName = str(cam_id) + "-"+str(i)+"-"+datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")+".jpg"
                fn = os.path.join(self.savepath, os.path.basename(fileName))
                # im = imgPro.fromarray(img)
                im = img[:,:,0]
                print(im.shape)
                # imgs_expand_dims.append(im)
                sm.imsave(fn,im)
                # im.save(fn)
                # i+=1
                print('file {} saved........with shape of {}'.format(fileName, im.shape))
            
        # change the format to 3 channel for grb for kivy blit func drawing
        working_data["img"] = change_img_color_format(imgs)
        h_imgs = np.hstack(tuple(img for img in flip_image(working_data)))
        # vstack_image = np.vstack((h_imgs))
        self.callback(h_imgs, working_data["cam"])
        # except Exception as ex:
        #     print("Saved file failed, bz of {}".format(ex))
from kivy.factory import Factory
Factory.register('sample',cls = Sample)   