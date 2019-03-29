import urllib2, pickle, os, StringIO, gzip, bz2
from cProfile import label

import networkx as nx
import matplotlib.pyplot as plt

# SamplingYears = range(1998,2020);
SamplingYears = [2006, 2009, 2012, 2015, 2018];
selectedMonths = [6];
DataSets = ['lacnic', 'arin', 'apnic', 'afrinic', 'ripencc'];

countryToAsnMatrix = {}
regionCountryAsnMatrix = {}

def save_obj(FileName, obj):
    with open(FileName, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(FileName):
    with open(FileName, 'rb') as f:
        return pickle.load(f)

def read_metadata_as_relationship():
    [p2pM, p2cM] = load_obj('MetaData/as_relation/as_relation_matrix.networkx')
    return [p2pM, p2cM]

def calculate_country_to_asn_matrix():
    #read metadata asn and calculate country to asn matrix
    for regionName in DataSets:
        if os.path.isfile('MetaData/' + regionName):
            ASN = load_obj('MetaData/' + regionName + '_asn')
            for year in ASN.keys():
                for month in ASN[year].keys():
                    for day in ASN[year][month].keys():
                        date = year * 10000 + month * 100 + day
                        countryToAsnMatrix[date] = {}
                        # print str(year)+'/'+str(month)+"/"+str(day)
                        for country in ASN[year][month][day].keys():
                            # print country
                            # if  country=="TotalNumber":
                            # print "^^^^^^^^^^^^"
                            # print country
                            # print ASN[year][month][day][country]

                            try:
                                countryToAsnMatrix[date][country] = calculateListOfAsnInCountry(ASN[year][month][day][country])
                            except Exception as e:
                                pass
                                #print date
                                print e
    # print len(countryToAsnMatrix.keys())
    return countryToAsnMatrix

def calculateListOfAsnInCountry (asnDirtyList):
    #cleansing for example:
    #   input: 134214,1,allocated|134206,1,allocated|134187,1,allocated|134171,1,allocated
    #   output:[134214,134206,134187,134171,134144]
    return [asnData.split(',')[0] for asnData in asnDirtyList.split('|')]

def calculateDegreeOfAllAsnsPerCountry ():
    # output: dictionary [date][country] [asn] [degree]
    [p2pCountryDegreeIntra, p2cCountryDegreeIntra, p2pCountryDegreeInter, p2cCountryDegreeInter] = [{}, {}, {}, {}]
    [p2pM, p2cM] = read_metadata_as_relationship()

    countryToAsnMatrix = calculate_country_to_asn_matrix()
    for year in SamplingYears:
        # for month in range(1, 13):
        for month in selectedMonths:
            date = year * 10000 + month * 100 + 01
            [p2pCountryDegreeIntra[date], p2cCountryDegreeIntra[date], p2pCountryDegreeInter[date], p2cCountryDegreeInter[date]] = [{}, {}, {}, {}]

            for countryName in countryToAsnMatrix[date].keys():
                for asn in p2cM[date].keys():
                    if asn in countryToAsnMatrix[date][countryName] and countryName != 'TotalNumber' and countryName != '':
                        for connected_asn in p2cM[date][asn]:
                            if connected_asn in countryToAsnMatrix[date][countryName]:
                                # so connected_asn is intra country
                                if countryName in p2cCountryDegreeIntra[date].keys():
                                    p2cCountryDegreeIntra[date][countryName] += 1
                                else:
                                    p2cCountryDegreeIntra[date][countryName] = 0
                               # p2cCountryDegreeIntra[date][countryName] += (1 if countryName in p2cCountryDegreeIntra[date].keys() else 0)
                                #len(p2cM[date][asn]) \
                                #+ (p2cCountryDegreeIntra[date][countryName] \
                                #if countryName in p2cCountryDegreeIntra[date].keys() else 0)
                            else:
                                if countryName in p2cCountryDegreeInter[date].keys():
                                    p2cCountryDegreeInter[date][countryName] += 1
                                else:
                                    p2cCountryDegreeInter[date][countryName] = 0
                                #p2cCountryDegreeInter[date][countryName] += (1 if countryName in p2cCountryDegreeInter[date].keys() else 0)
                                #len(p2cM[date][asn]) \
                                #+ (p2cCountryDegreeInter[date][countryName] \
                                #if countryName in p2cCountryDegreeInter[date].keys() else 0)
                        # if countryName == '': print countryName, " ", asn
                for asn in p2pM[date].keys():
                    if asn in countryToAsnMatrix[date][countryName] and countryName != 'TotalNumber' and countryName != '':
                        for connected_asn in p2pM[date][asn]:
                            if connected_asn in countryToAsnMatrix[date][countryName]:
                                #so connected_asn is intra country
                                if countryName in p2pCountryDegreeIntra[date].keys():
                                    p2pCountryDegreeIntra[date][countryName] += 1
                                else:
                                    p2pCountryDegreeIntra[date][countryName] = 0
                                #p2pCountryDegreeIntra[date][countryName] += (1 if countryName in p2pCountryDegreeIntra[date].keys() else 0)
                                #len(p2pM[date][asn]) \
                                #+ (p2pCountryDegreeIntra[date][countryName] \
                                #       if countryName in p2pCountryDegreeIntra[date].keys() else 0)
                            else:
                                if countryName in p2pCountryDegreeInter[date].keys():
                                    p2pCountryDegreeInter[date][countryName] += 1
                                else:
                                    p2pCountryDegreeInter[date][countryName] = 0
                                #p2pCountryDegreeIntra[date][countryName] += (1 if countryName in p2pCountryDegreeIntra[date].keys() else 0)
                                #len(p2pM[date][asn]) \
                                #+ (p2pCountryDegreeInter[date][countryName] \
                                #if countryName in p2pCountryDegreeInter[date].keys() else 0)
                        # if countryName == '': print countryName, " ", asn
    return [p2pCountryDegreeIntra, p2cCountryDegreeIntra, p2pCountryDegreeInter, p2cCountryDegreeInter]

def generate_metadata_AS_per_country_degree():
    return
def generate_metadata_AS_per_region_degree():
    return

def plot(list,name):
    years = sorted(list.keys())
    sortedCountryNames = sorted(set([c for year in list.keys() for c in list[year].keys()]))
    data = {y:[(c,list[y][c] if c in list[y].keys() else 0) for c in sortedCountryNames] for y in years}
    eachYearData = {y:[data[y][i][1] for i in range(len(sortedCountryNames))] for y in years}

    width = 0.5
    fig,ax=plt.subplots()
    fig.set_size_inches(24.14, 16.14)
    [ax.bar([j+i*(width/len(years)) for j in range(len(sortedCountryNames))],eachYearData[years[i]],width/len(years),label=str(years[i])) for i in range(len(years))]
    ax.set_ylabel('degree')
    ax.set_title(name)
    ax.set_xticks([i for i in range(len(sortedCountryNames))])
    ax.set_xticklabels(sortedCountryNames)
    ax.legend()
    fig.savefig('plots/degree/'+name+".pdf", bbox_inches='tight')

[p2pCountryDegreeIntra, p2cCountryDegreeIntra, p2pCountryDegreeInter, p2cCountryDegreeInter] =  calculateDegreeOfAllAsnsPerCountry ()


plot(p2pCountryDegreeIntra,'p2pCountryDegreeIntra')
plot(p2cCountryDegreeIntra,'p2cCountryDegreeIntra')
plot(p2pCountryDegreeInter,'p2pCountryDegreeInter')
plot(p2cCountryDegreeInter,'p2cCountryDegreeInter')

print "p2pCountryDegreeIntra: ",p2pCountryDegreeIntra
print "-------------------"
print "p2cCountryDegreeIntra: ",p2cCountryDegreeIntra
print "-------------------"
print "p2pCountryDegreeInter",p2pCountryDegreeInter
print "-------------------"
print "p2cCountryDegreeInter",p2cCountryDegreeInter



