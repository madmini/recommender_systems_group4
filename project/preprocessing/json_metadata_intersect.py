import csv
import os

json_folder_path = r'D:\miniGlump\RecommenderSystems\assets\extracted_content_ml-latest'
movies_csv_paths = [
    r'D:\miniGlump\RecommenderSystems\assets\ml-20m',
    r'D:\miniGlump\RecommenderSystems\assets\ml-25m',

]

set_json = set()
for name in os.listdir(json_folder_path):
    set_json.add(int(name.rstrip('.json')))

print('json: ', len(set_json))

for path in movies_csv_paths:

    set_csv = set()
    with open(path + r'\movies.csv', encoding='utf8') as f:
        reader = csv.reader(f)
        next(reader)

        for row in reader:
            set_csv.add(int(row[0]))

    print(path)
    print('csv: ', len(set_csv), ' intersect: ', len(set_json.intersection(set_csv)))
