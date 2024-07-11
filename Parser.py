import csv
import os
import pandas as pd
tags = set([])

def read_csv(file_path):
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row[0] != "Code":
                tags.add(row[0])
    return

read_csv("ETF_idx.csv")
dataframe = pd.read_csv("ETF_idx.csv")

new_directory = "output_csvs"
os.makedirs(new_directory, exist_ok=True)


for tag in tags:
    sub_dataframe = dataframe.loc[(dataframe["Code"]==tag)]
    sub_dataframe.to_csv(os.path.join(new_directory, f"{tag}.csv"),index = False)