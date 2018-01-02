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
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
##-----------------------------------------------------------------------##
def audit_postcode(postcode_types, postcode):
        
        if len(postcode) != 5 :
            print postcode
            postcode_types.add(postcode)
        else:
            try:
                val = int(postcode)
            except ValueError:
                postcode_types.add(postcode)

def is_postcode(elem):
    return (elem.attrib['k'] == "addr:postcode")

##-----------------------------------------------------------------------##
#OSMFILE = "smallareaboston.osm"
OSMFILE = "boston_part.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "At", "West", "North ", "East", "South", "oppsite"]

# UPDATE THIS VARIABLE
mapping = { "St": "Street",
            "St.": "Street",
            "Rd.": "Road",
            "Ave": "Avenue",
            "Ave.": "Avenue",
            "Pk" : "Parkway",
            "Sq" : "Square",
            "@" : "At",
            "W" : "West",
            "N" : "North ",
            "E" : "East",
            "S" : "South",
            "W." : "West",
            "N." : "North ",
            "E." : "East",
            "S." : "South",
            "opp" : "oppsite",
            "opp." : "oppsite"
            }


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
                if street_type in mapping.keys():
                        #print street_type , street_name
                        street_types[street_type].add(street_name)
                        return True
        return False


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    postcode_types = set()
    
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
                if is_postcode(tag):
                    audit_postcode(postcode_types, tag.attrib['v'])
    osm_file.close()
    return street_types, postcode_types


#-----------------------------------------------------------------------##
       

def test():
    
    #audit data    
    st_types , pc_types= audit(OSMFILE)
    pprint.pprint(dict(st_types))
    pprint.pprint(pc_types)
    
    
    
    
if __name__ == "__main__":
    test()
