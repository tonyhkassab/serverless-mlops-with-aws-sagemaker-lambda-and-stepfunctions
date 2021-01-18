import os
import argparse
import warnings
import numpy as np
import pandas as pd
from time import gmtime, strftime
from sklearn.exceptions import DataConversionWarning
warnings.filterwarnings(action='ignore', category=DataConversionWarning)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--train-test-split-ratio', type=float, default=0.3)
    parser.add_argument('--local_path', type=str, default="/opt/ml/processing")
    
    args, _ = parser.parse_known_args()
    split_ratio = args.train_test_split_ratio
    local_path = args.local_path

    input_data_path = os.path.join(local_path, 'input/boston.csv')
    print('Reading input data from {}'.format(input_data_path))
    df = pd.read_csv(input_data_path)
    print(df.shape)
    
    test_index = np.random.rand(len(df)) < 0.2
    test_df = df[test_index].reset_index(drop=True)
    df = df[~test_index].reset_index(drop=True)
    valid_index = np.random.rand(len(df)) < 0.2
    valid_df = df[valid_index].reset_index(drop=True)
    train_df = df[~valid_index].reset_index(drop=True)

    # Write train/valid/test seta to disk (sagemaker will automatically copy them to S3)
    train_df.to_csv(os.path.join(local_path, "train/train.csv"), index = False)
    valid_df.to_csv(os.path.join(local_path, "validation/validation.csv"), index = False)
    test_df.to_csv(os.path.join(local_path, "test/test.csv"), index = False)
    
    print(train_df.shape)
    print(valid_df.shape)
    print(test_df.shape)