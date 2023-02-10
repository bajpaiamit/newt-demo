from google.cloud import storage
import os
from datetime import datetime
import json
import csv
import pandas as pd
import sys
import time


bucket_name = os.environ["BUCKET_NAME"]
project_id = os.environ["PROJECT_ID"]


st_client = storage.Client()

bucket = st_client.get_bucket(bucket_name)


def dt_schema():
    for blob in bucket.list_blobs(prefix="schema_map/"):
        if "DT_Map.json" in blob.name:
            data = json.loads(blob.download_as_string())
            return data


try:
    mapping_object = dt_schema()
    if mapping_object:
        tab_schema = []
        tab_name = sys.argv[1]
        for blob in bucket.list_blobs(prefix="schema_map/"):
            if tab_name+".csv" in blob.name:
                df=pd.read_csv("gs://"+bucket_name+"/"+blob.name)
                for index, row in df.iterrows():
                    type_argument = ""
                    split_dt = row["DATATYPE"].strip().split("(")[0]
                    datatype = mapping_object[split_dt]
                    if 'string(' in row['DATATYPE']:
                        max_length = row['DATATYPE'].split('(')[1].split(')')[0]
                        bq_type = {"name": row["COLUMNNAME"], "type": mapping_object[row['DATATYPE'].split('(')[0]], "maxLength": max_length}
                    elif 'nvarchar(' in row['DATATYPE']:
                        if 'max' in row['DATATYPE']:
                            bq_type = {"name": row["COLUMNNAME"], "type": mapping_object[row['DATATYPE'].split('(')[0]]}
                        else:
                            max_length = row['DATATYPE'].split('(')[1].split(')')[0]
                            bq_type = {"name": row["COLUMNNAME"], "type": mapping_object[row['DATATYPE'].split('(')[0]], "maxLength": max_length}
                    elif 'decimal(' in row['DATATYPE']:
                        precision, scale = row['DATATYPE'].split('(')[1].split(')')[0].split(',')
                        bq_type = {"name": row["COLUMNNAME"], "type": mapping_object[row['DATATYPE'].split('(')[0]], "precision": precision, "scale": scale}
                    else:
                        bq_type = {"name": row["COLUMNNAME"], "type": datatype}

                    tab_schema.append(bq_type)
                    time.sleep(1) 
                blob = bucket.blob(f"table_schema/{tab_name}.json")
                blob.upload_from_string(
                    data=json.dumps(tab_schema, indent=2),
                    content_type='application/json'
                    )   
                print("Successfully uploaded the schema file {} in the bucket".format(tab_name))
except Exception as e:
    raise Exception(f"error: {e} ")
