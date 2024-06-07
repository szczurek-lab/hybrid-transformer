#!/bin/bash

python experiments/joint_training/train.py \
    --out_dir /home/adam/ml_results/jointformer \
    --path_to_task_config configs/tasks/guacamol/debug \
    --path_to_model_config configs/models/jointformer_debug \
    --path_to_trainer_config configs/trainers/joint \
    #    --path_to_logger_config configs/loggers/wandb \
    #    --logger_display_name jointformer \