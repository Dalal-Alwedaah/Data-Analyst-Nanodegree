#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
import pprint

def count_tags(filename):
        # YOUR CODE HERE
        #tree = ET.parse(filename)
        #root = tree.getroot()
        tags = {'bounds': 0,
                     'member': 0,
                     'nd': 0,
                     'node': 0,
                     'osm': 0,
                     'relation': 0,
                     'tag': 0,
                     'way': 0}
        
        for event, element in ET.iterparse(filename):
            tags[element.tag]+= 1
        return tags


def test():

    tags = count_tags(r'C:\Users\ABDULL\Desktop\Misk\p3\streetmap\boston_part.osm')
    #tags = count_tags(r'C:\Users\ABDULL\Desktop\Misk\p3\streetmap\smallareaboston.osm')
    pprint.pprint(tags)
    
    

if __name__ == "__main__":
    test()
