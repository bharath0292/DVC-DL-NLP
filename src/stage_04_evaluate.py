import argparse
import os
import logging
from src.utils.common import read_yaml, save_json
import joblib
import numpy as np
import sklearn.metrics as metrics
import json
import math

STAGE = "04" ## <<< change stage name 

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

    featurized_data_dir = os.path.join(artifacts["ARTIFACTS_DIR"],artifacts["FEATURIZED_DATA"])
    featurized_test_data_path = os.path.join(featurized_data_dir, artifacts["FEATURIZED_OUT_TEST"])

    model_dir_path = os.path.join(artifacts["ARTIFACTS_DIR"],artifacts["MODEL_DIR"])
    model_path = os.path.join(model_dir_path, artifacts["MODEL_NAME"])

    model = joblib.load(model_path)

    matrix = joblib.load(featurized_test_data_path)
    labels = np.squeeze(matrix[:,1].toarray())
    X = matrix[:, 2:]

    predictions_by_class = model.predict_proba(X)
    predictions = predictions_by_class[:, 1]

    PRC_json_path = config["plots"]["PRC"]
    ROC_json_path = config["plots"]["ROC"]
    scores_json_path = config["metrics"]["SCORES"]

    avg_precision = metrics.average_precision_score(labels, predictions)
    roc_auc = metrics.roc_auc_score(labels, predictions)

    scores = {
        "avg_precision": avg_precision,
        "roc_auc": roc_auc
    }
    save_json(path=scores_json_path, data=scores)

    precision, recall, prc_threshold = metrics.precision_recall_curve(labels, predictions)
    
    #take only limited data
    nth_point = math.ceil(len(prc_threshold)/1000)
    prc_points = list(zip(precision, recall, prc_threshold))[::nth_point] 
    prc_data = {
        "prc": [
            {"precision": p, "recall": r, "threshold": t}
            for p,r,t in prc_points 
        ]
    }

    save_json(PRC_json_path, prc_data)


    fpr, tpr, roc_threshold = metrics.roc_curve(labels, predictions)


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