import os
import argparse
import json

from tqdm import tqdm
from hybrid_transformer.configs.task import TaskConfig
from hybrid_transformer.configs.model import ModelConfig
from hybrid_transformer.configs.trainer import TrainerConfig
from hybrid_transformer.configs.logger import LoggerConfig

from hybrid_transformer.utils.datasets.auto import AutoDataset
from hybrid_transformer.utils.tokenizers.auto import AutoTokenizer
from hybrid_transformer.models.auto import AutoModel
from hybrid_transformer.utils.loggers.wandb import WandbLogger

from hybrid_transformer.trainers.trainer import Trainer

from scripts.joint_learning.train import DEFAULT_CONFIG_FILES

from hybrid_transformer.utils.objectives.guacamol.objective import GUACAMOL_TASKS
from hybrid_transformer.models.prediction import PREDICTION_MODEL_CONFIGS

from guacamol.assess_distribution_learning import assess_distribution_learning

from hybrid_transformer.models.utils import GuacamolModelWrapper


DEFAULT_REFERENCE_FILE = '../data/guacamol/test/smiles.txt'


def evaluate_distribution_learning(tokenizer, model, chembl_file, json_output_file, batch_size, device):
    assess_distribution_learning(
        model=GuacamolModelWrapper(model, tokenizer, batch_size, device),
        chembl_training_file=chembl_file,
        json_output_file=json_output_file,
        benchmark_version='v2')

    return None


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", type=str, required=True)
    parser.add_argument("--data_reference_file", type=str, default=DEFAULT_REFERENCE_FILE)
    parser.add_argument("-trainer", "--path_to_trainer_config", type=str, default=DEFAULT_CONFIG_FILES['trainer'])
    parser.add_argument("-logger", "--path_to_logger_config", type=str, default=DEFAULT_CONFIG_FILES['logger'])
    args = parser.parse_args()
    return args


def main():

    # Args
    args = parse_args()

    # Load configs
    task_config_path = lambda: f'./configs/tasks/guacamol/{guacamol_task}/config.json'

    for guacamol_task in tqdm(GUACAMOL_TASKS):
        task_config = TaskConfig.from_pretrained(task_config_path())
        task_config.augmentation_prob = 0.0 # disable augmentation
        task_config.validate = False  # debug
        dataset = AutoDataset.from_config(task_config, split='test')
        tokenizer = AutoTokenizer.from_config(task_config)

        for model_name, path_to_model_config in tqdm(PREDICTION_MODEL_CONFIGS.items()):

            model_config = ModelConfig.from_pretrained(path_to_model_config)

            trainer_config = TrainerConfig.from_pretrained(args.path_to_trainer_config)
            logger_config = LoggerConfig.from_pretrained(args.path_to_logger_config)

            run_dir = f'{model_name}/{guacamol_task}'
            out_dir = os.path.join(args.out_dir, run_dir)
            trainer_config.out_dir = out_dir

            logger_config.project = 'Table 1 Test'
            logger_config.name = model_name + '_' + guacamol_task

            model = AutoModel.from_config(model_config)
            logger = WandbLogger(logger_config, [task_config, model_config, trainer_config])
            trainer = Trainer(config=trainer_config, model=model, tokenizer=tokenizer, logger=logger)

            print(f"Loading checkpoint from {trainer.out_dir}...")
            trainer.load_checkpoint()
            prediction_results = trainer.test(dataset)

            with open(os.path.join(trainer.out_dir, 'result_prediction.json'), 'w') as fp:
                json.dump(prediction_results, fp)

            trainer.logger.finish()


if __name__ == "__main__":
    main()


# TODO: verify that good checkpoint is loaded
# TODO: verify that wandb is working
# TODO: test prediction
# TODO: test generation
# TODO: (optional) load json file and write log to wandb
