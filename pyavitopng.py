#!/usr/bin/env python
# coding: utf-8

# 20200206 by Tianzi
# the size of the screen: (1358x726)
# location (fixed): (197,95) size (rescaleble) (853,468)
# x*screenwidth-197,y*screenheight-95
#

import cv2
import numpy as np
fileindex = 1573754660363 #videofilename
taskindex = 1 


starttime = fileindex+50
out_groundtruth_rect="./Data/groundtruth_rect.txt"
lineList = [line.rstrip("\n").split(',') for line in
            open("./Data/testing/Tobii_taskA_trial" + str(taskindex) + "_" + str(fileindex) + ".txt")]


t_filter = list(filter(lambda x: x[0] == "Valid" and float(x[4]) <= 1 and float(x[5]) <= 1, lineList))
t_filter_len = len(t_filter)

print("Valid lines:")
print(t_filter_len)
arr_out_rect=[]

videoname = './Data/testing/Camera3_taskA_trial' + str(taskindex) + '_' + str(fileindex) + '.avi'
cap = cv2.VideoCapture(videoname)

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

screen_width=1358
screen_height=726
out = cv2.VideoWriter(videoname.replace('.avi', '_out.avi'), cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10,
                      (frame_width, frame_height))

# Check if camera opened successfully
if (cap.isOpened() == False):
    print("Error opening video stream or file")

ncount = 1
t_index = 0
# Read until video is completed
timestamps = 0
while (cap.isOpened()):
    # Capture frame-by-frame
    ret, frame = cap.read()
    if ret == True:
        timestamps = cap.get(cv2.CAP_PROP_POS_MSEC)
		
        t_time = starttime + timestamps
		
        t_x=0
        t_y=0
        t_n=0
        while t_index <= t_filter_len:
            if float(t_filter[t_index][11]) >= t_time:
                if t_n>0:
                    eyegaze_x = int(screen_width * float(t_x/t_n) - 197)
                    eyegaze_y = int(screen_height * float(t_y/t_n)-95)
                    arr_out_rect.append([eyegaze_x,eyegaze_y,23,28])
                break
            t_index += 1
			
            # get eyegaze position
            t_x += float(t_filter[t_index][4])
            t_y += float(t_filter[t_index][5])
            t_n +=1

        cv2.rectangle(frame, (eyegaze_x - 25, eyegaze_y - 25), (eyegaze_x + 25, eyegaze_y + 25), (0, 255, 0), 2)

        cv2.putText(frame, "Timestamp_v:" + str(t_time), (105, 105), cv2.FONT_HERSHEY_COMPLEX_SMALL, .7, (225, 0, 0))
        cv2.putText(frame, "Timestamp_e:" + t_filter[t_index][11], (105, 115), cv2.FONT_HERSHEY_COMPLEX_SMALL, .7,
                    (225, 0, 0))

        # Display the resulting frame
        cv2.imshow('Frame', frame)

        out.write(frame)
        ncount += 1

        # Press Q on keyboard to  exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    # Break the loop
    else:
        break
print("frames:")
print(ncount)
print(timestamps)

cap.release()
out.release()

cv2.destroyAllWindows()

with open(out_groundtruth_rect, 'a') as the_file:
    for item in arr_out_rect:
        t_str=','.join(map(str, item))
        the_file.write("%s\n" % t_str)





