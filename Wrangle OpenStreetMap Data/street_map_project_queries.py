#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
from collections import defaultdict
from pymongo import MongoClient
import pprint
import re
import codecs
import json
from bson import json_util

##-----------------------------------------------------------------------##

#OSMFILE = "smallareaboston.osm"
OSMFILE = "boston_part.osm"

##-----------------------------------------------------------------------##

def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2 , default=json_util.default) + "\n")
                else:
                    fo.write(json.dumps(el, default=json_util.default)  + "\n")
        
    return data



def get_db():
    # For local use
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    # 'examples' here is the database name. It will be created if it does not exist.
    db = client.boston_part
    return db
##-----------------------------------------------------------------------##
def data_overview(db):
        
        # Number of documents
        print "\nNumber of documents \n"
        print db.boston_part_data.find().count()

        # Number of nodes
        print "\n Number of nodes\n"
        print db.boston_part_data.find({"type":"node"}).count()

        # Number of ways
        print "\nNumber of ways \n"
        print db.boston_part_data.find({"type":"way"}).count()

        # Number of unique users
        print "\nNumber of unique users \n"
        print len(db.boston_part_data.distinct("created.user"))

        # Top 3 contributing user
        print "\nTop 3 contributing user \n"
        topcon = db.boston_part_data.aggregate([{"$group":{"_id":"$created.user", "count":{"$sum":1}}},
                           {"$sort":{"count":-1}}, {"$limit":3}])
        print (list(topcon))

        # Number of users appearing only once (having 1 post)
        print "\nNumber of users appearing only once \n"
        onepostusers = db.boston_part_data.aggregate([{"$group":{"_id":"$created.user", "count":{"$sum":1}}},
                           {"$group":{"_id":"$count", "num_users":{"$sum":1}}},
                           {"$sort":{"_id":1}}, {"$limit":1}])# “_id” represents postcount
        print (list(onepostusers))

        # Most attribution
        results = db.boston_part_data.aggregate([{"$match":{"attribution":{"$exists":1}}},
                                                 {"$group": {"_id":"$attribution",
                                                "count":{"$sum":1}}}, {"$sort":{"count":-1}}])
        print ("\n Most attribution \n")
        pprint.pprint(list(results))
        
        # Sort postcodes by count, descending
        print "\nSort postcodes by count, descending \n"
        postcodes = db.boston_part_data.aggregate([{"$match":{"address.postcode":{"$exists":1}}},
                           {"$group":{"_id":"$address.postcode", "count":{"$sum":1}}},
                           {"$sort":{"count":-1}}])
        print (list(postcodes))


def MongoDB_queries(db):

    results = db.boston_part_data.aggregate([{"$match":{"address.postcode":{"$exists":1}}},
                                                 {"$group": {"_id":"$address.postcode",
                                                "count":{"$sum":1}}}, {"$sort":{"count":-1}}])
    print ("\nPostcode list\n")
    pprint.pprint(list(results))
    
    # Top 10 appearing amenities
    results = db.boston_part_data.aggregate([{"$match":{"amenity":{"$exists":1}}},
                                                 {"$group":{"_id":"$amenity","count":{"$sum":1}}},
                                                 {"$sort":{"count":-1}}, {"$limit":10}])
    print ("\nTop 10 appearing amenities\n")
    pprint.pprint(list(results))

    # Biggest religion (no surprise here)
    results = db.boston_part_data.aggregate([{"$match":{"amenity":{"$exists":1}, "amenity":"place_of_worship"}},
                                               {"$group":{"_id":"$religion", "count":{"$sum":1}}},
                                               {"$sort":{"count":-1}}, {"$limit":3}])
    print ("\n Biggest religion\n")
    pprint.pprint(list(results))

    # Most popular cuisines
    results = db.boston_part_data.aggregate([{"$match":{"amenity":{"$exists":1}, "amenity":"restaurant"}},
                                               {"$group":{"_id":"$cuisine", "count":{"$sum":1}}},
                                               {"$sort":{"count":-1}}, {"$limit":10}])
    print ("\n Most popular cuisines\n")
    pprint.pprint(list(results))

    #Restaurant list
    results = db.boston_part_data.aggregate([{'$match': {'amenity':'restaurant','name':{'$exists':1}}},
                                   {'$project':{'_id':'$name','cuisine':'$cuisine','contact':'$phone'}}])
    print ("\n Restaurant list\n")
    pprint.pprint(list(results))

    # Most popular cafe
    results = db.boston_part_data.aggregate([{"$match":{"amenity":{"$exists":1}, "amenity":"cafe"}},
                                               {"$group":{"_id":"$name", "count":{"$sum":1}}},
                                               {"$sort":{"count":-1}}, {"$limit":10}])
    print ("\n Most popular cafe\n")
    pprint.pprint(list(results))

    # Most popular fast food
    results = db.boston_part_data.aggregate([{"$match":{"amenity":{"$exists":1}, "amenity":"fast_food"}},
                                               {"$group":{"_id":"$name", "count":{"$sum":1}}},
                                               {"$sort":{"count":-1}}, {"$limit":10}])
    print ("\n Most popular fast food\n")
    pprint.pprint(list(results))

##-----------------------------------------------------------------------##
       

def test():

    #import json file into MangoDB using command line >>
    db = get_db()
    # test DB by printing random object
    print db.boston_part_data.find_one()

    # data overview
    data_overview(db)
    
    # queries        
    MongoDB_queries(db)
    
    
if __name__ == "__main__":
    test()
