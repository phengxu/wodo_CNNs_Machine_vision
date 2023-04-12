#global var define

IMAGE0 = None
IMAGE1 = None
IMAGE2 = None
IMAGE3 = None

FPS = 30 # kivy camera image update frequence
frame_rate = 30.0 # fixed camera working frame rate
CameraBaseImageRatio = 0.5
V_STACK_IMGS = None
# CAMERA_NUM = 1# camera number in same position sequence on inspection line(machine)
# THIS_CAMERA_POSITION = 0 # this camera position of sequence on line (0 is first)
TARGET_SIZE = 30 # total number of targets in one rank of leds
# TARGET_IMAGE_SIZE = 256
BATCH_SIZE = 5 # targets number in one image that captured by camera
BATCHEND = 0 # the last batch id for completing inspecting
CAMEND = 0 # the last cam id for completing inspecting
CUTOFF_INDEX = 0 # the cutoff pos index for valid image or ng pos
                 # bz target size not always divided by batchsize completely


RECORD = [] # holding the ng record for each rank leditems
STEP = 0 # holding the current step of led-rank movement, 0 start first setp

# store_path_base = r'd:\wodo\wodo\data'

# store_path_cali = r"d:\wodo\wodo\data\coordins"

# # calibarte global list
# x,y,d,h,w  --- pos x,y; d -distance between rect, h -height, w- width
cali_a_list = {}
cali_b_list = {}
cali_c_list = {}
cali_d_list = {}

SYSTEM_WORKING_MODE = 'WORK' # define system working mode switch between work or train
CAM_WORKING_MODE = {} # define cam use prediction or measuremnt or meas. after pred
ACTIVE_CAMERA_CODE ='' # define whicth cam are/is used

## camera thresholds ############
# ta = 0.0001# threshold for camera a
# tb = 0.0001
# tc = 0.0001
# # tc = 0.0001
# td = 0.0001

# slider adjuster for move distance when calibrating 
sliderCalibrate = 1

sampleCount = 0
# sampleCountMax = 10000
sample_current_Count_max = 100000

current_prod_name = ''
# model_folder_path = "d:/wodo/data/Model"
# model_side_front_path = ''
# model_side_back_path = ''
# model_top_surface_path = ''
# model_top_inside_path = ''

# on/off swith for test func of usb send code for drive camera capturing
# test = True

# decide if assambley different camera position's image to display
different_camera_pos_display = False

# Control toggle btw factory and engineer mode
camera_trigger_on = True