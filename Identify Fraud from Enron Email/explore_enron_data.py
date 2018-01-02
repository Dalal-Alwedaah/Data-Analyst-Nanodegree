#!/usr/bin/python

import pickle
import pandas as pd
#load dataset from pickle file
enron_data = pickle.load(open("../final_project/final_project_dataset.pkl", "r"))

#creating features list
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

#converting dataset into data frame
enron_df = pd.DataFrame.from_dict(enron_data ,orient = 'index', dtype = float)

#print featuer names
print "\nfeatuer names"
enron_df.info() 

#size of enron data
print "\nsize of enron data"
data_count = len(enron_data)
print data_count

#Features in the enron dataset
print "\nFeatures in the enron dataset"
print len (enron_data["SKILLING JEFFREY K"])

#finding POIs in the Enron Data
print "\nfinding POIs in the Enron Data"
count = 0
for person_name, value in enron_data.iteritems():
    if(enron_data[person_name]["poi"]==1):
        count += 1

print count
print "%", (count/float(data_count))*100

#How many people in the E+F dataset (as it currently exists) have “NaN” for each feature?
print "\n How many people in the E+F dataset (as it currently exists) have “NaN” for each feature?"
count_list = []
for i, feature_name in enumerate(features_list):
    count_list.append(0)
    for feature_person, value in enron_data.iteritems():
        if(enron_data[feature_person][feature_name] == 'NaN' ):
            count_list[i] += 1
    percentage = (count_list[i] / float(data_count))*100
    print "\n", feature_name
    print "count:", count_list[i],",%",percentage
#for emails
email_count = 0
for person_name, value in enron_data.iteritems():
    if(enron_data[person_name]["email_address"] == 'NaN' ):
        email_count += 1
print "email_address" ,email_count, (email_count / float(data_count))*100

#how many POIs Exist?
print "\n how many POIs Exist?"
with open("../final_project/poi_names.txt", 'r') as f:
    f.readline()
    f.readline()
    POIs_Names = [line.strip() for line in f]
print len(POIs_Names)

unique_names = set()
for name in POIs_Names:
    new_name = name[4:].lower()
    unique_names.add(new_name)
    #print name ,"=>", new_name
for person_name, value in enron_data.iteritems():
    if(enron_data[person_name]["poi"]==1):
        name_list = person_name.split()
        if len(name_list[1])>2:
            new_person_name = name_list[0].lower() + ", " + name_list[1].lower()
        else:
            new_person_name = name_list[0].lower() + ", " + name_list[2].lower()
        #print person_name ,"=>", new_person_name
        unique_names.add(new_person_name)
print len(unique_names)


