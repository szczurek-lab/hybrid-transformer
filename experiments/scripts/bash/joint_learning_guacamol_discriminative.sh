#!/bin/bash

#python ./scripts/joint_learning/train_old.py \
#    --out_dir /raid/aizd/jointformer/results_v4/joint_learning/guacamol \
#    --benchmark guacamol \
#    --model GPTForPrediction

python ./scripts/joint_learning/eval.py \
    --out_dir /raid/aizd/hybrid_transformer/results_v4/joint_learning/guacamol \
    --benchmark guacamol \
    --model GPTForPrediction
