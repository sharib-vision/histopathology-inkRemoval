# @Author: Sharib Ali <shariba>
# @Date:   2018-05-22T13:53:32+01:00
# @Email:  sharib.ali@eng.ox.ac.uk
# @Project: BRC: VideoEndoscopy
# @Filename: deblurAssessment.py
# @Last modified by:   shariba
# @Last modified time: 2018-10-06T08:23:35+01:00
# @Copyright: 2018-2020, sharib ali

import os
import glob
import numpy as np
import re
import sys
import scipy.misc
from scipy.misc import imsave,imread
import cv2
import matplotlib.pyplot as plt
import videoQualityMetrics as QCM
# import metrics as mt
from ssim import SSIM
from PIL import Image
from ssim.utils import get_gaussian_kernel

gaussian_kernel_sigma = 2.5
gaussian_kernel_width = 5
gaussian_kernel_1d = get_gaussian_kernel(gaussian_kernel_width, gaussian_kernel_sigma)

def delimiterFileName (fileName):
    head, tail = os.path.split(fileName)
    return tail

ext = ['*.tif', '*.jpg', '*.png']

BASE_DIR = '/Users/shariba/dataset/histology/Evaluation_ISBI/'
restored='/Users/shariba/dataset/histology/Evaluation_ISBI/restored/'
original='/Users/shariba/dataset/histology/Evaluation_ISBI/original/'
corrupted='/Users/shariba/dataset/histology/Evaluation_ISBI/corrupted/'
undistributedData = 1
textfilename=''
# textfilename = 'Quality_inkRemoval_CycleGAN.txt'

if undistributedData:
    restored='/Users/shariba/dataset/histology/Evaluation_ISBI/restored_UndistributedData/'
    textfilename = 'Quality_inkRemoval_CycleGAN_Undistributed.txt'
else:
    textfilename = 'Quality_inkRemoval_CycleGAN.txt'

psnr = []
reco=[]
vifp=[]
ssim=[]

psnrB = []
recoB=[]
vifpB=[]
ssimB=[]


try:
    os.remove(textfilename)
except OSError:
    pass

useBlur = 0
if useBlur:
    textfilename = 'VQC_blur.txt'

file = BASE_DIR + textfilename
textfile = open(file, 'a')
grayscale=0
usereco=1
for filename in sorted(glob.glob(original + ext[1], recursive = True)):
    #print(filename)
    fileN=delimiterFileName(filename)
    img_clean = cv2.imread(filename)
    image_clean=Image.open(filename)
    img_gray_original = cv2.cvtColor(img_clean, cv2.COLOR_RGB2GRAY)
    if useBlur:
        img_blured = cv2.imread(filename)
        img_gray_blured = cv2.cvtColor(img_blured, cv2.COLOR_RGB2GRAY)
    else:
        print(restored+fileN)
        img_restored = cv2.imread(restored+fileN)
        img_gray_restored = cv2.cvtColor(img_restored, cv2.COLOR_RGB2GRAY)
        image_restored=Image.open(restored+fileN)
    # before
        img_corrupted = cv2.imread(corrupted+fileN)
        image_corrupted =Image.open(corrupted+fileN)
        img_gray_corrupted = cv2.cvtColor(img_corrupted, cv2.COLOR_RGB2GRAY)

    # restored vs original
    if grayscale:
        vifp_value_B = QCM.vifp_mscale(img_gray_original, img_gray_corrupted)
        psnr_value_B = QCM.psnr(img_gray_original, img_gray_corrupted)
        reco_value_B = QCM.reco(img_gray_original, img_gray_corrupted)
        ssim_value_B = SSIM(img_gray_original, gaussian_kernel_1d).ssim_value(img_gray_corrupted)
        # restored vs original
        vifp_value_A = QCM.vifp_mscale(img_gray_original, img_gray_restored)
        psnr_value_A = QCM.psnr(img_gray_original, img_gray_restored)
        reco_value_A = QCM.reco(img_gray_original, img_gray_restored)
        ssim_value_A = SSIM(img_gray_original, gaussian_kernel_1d).ssim_value(img_gray_restored)
    else:
        vifp_value_B = QCM.vifp_mscale(img_clean, img_corrupted)
        psnr_value_B = QCM.psnr(img_clean, img_corrupted)
        # reco_value_B = QCM.reco(img_clean, img_corrupted)
        ssim_value_B = SSIM(image_clean, gaussian_kernel_1d).ssim_value(image_corrupted)
        # restored vs original
        vifp_value_A = QCM.vifp_mscale(img_clean, img_restored)
        psnr_value_A = QCM.psnr(img_clean, img_restored)
        # reco_value_A = QCM.reco(img_clean, img_restored)
        ssim_value_A = SSIM(image_clean, gaussian_kernel_1d).ssim_value(image_restored)

    if usereco:
        reco_value_B = QCM.reco(img_gray_original/255, img_gray_corrupted/255)
        reco_value_A = QCM.reco(img_gray_original/255, img_gray_restored/255)

    textfile.write('\n' ': vifp_value ---> ' + str(vifp_value_B)+ '\t'+ str(vifp_value_A))
    textfile.write('\n' + fileN + ': psnr ---> ' + str(psnr_value_B)+ '\t'+ str(psnr_value_A))
    textfile.write('\n' ': reco_value ---> ' + str(reco_value_B)+ '\t'+ str(reco_value_A))
    textfile.write('\n' ': ssim_value ---> ' + str(ssim_value_B)+ '\t'+ str(ssim_value_A))
    textfile.write('\n')

    psnr.append(psnr_value_A)
    vifp.append(vifp_value_A)
    reco.append(reco_value_A)
    ssim.append(ssim_value_A)

    psnrB.append(psnr_value_B)
    vifpB.append(vifp_value_B)
    recoB.append(reco_value_B)
    ssimB.append(ssim_value_B)


textfile.write('\n'+'mean psnr restoration:' + str(np.mean(psnr))+ '+/-' + str(np.std(psnr)) )
textfile.write('\n'+'mean vifp restoration:' + str(np.mean(vifp))+ '+/-' + str(np.std(vifp)) )
textfile.write('\n'+'mean reco restoration:' + str(np.mean(reco)) + '+/-' + str(np.std(reco)))
textfile.write('\n'+'mean ssim restoration:' + str(np.mean(ssim)) + '+/-' + str(np.std(ssim)))

textfile.write('\n'+'mean psnr original:' + str(np.mean(psnrB))+ '+/-' + str(np.std(psnrB)))
textfile.write('\n'+'mean vifp original:' + str(np.mean(vifpB)) + '+/-' + str(np.std(vifpB)))
textfile.write('\n'+'mean reco original:' + str(np.mean(recoB)) + '+/-' + str(np.std(recoB)))
textfile.write('\n'+'mean ssim original:' + str(np.mean(ssimB)) + '+/-' + str(np.std(ssimB)))


textfile.write('\n')
textfile.close()
print(psnr)
