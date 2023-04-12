# shared func for process image
import cv2
import PIL
import scipy.misc as sm
import numpy as np

import copy
import math

import config


def change_img_color_format(imgs):
        colored_imgs = []
        for img in imgs:
            # rgb3 = np.tile(img[:,:,None],[1,1,3])
            cimg = _change_mono_to_rgb_format(img)
            colored_imgs.append(cimg)
        return colored_imgs

def flip_image(working_data): 
        imgs = working_data["img"]   
        # flip all image upside down
        fliped_imgs = []
        for img in imgs:
            fliped_imgs.append(cv2.flip(img, 0))
        return fliped_imgs

 
''' smain func '''
def crop_img(imgptr, coordins, batchsize):
    # croped with padding border for same size
    img_half_original= _scale_half_size(imgptr)
    croped_imgs = _croped_by_coordins(img_half_original, coordins, batchsize)
    # for_predit = True
    # print("cropde for predict----------------")
    return _padding_border_imgs(croped_imgs)
# func process image before predict or measurement
def _scale_half_size(img_ptr):
    img_arr = img_ptr.GetNDArray()
    # resize image by half size consistent with calibrate coordins
    img_arr_c = copy.deepcopy(img_arr)
    #import cv2
    #   rgb_3 = np.tile(img_arr_c[:,:,None],[1,1,3])
    #   img_arr_bgr = cv2.cvtColor(rgb_3, cv2.COLOR_RGB2BGR)#convert to cv2
    img_arr_bgr = _change_mono_to_rgb_format(img_arr_c)
    ratio = config.CameraBaseImageRatio
    img_resize =  cv2.resize(img_arr_bgr, None, fx=ratio,fy=ratio)#,interpolation=cv2.INTER_AREA)
    return img_resize[:,:,0] # return one channel image

def _croped_by_coordins(img, coordins, batchsize):
    # call with tuples (x, y, distance, h, w)
    x_box = coordins[0]
    y_box= coordins[1]
    distance = coordins[2]
    height_box = coordins[3]
    width_box = coordins[4]
    interval =width_box + distance

    #   target_img = []
    croped_imgs = []
    #print('batchsize is:  ', config.BATCH_SIZE)
    # import copy
    # print('predict batchsize of loop is {}'.format(batchsize))
    for i in range(batchsize):
        # x_box += i*interval
        #croped = copy.deepcopy(img[y_upper:y_upper+h,x_upper:x_upper+w])
        croped = copy.deepcopy(img[ y_box:y_box + height_box,\
                                    x_box+i*interval:x_box+i*interval + width_box])
        # print('predict coordings  x{} y {} dis{} w{} h{}'.format(x_box,y_box,distance,width_box,height_box))
        croped_add_dim = croped[:,:,np.newaxis]# reshape size as x,x,1
        croped_imgs.append(croped_add_dim)
    # print("---------croped--before sending-----------")
    # print(croped_imgs[0].shape)
    return croped_imgs
# padding 5~6 batch size is ok, but for 10+ batch, the border is too large
# resize image without change ratio and then pading border
def _padding_border_imgs(croped_imgs):
    h, w, _ = croped_imgs[0].shape# all crop image has same size, get any one of them
    # print('cropped image has size{}'.format(croped_imgs[0].shape))
    pad_imgs = []
    for img in croped_imgs:
        pad_imgs.append(_padding_img(img, w,h))
    # resized_pad_imgs = []
    # for img in pad_imgs:
    return resize_croped_image(pad_imgs)

# sub func for padding border imgs func
def resize_croped_image(imgs):
        # measurement padding do not need add new dim!
        resize_imgs = []
        for et in imgs:
            ri = sm.imresize(et,(256,256))
            # if if_predict:
            ri_add_dim = ri[:,:,np.newaxis]
            # print('img add dim after image resize of target_img{}', format(ri_add_dim.shape))
            resize_imgs.append(ri_add_dim)
            # else: # only for measuere image process
            #     resize_imgs.append(ri)
        # print("----------resize after cropedd----------")
        # print(resize_imgs[0].shape)
        return resize_imgs

def _change_mono_to_rgb_format(img):
    # img = np.tile(img[:,:,None],[1,1,3])
    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)#convert to cv2

def _padding_img(img, w,h):
    # to padding img to square shape and resize to target size
    if w>h:# padding top and bottom
        padingpix = math.ceil((w-h)/2)#int((w-h)/2)
        img = cv2.copyMakeBorder(img, top = padingpix,bottom = padingpix,\
             left = 0,right = 0,borderType=  cv2.BORDER_REPLICATE)
        return img
    elif h>w: # padding left and right
        padingpix = math.ceil((h-w)/2)
        img = cv2.copyMakeBorder(img, top = 0,bottom = 0,\
             left = padingpix,right = padingpix, borderType= cv2.BORDER_REPLICATE)
        return img
    else: # same side, no need padding
        return img