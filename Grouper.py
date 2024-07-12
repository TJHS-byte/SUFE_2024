import random
from pathlib import Path
import csv
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import davies_bouldin_score, calinski_harabasz_score, silhouette_score
import pandas as pd
from Weighter import synthetic_control
p = Path('D:\\SUFE\\Project0\\output_csvs')
all_funds_files = p.rglob("*.csv")


def calculate_distance(vector_a,vector_b):
    row_upper_limit = len(vector_a) + 1
    col_upper_limit = len(vector_b) + 1

    distance_matrix = [[0 for _ in range(col_upper_limit)] for _ in range(row_upper_limit)]

    for i in range(row_upper_limit):
        distance_matrix[i][0] = float('inf')
    for j in range(col_upper_limit):
        distance_matrix[0][j] = float('inf')

    distance_matrix[0][0] = 0

    for i in range(1,row_upper_limit):
        for j in range(1,col_upper_limit):
            current_cost = ((vector_a[i-1]-vector_b[j-1])**2)**0.5
            distance_matrix[i][j] = current_cost + min(distance_matrix[i-1][j-1], distance_matrix[i][j-1], distance_matrix[i-1][j])

    return distance_matrix[-1][-1]


class fund:
    def __init__(self, name):
        self.name = name
        self.open = []
        self.close = []
        self.high = []
        self.low = []
        self.volume = []

    def add_info(self, val):
        try:
            self.open.append(float(val[2]))
        except ValueError:
            self.open.append(float(0))

        try:
            self.high.append(float(val[3]))
        except ValueError:
            self.high.append(float(0))

        try:
            self.low.append(float(val[4]))
        except ValueError:
            self.low.append(float(0))

        try:
            self.close.append(float(val[5]))
        except ValueError:
            self.close.append(float(0))

        try:
            self.volume.append(float(val[6]))
        except ValueError:
            self.volume.append(float(0))

    def inter_fund_distance(self, other,time_scale):
        distance = 0

        control_dataframe = pd.read_csv("ETF_idx.csv")
        treatment_dataframe = pd.read_csv("etf_fund_data.csv")
        comprehensive_dataframe = pd.concat([control_dataframe, treatment_dataframe],
                                            ignore_index = True)
        control_funds_set = set()
        with open("ETF_idx.csv", "r") as control_group:
            cursor = csv.reader(control_group)
            for line in cursor:
                if line[0] != "Code":
                    control_funds_set.add(line[0])

        control_funds_lst = list(control_funds_set)
        coef = synthetic_control(comprehensive_dataframe,control_funds_lst,"volume",['512760.SZ', '519674.OF'],time_scale)

        distance += coef[0]*calculate_distance(self.open, other.open)
        distance += coef[1]*calculate_distance(self.close, other.close)
        distance += coef[2]*calculate_distance(self.high, other.high)
        distance += coef[3]*calculate_distance(self.low, other.low)
        # distance += calculate_distance(self.volume, other.volume)
        return distance


def rolling_window_sampling(data, window_size=30):
    if len(data) < window_size:
        return data
    start_index = random.randint(0, len(data) - window_size)
    return data[start_index:start_index + window_size]


fund_objs = []
sampled_dates = []
for file_obj in all_funds_files:
    fund_obj = fund(file_obj.stem)
    with open(file_obj, mode='r', newline='', encoding='utf-8') as file:
        cursor = csv.reader(file)
        lines = list(cursor)
        filtered_lines = [line for line in lines if line[0] != "Code"]
        sampled_lines = rolling_window_sampling(filtered_lines, 60)
        for line in sampled_lines:
            fund_obj.add_info(line)
            sampled_dates.append(line[1])
    fund_objs.append(fund_obj)

num_of_funds = len(fund_objs)
intra_fund_distance_matrix = np.zeros((num_of_funds, num_of_funds))

for i in range(num_of_funds):
    for j in range(num_of_funds):
        intra_fund_distance_matrix[i][j] = fund_objs[i].inter_fund_distance(fund_objs[j],sampled_dates)

num_clusters = 8
kmeans = KMeans(n_clusters=num_clusters, random_state=0, n_init='auto')
kmeans.fit(intra_fund_distance_matrix)


labels = kmeans.labels_
db_score = davies_bouldin_score(intra_fund_distance_matrix, labels)
ch_score = calinski_harabasz_score(intra_fund_distance_matrix, labels)
sil_score = silhouette_score(intra_fund_distance_matrix, labels)

print(f"Davies-Bouldin Index: {db_score}")
print(f"Calinski-Harabasz Index: {ch_score}")
print(f"Silhouette Score: {sil_score}")

#for i, label in enumerate(kmeans.labels_):
#    print(f"Fund {fund_objs[i].name}: Cluster {label}")

#print("Cluster centers:", kmeans.cluster_centers_)

