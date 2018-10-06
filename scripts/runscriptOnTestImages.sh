
#!\bin\bash

source activate $ENVIRONMENT

BASEDIR=HISTOPATHOLOGY-PIPELINE-CHECKPOINTS
RESULTDIR=$BASEDIR/results

`mkdir -p $RESUTLDIR`

python test_cycleGAN.py --dataroot ./$BASEDIR/test_ISBI/ \
--model test --loadSize 512 --fineSize 512  --how_many 3 \
--results_dir $RESULTDIR \
--checkpoints_dir .$BASEDIR/checkpoint_SPARSE/


