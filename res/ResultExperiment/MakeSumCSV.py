import pandas as pd
from matplotlib import gridspec
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from res.SSEnum import OperationEnum


OPERATION_NAMES = OperationEnum.OperationName_LIST.value
hfont = {'fontname': 'Times New Roman'}
def transformData(data, label):
    data.loc[(data[label + "_manipulation"] == 0) & (data[label + "_direction"] == 0), label] = OperationEnum.Ir.value
    data.loc[(data[label + "_manipulation"] == 0) & (data[label + "_direction"] == 1), label] = OperationEnum.Id.value
    data.loc[(data[label + "_manipulation"] == 1) & (data[label + "_direction"] == 0), label] = OperationEnum.Dl.value
    data.loc[(data[label + "_manipulation"] == 1) & (data[label + "_direction"] == 1), label] = OperationEnum.Du.value
    data.loc[(data[label + "_manipulation"] == 2) & (data[label + "_direction"] == 4), label] = OperationEnum.Copy.value
    data.loc[(data[label + "_manipulation"] == 3) & (data[label + "_direction"] == 4), label] = OperationEnum.Cut.value
    data.loc[(data[label + "_manipulation"] == 4) & (data[label + "_direction"] == 4), label] = OperationEnum.Paste.value
    data.loc[(data[label + "_manipulation"] == 5) & (data[label + "_direction"] == 2), label] = OperationEnum.Sa.value
    data.loc[(data[label + "_manipulation"] == 5) & (data[label + "_direction"] == 3), label] = OperationEnum.Sd.value
    return data

# 操作ごとのlabelカラムの合計値DataFrameを返す

def main():
    pd.set_option('display.max_columns', 15)
    shortcutRateDf = pd.DataFrame()
    gestureRateDf = pd.DataFrame()
    all_data = pd.DataFrame()
    for i in range(15):
        data = pd.read_csv('./result_p{}.csv'.format(i + 1), header=0, index_col=None)

        # データ整形
        data['true'] = 0
        data['select'] = 0
        data = transformData(data, 'true')
        data = transformData(data, 'select')
        all_data = pd.concat([all_data, data])

        # split data gesture and shortcut
        gesture_df = data[data['mode'] == 0]
        shortcut_df = data[data['mode'] == 1]

    gesture_df = all_data[all_data['mode'] == 0]
    gesture_df.reset_index()
    print(gesture_df.loc[:, ['participant', 'true', 'select', 'time']])
    gesture_df.loc[:, ['participant', 'true', 'select', 'time']].to_csv("./summary.csv")


if __name__ == "__main__":
    main()
