#!/usr/bin/env python
# coding: utf-8

# 20200206 by Tianzi
# the size of the screen: (1358x726)
# location (fixed): (197,95) size (rescaleble) (853,468)
# x*screenwidth-197,y*screenheight-95
#

# 2/18/2020 by tianzi
# change work flow to fit the rate dropping problem
# step 1: extract all image from the video, get the number of images
# step 2: filter data from eye tracking file
# step 3: use the starttime, endtime from file Trials_1573754637958.txt
# step 3.1: calculate average time slot for each image,
# step 3.2: assign multiple eye tracking data to each image.
# step 4: generate video based on image and groundtruth


import cv2
import numpy as np
import progressbar

# step 1: extract all image from the video, get the number of images
def ImageExtraction(videoname,folder="./Data/testing/"):
    cap = cv2.VideoCapture(videoname)
    if (cap.isOpened() == False):
        print("Error opening video stream or file")

    #number of images
    ncount = 1
    cap = cv2.VideoCapture(videoname)

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    while (cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            cv2.imwrite(folder+"img/%04d.jpg" % ncount, frame)
            print(folder+"img/%04d.jpg" % ncount)
            ncount += 1
        else:
            break

    cap.release()
    return ncount,frame_width,frame_height

# step 2: filter data from eye tracking file
def CheckValidityLines(filename):
    lineList = [line.rstrip("\n").split(',') for line in open(filename)]
    t_filter = list(filter(lambda x: x[0] == "Valid" and float(x[4]) <= 1 and float(x[5]) <= 1, lineList))
    return t_filter

# step 3: use the starttime, endtime from file Trials_1573754637958.txt to generate groundtruth_rect.txt
def GroundTruth(eyetrackingdata, starttime,endtime,imagecount,out_groundtruth_file):
    arr_out_rect = []
    # step 3.1: calculate average time slot for each image,
    # each image has time:
    interval=float(endtime-starttime)/imagecount
    #print(interval)
    screen_width = 1358
    screen_height = 726
    screen_left=100#197
    screen_top=95#95
    inidiameter=4.0
    eyegaze_x,eyegaze_y=0,0
    # valid line index of the eye tracker data file
    t_index = 0

    # step 3.2: assign multiple eye tracking data to each image.
    for i in range (0,imagecount):
        # average position
        t_x = 0.0
        t_y = 0.0
        t_n = 0.0
        diameter_l = inidiameter
        diameter_r = inidiameter
        #print(starttime + interval*i)
        while t_index< len(eyetrackingdata) and int(eyetrackingdata[t_index][11]) <= starttime + interval*(i+1):
            left_x = float(eyetrackingdata[t_index][4])
            left_y = float(eyetrackingdata[t_index][5])
            right_x = float(eyetrackingdata[t_index][6])
            right_y = float(eyetrackingdata[t_index][7])

            t_x += left_x
            t_y += left_y
            diameter_l = max(float(eyetrackingdata[t_index][9]), diameter_l)
            diameter_r = max(float(eyetrackingdata[t_index][10]), diameter_r)

            t_n += 1
            t_index += 1

        if np.isnan(diameter_l) or diameter_l < inidiameter:
            diameter_l = inidiameter
        if np.isnan(diameter_r) or diameter_r < inidiameter:
            diameter_r = inidiameter

        if t_n > 0:
            #eyegaze_x = int(screen_width * left_x - screen_left)
            #eyegaze_y = int(screen_height * left_y - screen_top)
            eyegaze_x = int(screen_width * float(t_x / t_n) - screen_left)
            eyegaze_y = int(screen_height * float(t_y / t_n) - screen_top)
            arr_out_rect.append([eyegaze_x, eyegaze_y, int(diameter_l * 100 - 400), int(diameter_r * 100 - 400)])
        else:
            arr_out_rect.append([eyegaze_x, eyegaze_y, int(diameter_l * 100 - 400), int(diameter_r * 100 - 400)])

    #print(len(arr_out_rect))
    # step 3.3 write the groundtruth rile.
    with open(out_groundtruth_file, 'w+') as the_file:
        for item in arr_out_rect:
            t_str = ','.join(map(str, item))
            the_file.write("%s\n" % t_str)
    return 0


# step 4: generate video based on image and groundtruth

def GenerateVideo(voutname,w,h,imgfolder,imagecount,out_groundtruth_file):
    bar = progressbar.ProgressBar(maxval=imagecount, \
                                  widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    lineList = []
    for line in open(out_groundtruth_file):
        lineList.append(list(map(int, line.rstrip("\n").split(','))))
    #print(len(lineList))
    out = cv2.VideoWriter(voutname, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10,(w, h))
    for i in range (0,imagecount):
        img=cv2.imread(imgfolder+"%04d.jpg" % (i+1))
        cv2.rectangle(img,
                      (lineList[i][0] - int(lineList[i][2] * 0.2),lineList[i][1] - int(lineList[i][3] * 0.2)),
                      (lineList[i][0] + int(lineList[i][2] * 0.2),lineList[i][1] + int(lineList[i][3] * 0.2)),
                      (0, 255, 0),
                      2)
        #cv2.imshow('Frame', img)
        out.write(img)
        bar.update(i + 1)
    bar.finish()
    out.release()
    cv2.destroyAllWindows()
    return 0


def main():
    fileindex = ['']#'1573754660363'
    taskindex ='A' #1
    trialindex='1' #'A'
    cameraindex='3'

    starttime = 1573754660378  # fileindex+50#1573754660364  #
    endtime = 1573754766404
    folder = "./Data/20191212_22/"#"./Data/testing/"


    out_groundtruth_rect = folder+"groundtruth_rect.txt"
    videoname = folder+"Camera"+cameraindex+"_task"+taskindex+'_trial' + trialindex + '_' + fileindex[0] + '.avi'

    vcount,w,h=ImageExtraction(videoname)
    #vcount,w,h=2213,1280,720
    t_filter=CheckValidityLines(folder+"Tobii_taskA_trial" + trialindex + "_" + fileindex + ".txt")
    GroundTruth(t_filter, starttime, endtime, vcount, out_groundtruth_rect)
    GenerateVideo(videoname.replace('.avi', '_out.avi'), w, h, folder+"img/", vcount, out_groundtruth_rect)
    print([vcount])
if __name__ == '__main__':
    main()





