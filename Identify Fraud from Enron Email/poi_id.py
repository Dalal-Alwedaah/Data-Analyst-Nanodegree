#!/usr/bin/python

import sys
import pickle
import matplotlib.pyplot as plt

sys.path.append("../tools/")

from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn import tree
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.metrics import classification_report, accuracy_score
from sklearn.grid_search import GridSearchCV
from sklearn.feature_selection import SelectKBest, chi2, f_classif
from sklearn.cross_validation import train_test_split, StratifiedShuffleSplit

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data, test_classifier


### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
POI_label = ['poi']

financial_features = ['salary',
                      'deferral_payments',
                      'total_payments',
                      'loan_advances',
                      'bonus',
                      'restricted_stock_deferred',
                      'deferred_income',
                      'total_stock_value',
                      'expenses',
                      'exercised_stock_options',
                      'other',
                      'long_term_incentive',
                      'restricted_stock',
                      'director_fees'] 

email_features = ['to_messages',
                  'from_poi_to_this_person',
                  'from_messages',
                  'from_this_person_to_poi',
                  'shared_receipt_with_poi']

 
features_list = POI_label + financial_features + email_features
# You will need to use more features

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

### Task 2: Remove outliers

#Visualise outliers#

def PlotOutlier(data_dict, feature_x, feature_y):
    """ Plot with flag = True in Red """
    data = featureFormat(data_dict, [feature_x, feature_y, 'poi'])
    for point in data:
        x = point[0]
        y = point[1]
        poi = point[2]
        if poi:
            color = 'red'
        else:
            color = 'blue'
        plt.scatter(x, y, color=color)
    plt.xlabel(feature_x)
    plt.ylabel(feature_y)
    plt.show()
    
#print(PlotOutlier(data_dict, 'salary', 'bonus'))

#  from outiers mini project we found that total is an outlier
data_dict.pop("TOTAL", 0 )
#  featureFormat function will handle zero or NAN data point



### Task 3: Create new feature(s)

### Store to my_dataset for easy export below.
my_dataset = data_dict


# add new features to dataset
def compute_fraction(poi_messages, all_messages):    
    if poi_messages == 'NaN' or all_messages == 'NaN':
        return 0.
    fraction = poi_messages / all_messages
    return fraction

for name in my_dataset:
    data_point = my_dataset[name]
    from_poi_to_this_person = data_point["from_poi_to_this_person"]
    to_messages = data_point["to_messages"]
    fraction_from_poi = compute_fraction(from_poi_to_this_person, to_messages)
    data_point["fraction_from_poi"] = fraction_from_poi
    from_this_person_to_poi = data_point["from_this_person_to_poi"]
    from_messages = data_point["from_messages"]
    fraction_to_poi = compute_fraction(from_this_person_to_poi, from_messages)
    data_point["fraction_to_poi"] = fraction_to_poi

# create new copies of feature list for grading
my_feature_list = features_list+['fraction_from_poi', 'fraction_to_poi']

#my_feature_list.remove('to_messages')  
#my_feature_list.remove('from_poi_to_this_person')
#my_feature_list.remove('from_messages')
#my_feature_list.remove('from_this_person_to_poi')

# get K-best features
num_features = 10 

# feature selection using SelectKBest
def get_k_best(data_dict, features_list, num_features):
    data = featureFormat(data_dict, features_list)
    target, features = targetFeatureSplit(data)

    clf = SelectKBest(k = num_features)
    clf = clf.fit(features, target)
    feature_weights = {}
    for idx, feature in enumerate(clf.scores_):
        feature_weights[features_list[1:][idx]] = feature
    best_features = sorted(feature_weights.items(), key = lambda k: k[1], reverse = True)[:num_features]
    new_features = []
    for k, v in best_features:
        #print k,v
        new_features.append(k)
    return new_features

####--------------------------------
#my_feature_list = features_list
####--------------------------------------

best_features = get_k_best(my_dataset, features_list, num_features)

features_list = POI_label + best_features

# print selected features
print "{0} selected features: {1}\n".format(len(features_list) - 1, features_list[1:])

### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list)
labels, features = targetFeatureSplit(data)

# scale features using min-max scaler

from sklearn import preprocessing
scaler = preprocessing.MinMaxScaler()
features = scaler.fit_transform(features)


'''
### Store to my_dataset for easy export below.
my_dataset = data_dict

### Extract features and labels from dataset for local testing

data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)
'''
### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

# Provided to give you a starting point. Try a variety of classifiers.

#clf = GaussianNB()

#----------------------------------------------------------------------------------------------------------------
from sklearn.feature_selection import SelectKBest
from sklearn import cross_validation
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import StratifiedShuffleSplit
from numpy import mean
from tester import test_classifier
from sklearn.linear_model import LogisticRegression
def evaluate(clf, dataset, feature_list, features, labels, num_iter, params):
    """
    Function used to evaluate our algorithm -- prints out the mean precision, recall, and accuracy.
    :param clf: Classifier algorithm (e.g. LogisticRegression(), DecisionTreeClassifier()
    :param features:
    :param labels: Feature we're trying to classify -- POI / non-POI
    :param num_iter: Amount of time we should iterate through the data -- 50 in this case
    :param params: Parameters used in the classifier pipeline.
                    e.g. {
                        "clf__criterion": ["gini", "entropy"],
                        "clf__min_samples_split": [10,15,20,25]
                    }
    :return: Prints the accuracy, precision, and recall score.
    """

    features_train, features_test, labels_train, labels_test = \
        train_test_split(features, labels, test_size=0.3, random_state=42)



    precision_values = []
    recall_values = []
    accuracy_values = []
    print clf
    for i in xrange(0, num_iter):
        #print params
        clf = GridSearchCV(clf, params, scoring = 'f1_weighted',)
        clf.fit(features_train, labels_train)
        print '*****************************'
        print clf.best_estimator_
        print clf.best_params_

        clf = clf.best_estimator_
        #test_classifier(clf, dataset, feature_list)
        pred = clf.predict(features_test)
        precision_values.append(precision_score(labels_test, pred))
        recall_values.append(recall_score(labels_test, pred))
        accuracy_values.append(accuracy_score(labels_test, pred))
    print 'Recall score: ', mean(recall_values)
    print 'Precision score: ', mean(precision_values)
    print 'Accuracy score: ' , mean(accuracy_values)

classifiers = [{'classifier': GaussianNB(),
                'params': {}
                    },
               {'classifier': LogisticRegression(),
                'params': {  "clf__C": [0.05, 0.5, 1, 10, 10**2, 10**3, 10**5, 10**10, 10**15],
                    "clf__tol":[10**-1, 10**-2, 10**-4, 10**-5, 10**-6, 10**-10, 10**-15],
                    "clf__class_weight":['auto']
}},
               {'classifier': AdaBoostClassifier(),
                'params': {
                      "clf__n_estimators" : [5, 8, 10, 20, 30, 50, 100],
                      "clf__learning_rate" : [0.025, 0.05, 0.1, 0.5, 1, 2, 4, 6]
                    }},
               {'classifier': tree.DecisionTreeClassifier(),
                'params':
                    {
                        "clf__criterion": ["gini", "entropy"],
                        "clf__min_samples_split": [10,15,20,25]
                    }
}]
'''
scaler = MinMaxScaler()
for c in classifiers:
    clf = Pipeline(steps=[("scaler", scaler), ("skb", SelectKBest(k='all')),
                          ("clf", c['classifier'])])
    evaluate(clf, my_dataset, features_list, features, labels, 50, c['params'])
'''



#clf = Pipeline(steps=[("scaler", scaler),("skb", SelectKBest(k='all')),("clf", GaussianNB())])
#clf = Pipeline(steps=[("scaler", scaler),("skb", SelectKBest(k='all')),
#                      ("clf", KNeighborsClassifier(weights= 'uniform', n_neighbors= 6))])
#clf = Pipeline(steps=[("scaler", scaler),("skb", SelectKBest(k='all')),
#                      ("clf", AdaBoostClassifier(learning_rate= 1, n_estimators= 30))])
#clf = Pipeline(steps=[("scaler", scaler),("skb", SelectKBest(k='all')),
#                      ("clf", tree.DecisionTreeClassifier(criterion = 'gini', min_samples_split = 25))])

#the best algorithm
clf = Pipeline(steps=[("scaler", scaler),
                      ("skb", SelectKBest(k='all')),
                        ("clf", LogisticRegression(tol=0.1, C = 0.05, class_weight='auto'))])

#------------------------------------------------------------------------------------------------------------------------
### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html






# Example starting point. Try investigating other evaluation techniques!
'''from sklearn.cross_validation import train_test_split
features_train, features_test, labels_train, labels_test = \
    train_test_split(features, labels, test_size=0.3, random_state=42)'''

### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, features_list)
