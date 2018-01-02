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

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

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

##-----------------------------------------------------------------------##
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



def update_name(name, mapping):

    # YOUR CODE HERE
    m =street_type_re.search(name) 
    if m:
        name = re.sub(street_type_re,mapping[m.group()],name)

    return name

##-----------------------------------------------------------------------##
def shape_element(element):
    
    node = {}
    address={}
    created={}
    node_refs=[]
    pos = []
    street_types = defaultdict(set)
    #print element.tag, element.attrib
    if element.tag == "node" or element.tag == "way" :
        # create a key in the node dictionary 'type'
        # give it the value of the element tag
        node['type']=element.tag
        # loop through the children of the element
        for key in element.attrib:
            #print key, element.attrib[key]
            #if child key in CREATED list
            if key in CREATED:
                # create a key in the created dictionary 
                # give it the value of the child 
                created[key]=element.attrib[key]
            
            elif (key == 'lat') or (key == 'lon'):
                #if attributes is latitude and longitude
                #add it to a "pos" array
                pos.append(float(element.attrib[key]))
            else:
                # create a key in the node dictionary 
                # give it the value of the child
                node[key]= element.attrib[key]
        
        # if the list 'pos' exists
        if pos:
            # create a key in the node dictionary 'pos'
            # give it the value of the pos list
            node['pos']=pos
        # create a key in the node dictionary 'created'
        # give it the value of the created dictionary
        node['created']=created

        # loop through the children of the element
        for child in element:
            # if the child element is 'nd'
            
            if child.tag == 'nd':
                # if one of the attributes of
                #the child element is 'ref'
                if child.attrib['ref']:
                    node_refs.append(child.attrib['ref'])
            # if the child element is 'tag'
            elif child.tag == 'tag':
                if re.search(problemchars, child.attrib['k']):
                    # if attribute keyname have problematic chars
                    pass
                elif child.attrib['k'].startswith('addr:'):
                    # if attribute keyname start with "addr:"
                    if child.attrib['k'].count(":") == 2:
                        # if attribute keyname have two colons
                        pass
                    else:
                        #remove "addr:" from the attribute keyname
                        updated_key_name=  child.attrib['k'][5:]
                        #print updated_key_name
                        if updated_key_name == "postcode":
                                address["postcode"]=re.sub("\D", "", child.attrib['v'])
                                if len(address["postcode"]) >5:
                                        address["postcode"] = address["postcode"][:5]
                                #print address["postcode"]
                        else:
                                address[updated_key_name]= child.attrib['v']
                elif child.attrib['k'] == "name":
                        if "&amp;" in child.attrib['v']:
                                att1,att2 = child.attrib['v'].spilt("&amp;")
                                node["name"] = att1
                                node["amenity"] = att2
                        else:
                                name = child.attrib['v']
                                new_name =""
                                for string in name.split():
                                        if(audit_street_type(street_types, string)):
                                                new_string = update_name(string, mapping)
                                                #print new_string
                                                new_name += new_string +" "
                                        else:
                                                new_name += string +" "
                                '''if (name.strip() != new_name.strip()):
                                        print name ," => " ,new_name'''                
                                node["name"] = new_name
                                        
                else:
                    # create a key in the node dictionary 
                    # give it the attribute value
                    node[child.attrib['k']]=child.attrib['v']
        # if the list 'address' exists
        if address:
            # create a key in the node dictionary 'address'
            # give it the value of the address dictionary
            node['address']=address
        # if the list 'node_refs' exists
        if node_refs:
            # create a key in the node dictionary 'node_ref'
            # give it the value of the node_refs list
            node['node_ref'] = node_refs
    if node:
        #print node
        return node
    else:
        return None

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


##-----------------------------------------------------------------------##
       

def test():

    print "process started ..."
    #convert osm file into well structured json file
    data = process_map(OSMFILE, False)
    #pprint.pprint(data)
    print "process complete"

    
    
if __name__ == "__main__":
    test()
