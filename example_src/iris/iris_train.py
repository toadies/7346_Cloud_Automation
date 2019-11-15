# A sample training component that trains a simple scikit-learn decision tree model.
# This implementation works in File mode and makes no assumptions about the input file names.
# Input is specified as CSV with a data point in each row and the labels in the first column.

from __future__ import print_function

import os
import argparse
import json
import joblib
import sys
import traceback

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import KFold
from sklearn import preprocessing

# These are the paths to where SageMaker mounts interesting things in your container.
if __name__ == '__main__':
    print("load data")
    parser = argparse.ArgumentParser()

    # Sagemaker specific arguments. Defaults are set in the environment variables.

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

    args = parser.parse_args()

    iris = pd.read_csv(os.path.join(args.train,"iris.csv"))

    # labels are in the first column
    train_X = iris.iloc[:,1:].values

    le = preprocessing.LabelEncoder()
    train_y = le.fit_transform(iris.iloc[:,0])

    print("trian model")
    clf = RandomForestClassifier(
        max_features="auto",
        n_estimators=10,
        min_samples_leaf=25,
        random_state=42)

    clf.fit(train_X, train_y)

    print("save model")
    # Print the coefficients of the trained classifier, and save the coefficients
    joblib.dump(clf, os.path.join(args.model_dir, "iris-rf.pkl"))
    joblib.dump(le, os.path.join(args.model_dir, "iris-labels.pkl"))


def model_fn(model_dir):
    """Deserialized and return fitted model

    Note that this should have the same name as the serialized model in the main method
    """
    clf = joblib.load(os.path.join(model_dir, "iris-rf.pkl"))
    return clfs

