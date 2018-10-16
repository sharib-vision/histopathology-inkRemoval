#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 19:22:01 2018

@author: sharib 
"""
def read_rgb(f):

    import cv2

    im = cv2.imread(f)
    [b,g,r] = cv2.split(im)

    return cv2.merge([r,g,b])

def detect_imgs(infolder, ext='.tif'):

    import os

    items = os.listdir(infolder)

    flist = []
    for names in items:
        if names.endswith(ext) or names.endswith(ext.upper()):
            flist.append(os.path.join(infolder, names))

    return np.sort(flist)


def classify_information(img, model, shape=(64,64)):

    from skimage.transform import resize

    im = resize(img, shape)

    info = model.predict(im[None,:])

    return info


if __name__=="__main__":

import numpy as np
    import cv2
    import os
    import time
    import argparse
    from shutil import copyfile, move

    # parse the
    parser = argparse.ArgumentParser()
    parser.add_argument('-input_dir', action='store', type=str, help='full path for your input image directory')
    parser.add_argument('-result_dir', action='store', type=str, help='full path for the results to be saved')
    parser.add_argument('-checkpoint', action='store', type=str, help='full path of binaryclassifier checkpoint')
    parser.add_argument('-moveImages', action='store', type=int, help='move files option')
    parser.add_argument('-fileListName', action='store', type=str, help='filename for list to be saved')
    arg_input = parser.parse_args()

    os.environ["CUDA_VISIBLE_DEVICES"]=str(0)
    from keras.models import load_model

    BASE_DIR= '/well/rittscher/projects/dataset-NS/annotationStudy/'
   #  #BASE_DIR= '/well/rittscher/projects/dataset-NS/originalFiles/'
   #
   # # DATA_DIR = '/well/rittscher/projects/dataset-NS/annotationStudy/29813_14_600950_RP_6O/'
   # # 33299_14_600957_RP_2I
   # # FOLDER_LIST=['','29813_14_600950_RP_6O','31304_14_600939_RP_5N','33299_14_600957_RP_2I','33299_14_600957_RP_2J','33299_14_600957_RP_2L', '45374_16_601166_RP_4O','48434_14_600983_RP_1J', '7539_14_600865_RP_1L']
   # #FOLDER_LIST=['','47502_16_601169_RP_6N']
   #  FOLDER_LIST=['','48434_14_600983_RP_1J']
   #  print(len(FOLDER_LIST))

    # load your model here
    FOLDER_LIST= arg_input.input_dir
    RESULTS_DIR= arg_input.result_dir
    
    print(FOLDER_LIST)
    print(RESULTS_DIR)

    imgfolder = FOLDER_LIST
    imgfiles = detect_imgs(imgfolder, ext='.jpg')

    CNN_classify_model = load_model(arg_input.checkpoint)
    infoness = ['ink', 'noInk']
    textfilename = ''
    if arg_input.fileListName == '':
        textfilename = 'ISBI2019_bckGrnd.txt'
    else:
        textfilename = arg_input.fileListName
    
    print(textfilename)
    file = RESULTS_DIR + textfilename
    textfile = open(file, 'a')

    tiles_score = []
    tiles_name = []

    for imagePath in imgfiles[:]:
        #image = io.imread(imagePath)
        print(imagePath)
        batch_size=1
        # img1 = cv2.imread(imagePath, 1)
        img1 = read_rgb(imagePath)
        print('Loading model :')
        t0 = time.time()
        informativeness = classify_information(img1, CNN_classify_model, shape=(128,128))
        t1 = time.time()
        print('Model loaded in: ', t1-t0)
        info_index = np.argmax(informativeness.ravel())
        # >0.51
        tiles_score.append(info_index)

        if info_index==1:
            resultFileName=imagePath.split('/')[-1]
            textfile.write('\n'+ resultFileName)
            tiles_name.append(RESULTS_DIR+resultFileName)
            if arg_input.moveImages:
                move(imgfolder+resultFileName, RESULTS_DIR+resultFileName)
            else:
                copyfile(imgfolder+resultFileName, RESULTS_DIR+resultFileName)

    textfile.write('\n')
    textfile.write('\n Total: '+ str(len(tiles_name)))
    textfile.close()
