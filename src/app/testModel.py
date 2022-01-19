import csv
import pickle
import pandas as pd
from matplotlib import pyplot as plt, gridspec
from sklearn import metrics
from sklearn.metrics import confusion_matrix, classification_report

from res.SSEnum import HandEnum, FeatureEnum
import seaborn as sns

from src.HandScensing.HandListener import HandData
from src.HandScensing.Predictor import convertLearningPS

lr_label = ['left', 'right']
model_label = ['KNN', 'SVC', 'NN']
model_name = ['KNeighborsClassifier', 'SVC', 'MLPClassifier']
model_ver = "p0"
data_ver = "test"
model_pass = '../../res/learningModel/{}'.format(model_ver)
data_pass = '../../res/data/train/saved/{}'.format(data_ver)

accuracy = [0, 0, 0]


def convertLearningDF(data: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame(columns=FeatureEnum.FEATURE_LIST.value)
    hand = HandData()
    for i, ps in data.iterrows():
        hand.loadPS(ps)
        d = convertLearningPS(hand)
        df = df.append(d, ignore_index=True)
    return df


def main():
    for i in range(2):
        print("------------- {} start -------------".format(lr_label[i]))
        read_data = pd.read_csv(data_pass + '/' + lr_label[i] + 'Data.csv', sep=',', index_col=0)
        data = convertLearningDF(read_data).drop("Label", axis=1).values
        label = read_data["Label"].values

        fig = plt.figure(figsize=(15, 6))
        plt.suptitle('confusion matrix of test data for {} hand '.format(lr_label[i]))
        spec = gridspec.GridSpec(ncols=3, nrows=1, width_ratios=[1, 1, 1.3])
        # 操作の数だけグラフを作成
        ax = [fig.add_subplot(spec[i]) for i in range(len(model_label))]
        for model_id in range(3):
            print("------------- {} start ------------\n".format(model_label[model_id]))
            model = pickle.load(open('{}/{}Model_{}.pkl'.format(model_pass, lr_label[i], model_label[model_id], model_ver), 'rb'))
            # モデルを読み込む --- (*4)
            pred = model.predict(data)
            print(pred)
            print(model.predict_proba(data))
            true_label = label.tolist()
            labels = HandEnum.NAME_LIST.value

            c_matrix = confusion_matrix(true_label, pred)
            print(c_matrix)
            cm_pd = pd.DataFrame(c_matrix, columns=labels, index=labels)
            sum = int(data.shape[0]) / int(labels.__len__())  # 各ラベルの数
            ax[model_id].tick_params(axis='x', labelsize=8)
            ax[model_id].tick_params(axis='y', labelsize=8)
            ax[model_id].set_title(model_name[model_id])
            if model_id == 2:
                sns.heatmap(cm_pd / sum * 100, annot=True, cmap="Blues", fmt='.4g', ax=ax[model_id])  # パーセントで表示
            else:
                sns.heatmap(cm_pd / sum * 100, annot=True, cmap="Blues", fmt='.4g', cbar=False, ax=ax[model_id])

            with open('../../res/learningResult/check/{}CM_{}.csv'.format(lr_label[i], model_label[model_id]), 'w') as file:
                writer = csv.writer(file, lineterminator='\n')
                writer.writerows(c_matrix)
            print(classification_report(label, pred))
            accuracy[model_id] = accuracy[model_id] + metrics.accuracy_score(label, pred)
            print("正答率 = ", metrics.accuracy_score(label, pred))
            print("------------- {} end ------------\n".format(model_label[model_id]))

        plt.savefig('../../res/learningResult/check/{}CM.png'.format(lr_label[i]))
        print("------------- {} end ------------".format(lr_label[i]))

    for model_id in range(3):
        print("{}: {}".format(model_name[model_id], accuracy[model_id] / 2))
    plt.show()

if __name__ == "__main__":
    main()