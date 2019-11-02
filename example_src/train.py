# A sample training component that trains a simple scikit-learn decision tree model.
# This implementation works in File mode and makes no assumptions about the input file names.
# Input is specified as CSV with a data point in each row and the labels in the first column.

from __future__ import print_function

import os
import json
import pickle
import sys
import traceback

import numpy as np
import pandas as pd
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import KFold

# These are the paths to where SageMaker mounts interesting things in your container.

prefix = ''

input_path = prefix + 'data'
output_path = os.path.join(prefix, 'output')
model_path = os.path.join(prefix, 'model')

# This algorithm has a single channel of input data called 'training'. Since we run in
# File mode, the input files are copied to the directory specified here.
channel_name='training'
training_path = os.path.join(input_path, channel_name)

# The function to execute the training.
def train():
    print('Starting the training.')
    try:

        # Take the set of files and read them all into a single pandas dataframe
        input_files = [ os.path.join(training_path, file) for file in os.listdir(training_path) ]
        if len(input_files) == 0:
            raise ValueError(('There are no files in {}.\n' +
                              'This usually indicates that the channel ({}) was incorrectly specified,\n' +
                              'the data specification in S3 was incorrectly specified or the role specified\n' +
                              'does not have permission to access the data.').format(training_path, channel_name))
        raw_data = [ pd.read_csv(file, header=None) for file in input_files ]
        train_data = pd.concat(raw_data)

        # labels are in the first column
        train_y = train_data.iloc[:,0]
        train_X = train_data.iloc[:,1:]

        clf = RandomForestClassifier(random_state=42)

        grid_params = [{
            "max_features" : ["auto","log2",0.20, 0.30],
            "n_estimators" : [10,50,100],
            "min_samples_leaf" : [25, 50, 100]
        }]

        scoring = {
            'acc':'accuracy',
            'precision':'precision',
            'recall':'recall',
            'auc':'roc_auc',
            'mse':'neg_mean_squared_error',
            'r2':'r2'
        }

        grid_clf = GridSearchCV(
            estimator = clf, 
            param_grid=grid_params, 
            cv=5, 
#             scoring=scoring,
            refit='auc',
            n_jobs=-1,verbose=1,return_train_score=False)

        grid_clf.fit(train_X, train_y)

        # save the model
        with open(os.path.join(model_path, 'iris-randomforest.pkl'), 'wb') as out:
            pickle.dump(grid_clf, out, protocol=0)
        print('Training complete.')

    except Exception as e:
        # Write out an error file. This will be returned as the failureReason in the
        # DescribeTrainingJob result.
        trc = traceback.format_exc()
        with open(os.path.join(output_path, 'failure'), 'w') as s:
            s.write('Exception during training: ' + str(e) + '\n' + trc)
        # Printing this causes the exception to be in the training job logs, as well.
        print('Exception during training: ' + str(e) + '\n' + trc, file=sys.stderr)
        # A non-zero exit code causes the training job to be marked as Failed.
        sys.exit(255)

if __name__ == '__main__':
    train()

    # A zero exit code causes the job to be marked a Succeeded.
    sys.exit(0)
