import math

import pandas as pd
from matplotlib import gridspec, rcParams
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from res.SSEnum import OperationEnum

# -----JP------
rcParams['font.family'] = 'Hiragino Maru Gothic Pro'
rcParams['pdf.fonttype'] = 42
OPERATION_NAMES = OperationEnum.OperationName_LIST_JP.value
# -------------
# # En
# OPERATION_NAMES = OperationEnum.OperationName_LIST.value

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
def calcDfAvarage(data, p, column):
    df = pd.DataFrame(index=["{}".format(p)], columns=OPERATION_NAMES)
    for i in range(len(OPERATION_NAMES)):
        d = data.loc[(data["true"] == i), column]
        df[OPERATION_NAMES[i]] = d.sum() / len(d)
    return df

def calcDfStd(data, p, column):
    df = pd.DataFrame(index=["{}".format(p)], columns=OPERATION_NAMES)
    for i in range(len(OPERATION_NAMES)):
        d = data.loc[(data["true"] == i), column]
        df[OPERATION_NAMES[i]] = d.std()
    return df

def calcDfSe(data, p, column):
    df = pd.DataFrame(index=["{}".format(p)], columns=OPERATION_NAMES)
    for i in range(len(OPERATION_NAMES)):
        d = data.loc[(data["true"] == i), column]
        df[OPERATION_NAMES[i]] = d.std() / math.sqrt(len(d))
    return df


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
        gestureRateDf = pd.concat([gestureRateDf, calcDfAvarage(gesture_df, i + 1, "error")])
        shortcutRateDf = pd.concat([shortcutRateDf, calcDfAvarage(shortcut_df, i + 1, "error")])


    # print(((1-gestureRateDf).sum()/len(gestureRateDf)).std())
    # print(shortcutRateDf)
    # print(calcDfAvarage(all_data[all_data['mode'] == 0], "gesture", 'error'))
    # print(calcDfAvarage(all_data[all_data['mode'] == 1], "shortcut", 'error'))
    print("gesture recognition: {0:2f} %\nshortcut recognition: {1:2f} %".format(((1-gestureRateDf).sum()/len(gestureRateDf)).sum()/len(OPERATION_NAMES) * 100, ((1-shortcutRateDf).sum()/len(shortcutRateDf)).sum()/len(OPERATION_NAMES) * 100))
    print("gesture std: {0:2f}\nshortcut std: {1:2f}\n".format(((1-gestureRateDf).sum()/len(gestureRateDf)).std(), ((1-shortcutRateDf).sum()/len(shortcutRateDf)).std()))

    show_CM(all_data)
    # show_Bar(all_data, "time")

def show_Bar(data, column):
    all_gestures = data[data['mode'] == 0]
    all_shortcuts = data[data['mode'] == 1]
    aveDf = calcDfAvarage(all_gestures, "gesture", column)
    aveDf = pd.concat([aveDf, calcDfAvarage(all_shortcuts, "shortcut", column)])
    stdDf = calcDfStd(all_gestures, "gesture", column)
    stdDf = pd.concat([stdDf, calcDfStd(all_shortcuts, "shortcut", column)])
    print("gesture time std: {0:2f}\nshortcut time std: {1:2f}".format(all_gestures[column].std(), all_shortcuts[column].std()))
    print("gesture time ave: {0:2f}\nshortcut time ave: {1:2f}".format(all_gestures[column].sum()/len(all_gestures), all_shortcuts[column].sum()/len(all_gestures)))

    fig, ax1 = plt.subplots(figsize=(7, 3))
    x = np.arange(1, 10)
    x1 = np.linspace(0.85, 8.85, 9)
    x2 = np.linspace(1.15, 9.15, 9)

    ax1.bar(x1, aveDf.loc["gesture"].values, color='indianred', width=0.3, align="center", label="Gesture")
    ax1.bar(x2, aveDf.loc["shortcut"].values, color='cadetblue', width=0.3, align="center", label="Shortcut key")
    ax1.errorbar(x1, aveDf.loc["gesture"].values, yerr=stdDf.loc["gesture"].values, ecolor='black', markeredgecolor="black", fmt='None', capsize=3, alpha=0.5)
    ax1.errorbar(x2, aveDf.loc["shortcut"].values, yerr=stdDf.loc["shortcut"].values, ecolor='black', markeredgecolor="black", fmt='None', capsize=3, alpha=0.5)
    ax1.set_xticks(x)
    ax1.set_ylim(0, 25)
    ax1.set_xticklabels(OPERATION_NAMES, fontsize=13)  # X軸のラベル
    ax1.set_yticks(np.linspace(0, 25, 6))

    ax1.tick_params(bottom=False, labelsize=13)
    ax1.set_ylabel('{0} ({1})'.format(column.capitalize(), "s"), fontsize=15)

    ax1.legend(bbox_to_anchor=(1, 1), loc='upper right', borderaxespad=0.5, fontsize=8)

    plt.show()
    fig.savefig("./figure/{}.pdf".format(column))


def show_CM(data):
    all_gestures = data[data['mode'] == 0]
    cm_gesture = confusion_matrix(all_gestures['true'].values, all_gestures['select'].values)
    cm_g = pd.DataFrame(cm_gesture, columns=OPERATION_NAMES, index=OPERATION_NAMES)

    # print("gesture recognition: {0:2f} %\nshortcut recognition: {1:2f} %".format((1 - g_error.sum() / len(g_error)) * 100, (1 - s_error.sum() / len(s_error)) * 100))
    # print("gesture std: {0:2f}\nshortcut std: {1:2f}".format(g_error.std(), s_error.std()))

    fig, ax1 = plt.subplots(figsize=(8, 7))
    labelNum = int(len(all_gestures) / len(OPERATION_NAMES))  # 各ラベルの数
    # ax1.set_title("Gesture", fontsize=30)

    ax1.set_xticklabels(OPERATION_NAMES, fontsize=12)
    ax1.set_yticklabels(OPERATION_NAMES, fontsize=12)

    sns.set(font_scale=2)
    sns.heatmap(cm_g / labelNum, annot=True, cmap="Blues", fmt='.2f', ax=ax1, annot_kws={"size": 12}, vmin=0, vmax=1)  # 正規化したものを表示
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    fig.subplots_adjust(wspace=10)
    plt.show()

    fig.savefig("./figure/resultCM.pdf")


if __name__ == "__main__":
    main()
