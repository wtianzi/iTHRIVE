# iTHRIVE
Eye tracking visualization demo code for the virtual coach of laparoscopic surgery

## Environment: 
1) download and install 64bit python 3.7+ : https://www.python.org/downloads/
2) install python package:

pip install opencv-python

pip install numpy

pip install progressbar

## Rewrite the script:
1) Put the video file, eye tracking txt file in the folder "data/testing/".


2) Rewrite the file index and task index in the iTHRIVE_Imageextract.py file

    folder = "./Data/testing/"
    
    videoname = "Camera3_taskA_trial1_1573754660363.avi"
    
    trialfilename = "Trials_1573754637958.txt"

## Run the script:
Use command line or other IDEs installed.

If use command line: 
1) navigate to the iTHRIVE folder
2) type and run(enter) 'python iTHRIVE_Imageextract.py'
