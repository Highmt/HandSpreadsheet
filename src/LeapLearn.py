import csv
import datetime

import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.externals import joblib
from sklearn.metrics import classification_report, confusion_matrix

from sklearn.model_selection import train_test_split, GridSearchCV
from pycm import ConfusionMatrix

import os
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from src.SSEnum import SSEnum

np.random.seed(1671)  # for reproducibility

# network and training
DROPOUT = 0.2

# data: shuffled and split between train and test sets
read_data0 = pd.read_csv('./data/FREE_0.csv', sep=',', index_col=0)
read_data1 = pd.read_csv('./data/PINCH_IN_1.csv', sep=',', index_col=0)
read_data2 = pd.read_csv('./data/PINCH_OUT_2.csv', sep=',', index_col=0)
read_data3 = pd.read_csv('./data/PALM_OPEN_3.csv', sep=',', index_col=0)
read_data4 = pd.read_csv('./data/GRAB_4.csv', sep=',', index_col=0)
read_data = pd.concat([read_data0, read_data1, read_data2, read_data3, read_data4], ignore_index=True)
data = read_data.drop("label", axis=1).values
label = read_data["label"].values


train_data, test_data, train_label, test_label = train_test_split(data, label, test_size=0.2, stratify=label)

# normalize
print(train_data.shape[0], 'train samples')
print(test_data.shape[0], 'test samples')

knn_parameters = {'n_neighbors': [7, 11, 19],
                    'weights': ['uniform', 'distance'],
                    'metric': ['euclidean', 'manhattan']
                  }
scores = ['precision', 'recall', 'f1']

print("train start")
print("# Tuning hyper-parameters for accuracy")

#  グリッドサーチと交差検証法
clf = GridSearchCV(KNeighborsClassifier(), knn_parameters, cv=5,
                   scoring='accuracy', n_jobs=-1)
clf.fit(train_data, train_label)
print(clf.best_estimator_)
print(classification_report(test_label, clf.predict(test_data)))
nowTime = datetime.datetime.now().strftime('%Y%m%d%H%M')
joblib.dump(clf, './learnModel/KNN_{}.pkl'.format(nowTime))

# モデルを読み込む --- (*4)

pred = clf.predict(test_data)
touch_true = test_label.tolist()
labels = ["FREE", "PINCH_IN", "PINCH_OUT", "PALM_OPEN", "GRAB"]

c_matrix = confusion_matrix(touch_true, pred)
print(c_matrix)
cm_pd = pd.DataFrame(c_matrix, columns=labels, index=labels)
sum = int(test_data.shape[0]) / int(labels.__len__())  # 各ラベルの数
sns.heatmap(cm_pd / sum, annot=True, cmap="Reds", fmt='.4g')  #  正規化したものを表示
plt.savefig('./learningResult/CM_{}.png'.format(nowTime))
with open('./learningResult/CM_{}.csv'.format(nowTime), 'w') as file:
    writer = csv.writer(file, lineterminator='\n')
    writer.writerows(c_matrix)
print(classification_report(test_label, pred))
print("正答率 = ", metrics.accuracy_score(test_label, pred))
