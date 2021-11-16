import argparse
import os
import shutil
from tqdm import tqdm
import logging
from src.utils.common import read_yaml, create_directories
import random


STAGE = "02" ## <<< change stage name 

logging.basicConfig(
    filename=os.path.join("logs", 'running_logs.log'), 
    level=logging.INFO, 
    format="[%(asctime)s: %(levelname)s: %(module)s]: %(message)s",
    filemode="a"
    )


def main(config_path, params_path):
    ## read config files
    config = read_yaml(config_path)
    params = read_yaml(params_path)
    
    artifacts = config["artifacts"]

    prepared_data_dir = os.path.join(artifacts["ARTIFACTS_DIR"],artifacts["PREPARED_DATA_DIR"])
    train_data_path = os.path.join(prepared_data_dir, artifacts["TRAIN_DATA"])
    test_data_path = os.path.join(prepared_data_dir, artifacts["TEST_DATA"])
    
    featurized_data_dir = os.path.join(artifacts["ARTIFACTS_DIR"],artifacts["FEATURIZED_DATA"])
    create_directories([featurized_data_dir])

    featurized_train_data_path = os.path.join(prepared_data_dir, artifacts["FEATURIZED_OUT_TRAIN"])
    featurized_test_data_path = os.path.join(prepared_data_dir, artifacts["FEATURIZED_OUT_TEST"])

    max_features = params["featurize"]["max_features"]
    ngrams = params["featurize"]["ngrams"]


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("--config", "-c", default="configs/config.yaml")
    args.add_argument("--params", "-p", default="params.yaml")
    parsed_args = args.parse_args()

    try:
        logging.info("\n********************")
        logging.info(f">>>>> stage {STAGE} started <<<<<")
        main(config_path=parsed_args.config, params_path=parsed_args.params)
        logging.info(f">>>>> stage {STAGE} completed!<<<<<\n")
    except Exception as e:
        logging.exception(e)
        raise e