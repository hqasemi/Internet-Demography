import pickle, os, numpy as np, matplotlib.pyplot as plt, math, matplotlib
import numpy


import networkx as nx
import matplotlib.pyplot as plt

DataSets = ['lacnic', 'arin', 'apnic', 'afrinic', 'ripencc'];

YearsToCheck = [2006, 2009, 2012, 2015, 2018];
slctdMonth = 6;
slctdDay = 1;
DatesToCheck = [i*10000+slctdMonth*100+slctdDay for i in YearsToCheck]#[20060601, 20090601, 20120601, 20150601, 20180601];
nan = float('nan')
def my_test_MetaData_ripe():
    for DataSetName in DataSets:
        print DataSetName
        if os.path.isfile('MetaData/' + DataSetName):
            [IPv4, IPv6, ASN] = load_obj('MetaData/' + DataSetName)
            #print type(IPv4)
            for year in ASN.keys():
                for month in ASN[year].keys():
                    for day in ASN[year][month].keys():
                        #print str(year)+'/'+str(month)+"/"+str(day)
                        for country in ASN[year][month][day].keys():
                            #print country
                            #if  country=="TotalNumber":
                            print "^^^^^^^^^^^^"
                            print country

                            print ASN[year][month][day][country]

def my_test_MetaData_CAIDA_relation():
    print " "


def load_obj(FileName):
    with open(FileName, 'rb') as f:
        return pickle.load(f)


def save_obj(FileName,obj):
    with open(FileName, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

# d = {'BBDD': [nan,nan,nan,nan,nan,nan,nan],
#  'AAAD': ['BBDD',nan,nan,nan,nan,nan,nan],
#  'AAFF': ['AAAD',nan,nan,nan,nan,nan,nan],
#  'MMCC': ['AAAD',nan,nan,nan,nan,nan,nan],
#  'KKLL': ['AAFF', 'MMCC', 'AAAD', 'BBDD',nan,nan,nan]}
# #g = nx.DiGraph()
# #undirected graph with self-loop and multiple (parallel) edges are not allowed
# g = nx.Graph()
# g.add_nodes_from(d.keys())
#
# for k, v in d.items():
#     g.add_edges_from(([(k, t) for t in v]))
#
# print  g.edges()
my_test_MetaData_ripe()