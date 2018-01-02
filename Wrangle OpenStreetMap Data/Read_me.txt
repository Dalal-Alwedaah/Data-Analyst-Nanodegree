Project Name: OpenStreetMap Project Data Wrangling with MongoDB¶
Author: Dalal Alwedaah

Map Area: Boston, MA, United States

https://mapzen.com/data/metro-extracts/your-extracts/3613179a3346

I use part of boston city for this project. boston is the capital and most populous city of the Commonwealth of
 Massachusetts in the United States. I choose it because its hisorical importance.

Getting Started:
1. run street_map_project_audit.py
2. run street_map_project_process.py
3.Start MongoDB using command line
		cd "C:\"
		"C:\Program Files\MongoDB\Server\3.4\bin\mongod.exe"
4. open command line and run this command 
		mongoimport -d boston_part -c boston_part_data --file C:\Users\ABDULL\Desktop\Misk\P3\streetmap\boston_part.osm.json
5. run street_map_project_queries.py 

Prerequisites:
python 2.7
mangodb
