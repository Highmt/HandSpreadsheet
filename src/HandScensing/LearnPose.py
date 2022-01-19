import csv
import datetime
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import gridspec
from sklearn import metrics, svm
from sklearn.metrics import classification_report, confusion_matrix

from sklearn.model_selection import train_test_split, GridSearchCV

import os
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier

from res import SSEnum
from res.SSEnum import FeatureEnum
from src.HandScensing.HandListener import HandData
from src.HandScensing.Predictor import convertLearningPS

np.random.seed(1671)  # for reproducibility
ver = "p0"
# network and training
DROPOUT = 0.2
data_pass = '../../res/data/train/saved/{}'.format(ver)
lr_label = ['left', 'right']
model_label = ['KNN', 'SVC', 'NN']
model_name = ['KNeighborsClassifier', 'SVC', 'MLPClassifier']


# ディレクトリが存在しない場合作成
model_pass = '../../res/learningModel/{}'.format(ver)
dir = Path(model_pass)
dir.mkdir(parents=True, exist_ok=True)

result_pass = '../../res/learningResult/create/{}'.format(ver)
dir = Path(result_pass)
dir.mkdir(parents=True, exist_ok=True)

def convertLearningDF(data: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame(columns=FeatureEnum.FEATURE_LIST.value)
    hand = HandData()
    for i, ps in data.iterrows():
        hand.loadPS(ps)
        d = convertLearningPS(hand)
        df = df.append(d, ignore_index=True)
    return df


for i in range(2):
    print("------------- {} start -------------".format(lr_label[i]))
    read_data = pd.read_csv(data_pass + '/' + lr_label[i] + 'Data.csv', sep=',', index_col=0)

    # read_data = pd.read_csv('../../res/data/train/saved/p0/{}Data.csv'.format(lr_label[i]), index_col=0)
    # for j in range(1, 3):
    #     read_data = read_data.append(pd.read_csv('../../res/data/train/saved/p{}/{}Data.csv'.format(j, lr_label[i]), index_col=0))
    data = convertLearningDF(read_data).drop("Label", axis=1).values
    label = read_data["Label"].values
    train_data, test_data, train_label, test_label = train_test_split(data, label, test_size=0.2, stratify=label)

    # normalize
    print(train_data.shape[0], 'train samples')
    print(test_data.shape[0], 'test samples')

    print("train start")
    print("# Tuning hyper-parameters for accuracy")
    fig = plt.figure(figsize=(15, 7))
    plt.suptitle('confusion matrix of Cross-validation for {} hand '.format(lr_label[i]))

    spec = gridspec.GridSpec(ncols=3, nrows=1, width_ratios=[1, 1, 1.3])
    # 操作の数だけグラフを作成
    ax = [fig.add_subplot(spec[i]) for i in range(len(model_label))]


    for model_id in range(3):
        print("------------- {} start ------------\n".format(model_label[model_id]))

        #  KNN------------------------------------------------
        if model_id == 0:
            knn_parameters = {'n_neighbors': [7, 11, 19],
                              'weights': ['uniform', 'distance'],
                              'metric': ['euclidean', 'manhattan']
                              }
            scores = ['precision', 'recall', 'f1']

            clf = GridSearchCV(KNeighborsClassifier(), knn_parameters, cv=5,
                               scoring='accuracy', n_jobs=-1, verbose=10)
            clf.fit(train_data, train_label)
            model = "KNN"
        # ------------------------------------------------------

        #   SVC-------------------------------------------------
        elif model_id == 1:
            svc_parameters = {'kernel': ['rbf'],
                                'gamma': [1e-3, 1e-4],
                                 'C': [0.1, 1, 10]}
            scores = ['precision', 'recall', 'f1']
            #  グリッドサーチと交差検証法
            clf = GridSearchCV(svm.SVC(probability=True), svc_parameters, cv=5,
                               scoring='accuracy', n_jobs=-1, verbose=10)
            clf.fit(train_data, train_label)
            model = "SVC"
        # ------------------------------------------------------

        #   NN-------------------------------------------------
        elif model_id == 2:
            nn_parameters = [{
                # 最適化手法
                "solver": ['sgd', 'adam'],
                # 隠れ層の層の数と、各層のニューロンの数
                "hidden_layer_sizes": [(100, 100, 100, 10)],
                'activation': ["logistic", "relu", "tanh"],
            }]
            scores = ['precision', 'recall']
            clf = GridSearchCV(MLPClassifier(early_stopping=True), param_grid=nn_parameters, cv=5,
                               scoring='accuracy', n_jobs=-1, verbose=10)
            clf.fit(train_data, train_label)
            model = "NN"
        # ------------------------------------------------------
        else:
            sys.exit(1)

        print(clf.best_estimator_)
        print(classification_report(test_label, clf.predict(test_data)))
        pickle.dump(clf, open('{}/{}Model_{}.pkl'.format(model_pass, lr_label[i], model), 'wb'))

        # モデルを読み込む --- (*4)
        pred = clf.predict(test_data)
        print(pred)
        print(clf.predict_proba(test_data))
        true_label = test_label.tolist()
        labels = SSEnum.HandEnum.NAME_LIST.value

        c_matrix = confusion_matrix(true_label, pred)
        print(c_matrix)
        cm_pd = pd.DataFrame(c_matrix, columns=labels, index=labels)
        sum = int(test_data.shape[0]) / int(labels.__len__())  # 各ラベルの数
        # plt.tick_params(labelsize=10)
        ax[model_id].tick_params(axis='x', labelsize=8)
        ax[model_id].tick_params(axis='y', labelsize=8)
        ax[model_id].set_title(model_name[model_id])
        if model_id == 2:
            sns.heatmap(cm_pd / sum * 100, annot=True, cmap="Blues", fmt='.4g', ax=ax[model_id])  # パーセントで表示
        else:
            sns.heatmap(cm_pd / sum * 100, annot=True, cmap="Blues", fmt='.4g', cbar=False, ax=ax[model_id])
        with open('{}/{}CM_{}.csv'.format(result_pass, lr_label[i], model), 'w') as file:
            writer = csv.writer(file, lineterminator='\n')
            writer.writerows(c_matrix)
        print(classification_report(test_label, pred))
        print("正答率 = ", metrics.accuracy_score(test_label, pred))
        print("------------- {} end ------------\n".format(model_label[model_id]))


    plt.savefig('{}/{}CM.png'.format(result_pass, lr_label[i]))
    print("------------- {} end ------------\n".format(lr_label[i]))
plt.show()
