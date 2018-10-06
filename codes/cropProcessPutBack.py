# @Author: Sharib Ali <shariba>
# @Date:   2018-10-02T17:08:21+01:00
# @Email:  sharib.ali@eng.ox.ac.uk
# @Project: BRC: VideoEndoscopy
# @Filename: cropProcessPutBack.py
# @Last modified by:   shariba
# @Last modified time: 2018-10-03T10:27:17+01:00
# @Copyright: 2018-2020, sharib ali


from PIL import Image
import numpy as np
import argparse
from shutil import copyfile, move
import os
import errno
import glob


def group(seq, sep):
    g = []
    for el in seq:
        if el == sep:
            yield g
            g = []
        g.append(el)
    yield g


parser = argparse.ArgumentParser(description='ink removal test arguments')

parser.add_argument('--datalist', type=str, default='./tilesWithInk.txt', help='enter datalist')
parser.add_argument('--result_dir', type=str, default='./tilesWithInk.txt', help='enter result_dir')

args = parser.parse_args()
print(args.datalist)
dataList = open(args.datalist, 'rt').read().split('\n')
RESULTS_DIR=args.result_dir
print(len(dataList))

ex = ['Enter', ':', 'Ink:' ]
result = list(group(dataList, 'Enter'))
result = list(group(result, ':'))
print(len(result))
fileNamesList = []
bbox=[]
classifiedRowsPerImage=0
NClassPerImage=[]
# len(dataList)
for i in range (400, len(dataList)):
    readLines = dataList[i]
    # print('reading', readLines)
    findImage = readLines.split(':')
   
    # findImage= list(group(readLines, ':'))
    if findImage !=[]:
        bbox_1=[]
        # fileNamesList
#        print(findImage[0])
        if findImage[0] == 'Enter Image Path':
            fileNamesList.append(findImage[1])
            NClassPerImage.append(classifiedRowsPerImage)
            classifiedRowsPerImage = 0
#            print(fileNamesList)

        if findImage[0] == 'Ink':
            classifiedRowsPerImage=classifiedRowsPerImage+1
#            print(findImage)
            left_x = findImage[2].split('t')
            # print(left_x[0])
            bbox_1.append(left_x[0])
            left_x = findImage[3].split('w')
            # print(left_x[0])
            bbox_1.append(left_x[0])
            left_x = findImage[4].split('h')
            # print(left_x[0])
            bbox_1.append(left_x[0])
            left_x = findImage[5].split(')')
            # print(left_x[0])
            # x, y,
            bbox_1.append(left_x[0])
            bbox.append(bbox_1)


print('Number of ink per image:', NClassPerImage)
print('fileLists',fileNamesList)
print('bbox:', bbox)
print(len(NClassPerImage))
# Processing here
# if list number of ink per image == 0 then copy file to the restored foler (no restoration needed)
# RESULTS_DIR=
moveFiles = 1
if moveFiles:
    for i in range (1, len(NClassPerImage)):
        if NClassPerImage[i] == 0:
            print(fileNamesList[i])
            resultFileName=fileNamesList[i].split('/')[-1]
            print('copying/moving file ...', resultFileName)
            move(fileNamesList[i].strip(), RESULTS_DIR+resultFileName)

# imageList= dataList.split('\n')
# print(imageList)
useCropping = 0
if useCropping:

    EXP1 = 0
    EXP2 = 0
    EXP3 = 1
    if EXP1:
        # TODO to retreive from the txt files
        minX=1133
        minY=902
        width=389
        height=647
        #  read original image
        # Ink: 7%	(left_x: 1133   top_y:  902   width:  389   height:  647)
        largeImage='/Users/shariba/dataset/histology/testsCopyOnly/Tile002770.jpg'
        im = Image.open(largeImage)
        w, h = im.size

    if EXP2:
        # TODO to retreive from the txt files
        minX=125
        minY=160
        width=1407
        height=1316
        #  read original image
         # Ink: 51%	(left_x:  125   top_y:  160   width: 1407   height: 1316)
        # Ink: 7%	(left_x: 1133   top_y:  902   width:  389   height:  647)
        largeImage='/Users/shariba/dataset/histology/testsCopyOnly/ISBI2019_48434_1J_GB/Tile003993.jpg'
        im = Image.open(largeImage)
        w, h = im.size

    if EXP3:
        # TODO to retreive from the txt files
        minX=-5
        minY=58
        width=704
        height=1389
        #  read original image
    # (left_x:   -5   top_y:   58   width:  704   height: 1389)
        largeImage='/Users/shariba/dataset/histology/testsCopyOnly/ISBI2019_48434_1J_GB/Tile004500.jpg'
        # load processed image here
        largeImage='/Users/shariba/dataset/histology/restoredImages/Tile004500.jpg'
        im = Image.open(largeImage)
        w, h = im.size

    # module load cuda/9.0
    # .  ~/pytorch-v0.4.0-cuda8.0-py3.5-venv/bin/activate
    # python test.py --dataroot /well/rittscher/projects/detection_histology/testCropped/ --model test  --loadSize 1578 --fineSize 1578
    # --results_dir /well/rittscher/projects/detection_histology/result/
    # --checkpoints_dir checkpoint_ISBI19/
    # TODO multiple locations detected (compute min --> minX and minY and max --> w and h)



    # locate minimum
    tmpMinX = minX
    tmpMinY = minY
    if minX < w/8:
        minX = 0
    if minY < h/8:
        minY = 0

    if width > int(w/1.5):
        width = w
        tmpMinX=0

    if height > int(h/1.5):
        height = h
        tmpMinY=0

    # locate maximum depending upon the localized area
    if minX > w/2:
        width = w
    if minY > h/2:
        height = h

    if minX > w/2 or  minY > h/2:
        area = (minX, minY, width, height)
    else:
        area = (minX, minY, width+tmpMinX, height+tmpMinY)


    cropped_img = im.crop(area)
    cropped_img.save("/Users/shariba/dataset/histology/testsCopyOnly/Tile002770_small.jpg")
    #

    smallImage='/Users/shariba/dataset/histology/testsCopyOnly/Tile002770_small.jpg'
    im2 = Image.open(smallImage)

    # copy on original Image
    # load original image
    largeImage='/Users/shariba/dataset/histology/testsCopyOnly/ISBI2019_48434_1J_GB/Tile004500.jpg'
    im_orig = Image.open(largeImage)
    im_orig.paste(im2, (minX,minY))
    im_orig.save("/Users/shariba/dataset/histology/testsCopyOnly/test.png")
