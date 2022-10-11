import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics

def main():
    # load the dataset from the csv file
    colNames = ['winner', 'red_top', 'red_jungle', 'red_mid', 'red_adc', 'red_support', 'blue_top', 'blue_jungle', 'blue_mid', 'blue_adc', 'blue_support']
    filename = '/Users/adamharris/Documents/DraftCompanion/DataCollection/LogisticalRegression/matchDataNumbered.csv'
    matches = pd.read_csv(filename, usecols=colNames)
    print(matches)

    # now assign the features and target variables
    featureCols = ['red_top', 'red_jungle', 'red_mid', 'red_adc', 'red_support', 'blue_top', 'blue_jungle', 'blue_mid', 'blue_adc', 'blue_support']
    X = matches[featureCols]
    y = matches.winner

    # split the data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=33)

    # instantiate the model
    logreg = LogisticRegression(random_state=33)
    logreg.fit(X_train, y_train)

    yPred = logreg.predict(X_test)

    # evaluate the model
    cnfMatrix = metrics.confusion_matrix(y_test, yPred)

    # visualize the performance of the model
    classNames = ['red', 'blue']
    fig,ax = plt.subplots()
    tickMarks = np.arange(len(classNames))
    plt.xticks(tickMarks, classNames)
    plt.yticks(tickMarks, classNames)

    # create the heatmap
    sns.heatmap(pd.DataFrame(cnfMatrix), annot=True, cmap='YlGnBu', fmt='g')
    ax.xaxis.set_label_position("top")
    plt.tight_layout()
    plt.title('Confusion matrix', y=1.1)
    plt.ylabel('Actual label')
    plt.xlabel('Predicted label')
    plt.show()

    # evaluation metrics
    target_names = ['red wins', 'blue wins']
    print(metrics.classification_report(y_test, yPred, target_names=target_names))

if __name__ == "__main__":
    main()