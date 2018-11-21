#!/bin/bash

BASE_FOLDER=/Users/shariba/development/deepLearning/histology/histopathology-inkRemoval
ORIGINAL_FILES=$BASE_FOLDER/histo_ink_removal
ext='.jpg'
j=0
for i in `ls ${ORIGINAL_FILES} | grep $ext`; do

    echo ${ORIGINAL_FILES}/$i >> histotest_ISBI.txt
    j=$((j+1))
#    #echo $i
#    if (( $j % 10 == 0 ))
#    then
#        echo ${ORIGINAL_FILES}/$i >> histotest_ISBI_2class.txt
#        j=$((j+1))
#
#    else
#
#        echo ${ORIGINAL_FILES}/$i >> histotrain_ISBI_2class.txt
#        j=$((j+1))
#    fi
#

done
