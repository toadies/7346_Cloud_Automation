from __future__ import print_function

import os
import argparse
import json
import joblib

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn import preprocessing



if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    try:
        sm_output = os.environ['SM_OUTPUT_DATA_DIR']
        sm_model = os.environ['SM_MODEL_DIR']
        sm_train = os.environ['SM_CHANNEL_TRAIN']
    except:
        sm_output = "output/"
        sm_model = "model/"
        sm_train = "data/"

    parser.add_argument('--output-data-dir', type=str, default=sm_output)
    parser.add_argument('--model-dir', type=str, default=sm_model)
    parser.add_argument('--train', type=str, default=sm_train)
    parser.add_argument('--X', 
        type=str, 
        default='{"sepal_length":5,"sepal_width":3,"petal_length":1.2,"petal_width":0.4}')

    args = parser.parse_args()

    X_json = json.loads(args.X)
    X = pd.DataFrame([X_json]).values

    clf = joblib.load(os.path.join(args.model_dir, "iris-rf.pkl"))
    le = joblib.load(os.path.join(args.model_dir, "iris-labels.pkl"))

    pred = clf.predict(X)

    print( le.inverse_transform(pred) )

