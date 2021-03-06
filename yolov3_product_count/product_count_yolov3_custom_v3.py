# -*- coding: utf-8 -*-
"""product_count_yolov3_custom_v3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18Jzwo4WWRyK6JnXpOJr9q-iXSc46IbTu
"""

# Check if NVIDIA GPU is enabled
!nvidia-smi

from google.colab import drive
drive.mount('/content/gdrive')
!ln -s /content/gdrive/My\ Drive/ /mydrive
!ls /mydrive

#1) Clone the Darknet

!git clone https://github.com/AlexeyAB/darknet

#2) Compile Darknet using Nvidia GPU

# Commented out IPython magic to ensure Python compatibility.
# change makefile to have GPU and OPENCV enabled
# %cd darknet
!sed -i 's/OPENCV=0/OPENCV=1/' Makefile
!sed -i 's/GPU=0/GPU=1/' Makefile
!sed -i 's/CUDNN=0/CUDNN=1/' Makefile
!make

#3) Configure Darknet network for training YOLO V3

!cp cfg/yolov3.cfg cfg/yolov3_training.cfg

!sed -i 's/batch=1/batch=64/' cfg/yolov3_training.cfg
!sed -i 's/subdivisions=1/subdivisions=16/' cfg/yolov3_training.cfg
!sed -i 's/max_batches = 500200/max_batches = 4000/' cfg/yolov3_training.cfg
!sed -i '610 s@classes=80@classes=1@' cfg/yolov3_training.cfg
!sed -i '696 s@classes=80@classes=1@' cfg/yolov3_training.cfg
!sed -i '783 s@classes=80@classes=1@' cfg/yolov3_training.cfg
!sed -i '603 s@filters=255@filters=18@' cfg/yolov3_training.cfg
!sed -i '689 s@filters=255@filters=18@' cfg/yolov3_training.cfg
!sed -i '776 s@filters=255@filters=18@' cfg/yolov3_training.cfg

# Create folder on google drive so that we can save there the weights
!mkdir "/mydrive/yolov3"

!echo "pot" > data/obj.names
!echo -e 'classes= 1\ntrain  = data/train.txt\nvalid  = data/test.txt\nnames = data/obj.names\nbackup = /mydrive/yolov3' > data/obj.data
!mkdir data/obj

!ls /mydrive/yolov3/

!cp cfg/yolov3_training.cfg /mydrive/yolov3/yolov3_testing.cfg
!cp data/obj.names /mydrive/yolov3/classes.txt

# Download weights darknet model 53
!wget https://pjreddie.com/media/files/darknet53.conv.74

#4) Extract Images

#The images need to be inside a zip archive called "images.zip" and they need to be inside the folder "yolov3" on Google Drive

!unzip /mydrive/yolov3/images.zip -d data/obj

#6) Start the training

import glob
images_list = glob.glob("data/obj/*.jpg")
print(images_list)

with open("data/train.txt", "w") as f:
    f.write("\n".join(images_list))

# Start the training
!./darknet detector train data/obj.data cfg/yolov3_training.cfg darknet53.conv.74 -dont_show

#testing
!ls "data/obj.data"

#prediction and testing

!cp "/content/darknet" -r "/content/gdrive/MyDrive/yolov3"

#!./darknet detector test "data/obj.data" "cfg/yolov3_training.cfg" "/content/gdrive/MyDrive/yolov3/yolov3_training_last.weights" '/content/gdrive/MyDrive/yolov3/pot0.jpg'

!ls '/content/gdrive/MyDrive/yolov3'

#prediction, detection, and product count

import cv2
import numpy as np
import glob
import random
from google.colab.patches import cv2_imshow

#weights ='/content/gdrive/MyDrive/yolov3/yolov3_training_1000.weights'
weights ='/content/gdrive/MyDrive/yolov3/yolov3_training_last.weights'

cfg = '/content/gdrive/MyDrive/yolov3/yolov3_testing.cfg'
#dataset ='/content/gdrive/MyDrive/yolov3/pot0.jpg'

# Images path
img_path = '/content/gdrive/MyDrive/yolov3/input/images_orig/thumbnail_image002.jpg'

# Load Yolo
net = cv2.dnn.readNet(weights, cfg)

# Name custom object
classes = ["pot"]

layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
colors = np.random.uniform(0, 255, size=(len(classes), 3))


img = cv2.imread(img_path)
img = cv2.resize(img, None, fx=0.4, fy=0.4)
height, width, channels = img.shape

# Detecting objects
blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

net.setInput(blob)
outs = net.forward(output_layers)

# Showing informations on the screen
class_ids = []
confidences = []
boxes = []
for out in outs:
    for detection in out:
        scores = detection[5:]
        class_id = np.argmax(scores)
        confidence = scores[class_id]
        if confidence > 0.3:
            # Object detected
            #print(class_id)
            center_x = int(detection[0] * width)
            center_y = int(detection[1] * height)
            w = int(detection[2] * width)
            h = int(detection[3] * height)

            # Rectangle coordinates
            x = int(center_x - w / 2)
            y = int(center_y - h / 2)

            boxes.append([x, y, w, h])
            confidences.append(float(confidence))
            class_ids.append(class_id)

indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
print(indexes)
font = cv2.FONT_HERSHEY_PLAIN
for i in range(len(boxes)):
    if i in indexes:
        x, y, w, h = boxes[i]
        label = str(classes[class_ids[i]])
        color = colors[class_ids[i]]
        cv2.rectangle(img, (x, y), (x + w, y + h), (0,0,255), 2)
        #cv2.putText(img, label, (x, y + 30), font, 3, color, 1)

print("no. of bounding boxes",len(indexes))
cv2.imwrite("/content/gdrive/MyDrive/yolov3/output/test2_thumbnail_image002.jpg", img)
cv2_imshow(img)

