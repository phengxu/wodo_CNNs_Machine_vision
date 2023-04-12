# caliberation for camera to get image of targets
# image -- image from cameras
# width_box-- target box width
# height_box-- target box height
# distance -- distance between two box alongside horizontal axies
import cv2
import numpy as np
import copy
import config
def calibrate(image, w, h,d, x, y):
    # ensure pos point is interger values
    width_box = int(w)
    height_box = int(h)
    distance = int(d)
    x_box = int(x)
    y_box = int(y)
    if image is not None:
        img = image.GetNDArray()
        #print('image size array is {}'.format(img.shape))
        # image_width, image_height = img.shape[1], img.shape[0]
        #assert IMAGE_HEIGHT == self.image_height, 'Image height set error!'
        img_c = copy.deepcopy(img)
        del image
        del img
        rgb_3 = np.tile(img_c[:,:,None],[1,1,3])
        img_arr_bgr = cv2.cvtColor(rgb_3, cv2.COLOR_RGB2BGR)#convert to cv2
        img_arr_bgr =  cv2.resize(img_arr_bgr, None, fx=0.5,fy=0.5)#,interpolation=cv2.INTER_AREA)
       
        interval = int(width_box + distance)
        # draw img with box mark
        
        # use recursive to draw
        box = {
            "x": x_box,
            "y": y_box,
            "w": width_box,
            "h": height_box
        }
        batchsize = copy.copy(config.BATCH_SIZE)
        img_arr_bgr = _add_box(img_arr_bgr, batchsize, interval, box)
        b5_p2 = (x_box + (batchsize-1)*interval + width_box, y_box + height_box)
        img = cv2.cvtColor(img_arr_bgr, cv2.COLOR_BGR2RGB)#convert to rgb cv2
        #print('scaled and color transfered img size is {}'.format(img.shape))
        #convert back to np array
        return np.asarray(img), b5_p2
    else:
        return None, None

def _add_box(img, batchsize, interval, box):
    xbox = box["x"]
    ybox = box["y"]
    width = box["w"]
    height = box["h"]
    for i in range(batchsize):
        box_pt_upper = xbox + i*interval, ybox
        box_pt_bottom = xbox + i*interval + width, ybox+height
        cv2.rectangle(img,box_pt_upper, box_pt_bottom, (0, 255, 0), 1)#draw a rect.
    return img 