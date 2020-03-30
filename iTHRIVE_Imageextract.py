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
import os
import json

IMG_WIDTH=1280 
IMG_HEIGHT=720 
DELAY=50 #ms

# 2 degree fovea
# distance*tan(1)=0.01745
# screen is 9 inches, 0.2286 m
# size = (0.01745/0.2286)*1024
pupilsize=int(2*(0.01745/0.2286)*IMG_WIDTH)

# step 1: extract all image from the video, get the number of images
def ImageExtraction(videoname,folder):
    if not os.path.exists(folder+"/img/"):
        os.makedirs(folder+"/img/")
    cap = cv2.VideoCapture(videoname)
    if (cap.isOpened() == False):
        print("Error opening video stream or file")

    #number of images
    ncount = 0
    cap = cv2.VideoCapture(videoname)

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    while (cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            cv2.imwrite(folder+"img/%04d.jpg" % ncount, cv2.resize(frame,(IMG_WIDTH,IMG_HEIGHT)))
            print(folder+"img/%04d.jpg" % ncount)
            ncount += 1
        else:
            break

    cap.release()
    return ncount,frame_width,frame_height,IMG_WIDTH,IMG_HEIGHT

# step 2: filter data from eye tracking file
def CheckValidityLines(filename):
    print(filename)
    lineList = [line.rstrip("\n").split(',') for line in open(filename)]
    t_filter = list(filter(lambda x: x[0] == "Valid" and float(x[4]) <= 1 and float(x[5]) <= 1, lineList))
    return t_filter

# step 3: use the starttime, endtime from file Trials_1573754637958.txt to generate groundtruth_rect.txt
def GroundTruth(eyetrackingdata, starttime,endtime,imagecount,out_groundtruth_file,w_ratio=1.0,h_ratio=1.0):
    arr_out_rect = []
    # step 3.1: calculate average time slot for each image,
    # each image has time:
    interval=float(endtime-starttime)/imagecount
    #print(interval)
    screen_width = 1358
    screen_height = 726
    screen_left=100#197
    screen_top=50#95
    inidiameter=3.0
    eyegaze_x,eyegaze_y=0,0
    # valid line index of the eye tracker data file
    t_index = 0

    # step 3.2: assign multiple eye tracking data to each image.
    for i in range (imagecount-1):
        # average position
        t_x = 0.0
        t_y = 0.0
        t_n = 0.0
        diameter_l = inidiameter
        diameter_r = inidiameter
        #print(starttime + interval*i)
        while t_index< len(eyetrackingdata) and int(eyetrackingdata[t_index][11]) <= starttime + interval*(i+1)+DELAY:
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
            eyegaze_x = int((screen_width * float(t_x / t_n) - screen_left)*w_ratio)
            eyegaze_y = int((screen_height * float(t_y / t_n) - screen_top)*h_ratio)
        #arr_out_rect.append([eyegaze_x, eyegaze_y, int((diameter_l * 100 - 400)*w_ratio), int((diameter_r * 100 - 400)*h_ratio)])
        arr_out_rect.append([eyegaze_x, eyegaze_y, pupilsize, pupilsize])

        #pupilsize

    #print(len(arr_out_rect))
    # step 3.3 write the groundtruth rile.

    with open(out_groundtruth_file, 'w+') as the_file:
        print(len(arr_out_rect))
        for item in arr_out_rect:
            t_str = ','.join(map(str, item))
            the_file.write("%s\n" % t_str)
        #the_file.write("%s\n" % t_str)
    return 0


# step 4: generate video based on image and groundtruth

def GenerateVideo(voutname,w,h,imgfolder,imagecount,out_groundtruth_file):
    if not os.path.exists(imgfolder):
        os.makedirs(imgfolder)
    bar = progressbar.ProgressBar(maxval=imagecount, \
                                  widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    lineList = []
    for line in open(out_groundtruth_file):
        lineList.append(list(map(int, line.rstrip("\n").split(','))))
    #print(len(lineList))
    #out = cv2.VideoWriter(voutname, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10,(w, h))
    out = cv2.VideoWriter(voutname.replace(".avi",".mp4"), cv2.VideoWriter_fourcc('m','p','4','v'), 10, (w, h))
    for i in range (0,len(lineList)):
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

def ReadTrialData(trialfilename,taskindex='A',trialindex='1'):
    #json_arr=[]
    starttime,endtime=0,0
    with open (trialfilename) as fp:
        for line in fp:
            if 'participant' in line:
                line = line.rstrip(",\n").replace("\"\"{","\"").replace("}\"\"","\"")
                t_obj=json.loads(line)
                if t_obj["taskindex"]==taskindex and t_obj["trialindex"]==trialindex:
                    if t_obj["status"]=="START":
                        starttime= t_obj["unixtimestamp"]
                    elif t_obj["status"]=="END":
                        endtime= t_obj["unixtimestamp"]
                #json_arr.append(json.loads(line))
    #print(json_arr)
    return int(starttime),int(endtime) #json_arr

def main():
    folder = "./Data/20191114_02/"
    videoname="Camera3_taskA_trial1_1573754660363.avi"
    trialfilename = "Trials_1573754637958.txt"


    trialinfo_arr=videoname.split('_')
    print(trialinfo_arr)
    taskindex = trialinfo_arr[1].replace("task","") #'A'
    trialindex = trialinfo_arr[2].replace("trial","")#'1'
    videofileindex = trialinfo_arr[3].replace(".avi","") # '1573754660363' #number of the video file

    starttime,endtime=ReadTrialData(folder+trialfilename,taskindex,trialindex)
    print([starttime,endtime])
    #starttime = 1573754660378  # videofileindex+50#1573754660364  #
    #endtime = 1573754766404

    imagesize=1.0
    out_groundtruth_rect = folder+"groundtruth_rect.txt"

    vcount,w,h,w_new,h_new=ImageExtraction(folder+videoname,folder)
    #vcount,w,h,w_new,h_new=2213,1280,720,IMG_WIDTH,IMG_HEIGHT
    t_filter=CheckValidityLines(folder+"Tobii_task"+taskindex+"_trial" + trialindex + "_" + videofileindex + ".txt")
    GroundTruth(t_filter, starttime, endtime, vcount, out_groundtruth_rect,w_new/w, h_new/h)

    GenerateVideo(folder+videoname.replace('.avi', '_out.avi'), w_new, h_new, folder+"img/", vcount, out_groundtruth_rect)
    print([vcount])
if __name__ == '__main__':
    main()

