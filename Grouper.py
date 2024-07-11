from pathlib import Path
import csv

from sklearn.cluster import KMeans


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
            distance_matrix[i][j] = current_cost+min(distance_matrix[i-1][j-1],distance_matrix[i][j-1],distance_matrix[i-1][j])

    return distance_matrix[-1][-1]

class fund:
    def __init__(self,name):
        self.name=name
        self.open = []
        self.close = []
        self.high=[]
        self.low=[]
        self.volume=[]
    def add_info(self,val):
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

    def inter_fund_distance(self,other):
        distance = 0
        distance += calculate_distance(self.open,other.open)
        distance += calculate_distance(self.close, other.close)
        distance += calculate_distance(self.high, other.high)
        distance += calculate_distance(self.low, other.low)
        distance += calculate_distance(self.volume, other.volume)
        return distance

fund_objs=[]
for file_obj in all_funds_files:
    fund_obj = fund(file_obj.stem)
    with open(file_obj, mode='r', newline='', encoding='utf-8') as file:
        cursor = csv.reader(file)
        for line in cursor:
            if line[0]!="Code":
                fund_obj.add_info(line)
    fund_objs.append(fund_obj)

num_of_funds = len(fund_objs)
intra_fund_distance_matrix = [[0 for _ in range(num_of_funds)]for _ in range(num_of_funds)]

for i in range(num_of_funds):
    for j in range(num_of_funds):
        intra_fund_distance_matrix[i][j] = fund_objs[i].inter_fund_distance(fund_objs[j])

num_clusters = 10
kmeans = KMeans(n_clusters = num_clusters, random_state = 0, n_init = 'auto')
kmeans.fit(intra_fund_distance_matrix)


for i, label in enumerate(kmeans.labels_):
    print(f"Fund {fund_objs[i].name}: Cluster {label}")

print("Cluster centers:", kmeans.cluster_centers_)