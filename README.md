# wodo_CNNs_Machine_vision
Deploy CNNs model with four FLIR camera synchronously streaming target image

it's an automatic optical inspection ![application](https://github.com/phengxu/wodo_CNNs_Machine_vision/blob/main/data/icons/IMG_0746.JPG) for detecting bad part of LED bulb, using private multilayer Convolutional Neural Networks (CNNs) to train and deploy inferencing task; of course it can be used for other small parts inspection too, it depend on what cnn model you are going to train and deploy.

the application streaming image from four 5M pixel resolution FLIR machine vison camera/ model bfs-pge-50s5m-c with ethernet connection. the entire source code had compiled and run on real prodution enviornment for half year, was proved that it can run smoothly and stable on window platform with high performance, can inspecitng targets with speed 7K per hour.

the appliction controls 4 cameras, synchronously captures target image by different part/position, cameras is triggered by PLC program, and sent inpection/inference results througha  USB cable with braud rate 112500 to PLC program to executing the operation of pickuping bad parts. you can check real production video here <a href="https://www.youtube.com/embed/nzCObkuFY-E" target="_blank"><img src="https://www.youtube.com/embed/nzCObkuFY-E/0.jpg" akt="Multi -FLIR Cameras with CNNs Model deploy" width="560" height="315" border="10" /></a>

it suggests to configure camera with the fixed short exposure time within 2 ms and high framerate with high gain and ev compensation/target grey value to increase light sensitivity and eliminate blur effects from machine vibration, alternatively applying high power illuminating light source to enhence detailed capture capability with low gain and ev compensation for less image noise.

use conda install command to install dependencies, kivy/opencv/tensorflow... lib.

The camera driver is under spinnaker folder, of course you can use your own camera and replace camera class with your own defined one.

