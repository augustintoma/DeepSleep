#!/usr/bin/env python3
"""
Created on Fri Mar 30 22:03:29 2018

@author: mohammad
"""
import sys
import os
import glob
import numpy as np
import pandas as pd
import scipy.io
from sklearn.externals import joblib
import physionetchallenge2018_lib as phyc

def classify_record(record_name):
    header_file = record_name + '.hea'
    signal_file = record_name + '.mat'

    # Read model files from the 'models' subdirectory, which are
    # generated by 'train_classifier.py'
    model_list = []
    for f in glob.glob('models/*_model.pkl'):
        model_list.append(f)

    # Use the average predictions from the models generated on the
    # training set
    predictions_mean = 0.
    for j in range(0, len(model_list)):
        this_model = model_list[j]
        predictions = run_classifier(header_file, signal_file, this_model)
        predictions_mean += predictions

    predictions_mean /= len(model_list)

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Return a vector of per-sample predictions, as per challenge requirements
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    return predictions_mean

# This function generates the predictions from a single model
def run_classifier(header_file, signal_file, classifier_pickle):

    signal_names, Fs, n_samples = phyc.import_signal_names(header_file)

    # Get this subject's data as a dataframe
    this_data = phyc.get_subject_data_test(signal_file, signal_names)

    SaO2 = this_data.get(['SaO2']).values
    step        = Fs * 60
    window_size = Fs * 60

    # Initialize the X_subj and Y_subj matricies
    X_subj = np.zeros([((n_samples) // step), 1])

    for idx, k in enumerate(range(0, (n_samples-step+1), step)):
        X_subj[idx, :] = np.var(np.transpose(SaO2[k:k+window_size]), axis=1)

    # Load the classifier
    my_classifier = joblib.load(classifier_pickle)

    # Generate the prediction for the subjects.
    predictions = my_classifier.predict_proba(X_subj)
    predictions = predictions[:, 1]
    predictions = [x * np.ones([window_size]) for x in predictions]
    predictions = np.concatenate(predictions)
    predictions = np.append(predictions, np.zeros(np.size(this_data, 0)
                                                  - np.size(predictions, 0)))
    return predictions

if __name__ == '__main__':
    for record in sys.argv[1:]:
        output_file = os.path.basename(record) + '.vec'
        results = classify_record(record)
        np.savetxt('vec/' + output_file, results, fmt='%.3f')
