"""
POLLING CAMERA IMAGE automatic
"""
from kivy.app import App
import PySpin
from time import sleep
import config
from kivy.storage.jsonstore import JsonStore
import threading
import os
import datainterface

class SystemEventHandler(PySpin.InterfaceEvent):
    def __init__(self):
        super(SystemEventHandler, self).__init__()
        # self.cameras = None
        # self.system = system
    def OnDeviceArrival(self, serial_number):
        print('Device {} arrival...........'.format(serial_number))
        msg = 'Camera %s is connected' % serial_number
        App.get_running_app().alerting(msg)
        # self.cameras = Cameras()
    def OnDeviceRemoval(self, serial_number):
        msg = 'camera %s is losting!!.....' % serial_number
        App.get_running_app().alerting(msg)
    # def running(self):
    #     while True:
    #         sleep(10/1000.0)

class Cameras(object):
    def __init__(self):
        super(Cameras,self).__init__()
        self.dataint = datainterface.DataInt()
        self.system = PySpin.System.GetInstance()
        self.cam_list = self.system.GetCameras()
        # self.cam_id = cam_id
        # self.cam = cam
        # self.stopevent = stop_event
        self.keepalive = True
        self.app = App.get_running_app()
        self.camera_stop_event = threading.Event()
        self.cam_work_num = len(config.ACTIVE_CAMERA_CODE)
        # register sytemhandler to system for plug in/off notice
        self.SystemEventHandler = SystemEventHandler()
        self.system.RegisterInterfaceEvent(self.SystemEventHandler)
        # print('camera object init......')
        # try:
        if self.check_cameras_exist():
            self.create_cameras_threadings()
        else:
            # self.app.alerting("Cameras {} is lost ".format(str(self.lost_cameras)))
            self.app.root.start_cam_usb.background_color = (0,0,1,1) # change to blue color
            self.app.root.startwork.disabled = True
            # self.app.reset_cameras()
            # del self

    def create_cameras_threadings(self):
        for cam_id, cam_serial in self.register_cameras.items():
            if cam_serial is not "":
                cam = self.get_cam_by_serial(cam_serial)
                threading.Thread(target = self.acquiring_image,\
                    args = (cam_id, cam, self.camera_stop_event),\
                        daemon = True).start()
        # self.acquiring_image(cam_id = self.cam_id, cam= self.cam, system = self.system)
        # except PySpin.SpinnakerException as ex:
        #     print('Poweroff camera and plugin try again!')
        #     print(ex)
    def check_cameras_exist(self):
        result = True
        # get camera serials from store register
        # try: 
        
        self.register_cameras = {}
        # cp = os.path.join(config.store_path_base, 'cam_store.json') 
        # print("-------cam path ------------")
        # print(cp)
        # store = JsonStore(cp)
        camserial = self.dataint.get_cam_ser()
        # self.store_thr = JsonStore(config.store_path_thr)
        # get camera serial numbers
        # try:
        cam_a_serial  = camserial['a']#store.get('cam')['a']
        # print("----cam a serial from store-----{}".format(cam_a_serial))
        cam_b_serial  = camserial['b']#store.get("cam")["b"]
        # print("----cam b serial from store-----{}".format(cam_b_serial))
        cam_c_serial  = camserial['c']#store.get("cam")["c"]
        cam_d_serial  = camserial['d']#store.get("cam")["d"]
        # except:
        #     self.app.alerting("System Camera serial file is corrupted!!")
        if cam_a_serial is not None:
            self.register_cameras["a"] = cam_a_serial
        if cam_a_serial is not None:
            self.register_cameras["b"] = cam_b_serial
        if cam_a_serial is not None:
            self.register_cameras["c"] = cam_c_serial
        if cam_a_serial is not None:
            self.register_cameras["d"] = cam_d_serial
        # except:
        #     self.alerting("System Camera serial file is corrupted!!")
        print(self.register_cameras)
        # check camera is local system
        num_cams = self.cam_list.GetSize()
        print('there are {} cameras in system'.format(num_cams))
        # ensure to get interface and rerived a camera object
        if num_cams == 0:# no camera connected!
            # no camera in system
            self.app.alerting('[Check camera exist]: 系统没有发现相机!')
            return False
        if num_cams < self.cam_work_num:
            lost = self._get_lost_registered_camera_in_system()
            self.app.alerting("[Check camera exist]: \
                系统中相机数量不够,没有发现注册的相机{}!".format(':'.join(cam for cam in lost)))
                # enumerate(lost.items()))))
            return False
        if num_cams >= self.cam_work_num:
            # local cameras is more than needs,to check if register cameras in local system
            lost = self._get_lost_registered_camera_in_system()
            if len(lost)>0:
                        # self.lost_cameras.append(" ")
                self.app.alerting("[Check camera exist]: 系统中没有发现注册的相机{}!".format(':'.join(cam for cam in lost)))
                # result = False
                return False
            else:
                return True 
                
    def _get_lost_registered_camera_in_system(self):
        lost_cameras = []
        # get local cameras' serials
        devices_serial_from_camlist = []
        for cam in self.cam_list:
            # Retrieve device serial number that connected
            node_device_serial_number = PySpin.CStringPtr(cam.GetTLDeviceNodeMap().GetNode('DeviceSerialNumber'))
            if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
                device_serial_number = node_device_serial_number.GetValue()
                devices_serial_from_camlist.append(device_serial_number)
        # check one by one if registered in locals
        for cam_id, register_serial in self.register_cameras.items():
            if register_serial is not "":
                # print(cam_id, register_serial)
                # print("\n")
                if register_serial not in devices_serial_from_camlist:
                    lost_cameras.append(cam_id)
        # print(lost_cameras)
        return lost_cameras


    def get_cam_by_serial(self, serial) :
        for _, cam in enumerate(self.cam_list):
            # retriet cam by serial number
            # try:
            node_device_serial_number = PySpin.CStringPtr(cam.GetTLDeviceNodeMap().GetNode('DeviceSerialNumber'))
            if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
                if serial == node_device_serial_number.GetValue():
                    return cam
    def stop(self):
        # terminate the looping of collecting image
        self.camera_stop_event.is_set()
        # clear memories of cameras occupied
        self.system.UnregisterInterfaceEvent(self.SystemEventHandler)
        
        del self.SystemEventHandler
        self.cam_list.clear()
        self.system.ReleaseInstance()
        del self.system



    # def registerSystemEvent(self, system):
    #     system_event_handler = SystemEventHandler()
    #     system.RegisterInterfaceEvent(system_event_handler)
    #     del system_event_handler
        

    def acquiring_image(self, cam_id, cam, stop_event):
        try:
            cam.Init()
            # try:
            #Set acquisition mode
            # cam.registerSystemEvent(self.SystemEventHandler)
            nodemap = cam.GetNodeMap()
            
            # set fixed frame rate
           
            node_fr = PySpin.CFloatPtr(nodemap.GetNode('AcquisitionFrameRate'))
            if not PySpin.IsAvailable(node_fr) or not PySpin.IsWritable(node_fr):
                print('Unable to set acquisition frame rate. Aborting...')
                return False
            node_fr.SetValue(float(config.frame_rate))
             
            # set usr set file 0 as default
            node_file_selector = PySpin.CEnumerationPtr(nodemap.GetNode('FileSelector'))
            node_user_set_0 = node_file_selector.GetEntryByName('UserSet0')
            user_set_value = node_user_set_0.GetValue()
            node_file_selector.SetIntValue(user_set_value)
            # wait for system config settings
            sleep(200/1000)
            # start to capture image      
            cam.BeginAcquisition()
            # print('Acquiring images...heheh')
            # get frame rate node
            level = 0
            nodemap_applayer = cam.GetNodeMap()
            self.retrieve_frame_rate_node(nodemap_applayer.GetNode('Root'), level, cam_id)
                
        except PySpin.SpinnakerException as ex:
        #     print('Poweroff camera and plugin try again!')
        #     print(ex)
            App.get_running_app().alerting(str(ex),'cameraerror')

        # keepAlive = True
        # try:
        while True: #not stop_event:
            #wait moment to start polling new image
            # print(self.images[0])
            # print("i am alive...............")
            # if stopevent.is_set():
            #     keepalive = False
            # else:
            try:
                
                image = cam.GetNextImage()
                if image.IsIncomplete():
                    print('Image incomplete with image status %d ...' % image.GetImageStatus())
                    print(image.GetTimeStamp())
                    # print("image incoming...................")
                else:
                    '''
                    # Convert to mono8 asignt to kivy global img
                    '''
                    # Convert to mono8
                    image_converted = image.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)
                    if cam_id == 'a':
                        config.IMAGE0= image_converted
                        # image.Release()
                        self.app.root.btncalia.disabled =  False
                        self.app.root.camera_a_frame_rate.text = PySpin.CValuePtr(self.fr_node_cam0).ToString()[:4] + " fr"
                    if cam_id == 'b':
                        config.IMAGE1= image_converted
                        # image.Release()
                        self.app.root.btncalib.disabled =  False
                        self.app.root.camera_b_frame_rate.text = PySpin.CValuePtr(self.fr_node_cam1).ToString()[:4]+ " fr"
                    if cam_id == 'c':
                        config.IMAGE2= image_converted
                        # image.Release()
                        self.app.root.btncalic.disabled =  False
                        self.app.root.camera_c_frame_rate.text = PySpin.CValuePtr(self.fr_node_cam2).ToString()[:4]+ " fr"
                    if cam_id == 'd':
                        config.IMAGE3= image_converted
                        # image.Release()
                        self.app.root.btncalid.disabled =  False
                        self.app.root.camera_d_frame_rate.text = PySpin.CValuePtr(self.fr_node_cam3).ToString()[:4]+ " fr"
                    # clear buffer from camera
                    image.Release()
            except PySpin.SpinnakerException as ex:
                print('in image event polling images!')
                print(ex)
                App.get_running_app().alerting(ex, 'cameraerror')
                # keepAlive = False
                break
            sleep(10 / 1000.0)

        # except:
        #     print('Stop While loop failed!....')

    def retrieve_frame_rate_node(self, node, level, cam_id):
        try:
            # Create category node
            node_category = PySpin.CCategoryPtr(node)
            # Get and print display name
            # display_name = node_category.GetDisplayName()
            for node_feature in node_category.GetFeatures():
                if node_feature.GetDisplayName() == "Resulting Frame Rate":
                    if cam_id == "a":
                        self.fr_node_cam0 = node_feature
                        # return True
                    if cam_id == "b":
                        self.fr_node_cam1 = node_feature
                        # return True 
                    if cam_id == "c":
                        self.fr_node_cam2 = node_feature
                        # return True 
                    if cam_id == "d":
                        self.fr_node_cam3 = node_feature
                        # return True 
            
                # # # Ensure node is available and readable
                if not PySpin.IsAvailable(node_feature) or not PySpin.IsReadable(node_feature):
                    continue 
                    # print("Can not get frame rate feature or not readabel!.....")
             
                # # # Category nodes must be dealt with separately in order to retrieve subnodes recursively.
                if node_feature.GetPrincipalInterfaceType() == PySpin.intfICategory:
                    # if node_feature.GetDisplayName() == 'ResultingFrameRate':
                    self.retrieve_frame_rate_node(node_feature, level + 1, cam_id)

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            # return False
   
        
from kivy.factory import Factory
Factory.register('cameras',cls = Cameras)
