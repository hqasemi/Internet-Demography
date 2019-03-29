import os
import pickle
import matplotlib.pyplot as plt

SamplingYears = [2006, 2009, 2012, 2015, 2018];
selectedMonths = [6];
DataSets = ['lacnic', 'arin', 'apnic', 'afrinic', 'ripencc'];
countryToAsnMatrix = {}
def load_obj(FileName):
    with open(FileName, 'rb') as f:
        return pickle.load(f)

def read_metadata_as_relationship():
    [p2pM, p2cM] = load_obj('MetaData/as_relation/as_relation_matrix.networkx')
    return [p2pM, p2cM]

def calculateListOfAsnInCountry (asnDirtyList):
    #cleansing for example:
    #   input: 134214,1,allocated|134206,1,allocated|134187,1,allocated|134171,1,allocated
    #   output:[134214,134206,134187,134171,134144]
    return [asnData.split(',')[0] for asnData in asnDirtyList.split('|')]

def calculate_country_to_asn_matrix():
    #read metadata asn and calculate country to asn matrix
    for regionName in DataSets:
        if os.path.isfile('MetaData/' + regionName):
            ASN = load_obj('MetaData/' + regionName + '_asn')
            for year in ASN.keys():
                for month in ASN[year].keys():
                    for day in ASN[year][month].keys():
                        date = year * 10000 + month * 100 + day
                        if(date not in countryToAsnMatrix.keys()):
                            countryToAsnMatrix[date] = {}
                        # print str(year)+'/'+str(month)+"/"+str(day)
                        for country in ASN[year][month][day].keys():
                            # print country
                            # if  country=="TotalNumber":
                            # print "^^^^^^^^^^^^"
                            # print country
                            # print ASN[year][month][day][country]

                            try:
                                if(country not in countryToAsnMatrix[date].keys()):
                                    countryToAsnMatrix[date][country] = []
                                countryToAsnMatrix[date][country].extend(calculateListOfAsnInCountry(ASN[year][month][day][country]))
                            except Exception as e:
                                pass
                                #print date
                                print e
    # print len(countryToAsnMatrix.keys())
    return countryToAsnMatrix

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

class AsnData:
    def __init__(self):
        self.asn_country_mapping = {}
        self.asn_to_asn_relations = set()
    def feed_country_to_asn_mapping(self,data):
        self.asn_country_mapping = {asnNumber:countryName for countryName in data.keys() for asnNumber in data[countryName]}

    def feed_asn_relations(self,relations):
        self.asn_to_asn_relations = set([(source,target,self.asn_country_mapping[source] if source in self.asn_country_mapping.keys() else None,self.asn_country_mapping[target] if target in self.asn_country_mapping.keys() else None) for source in relations for target in source])

    def _get_intra_country_relations(self):
        result = {c:[x for x in self.asn_to_asn_relations if x[2]==c and x[3]==c] for c in set(self.asn_country_mapping.values())}

        # result = {c: [] for c in set(self.asn_country_mapping.values())}
        # [result[self.asn_country_mapping[x[0]]].append(x) for x in self.asn_to_asn_relations if x[0] in self.asn_country_mapping.keys() and x[1] in self.asn_country_mapping.keys() and self.asn_country_mapping[x[0]] == self.asn_country_mapping[x[1]]]
        return result

    def _get_inter_country_relations(self):
        # result = {c:[x for x in self.asn_to_asn_relations if x[0] in self.asn_country_mapping.keys() and x[1] in self.asn_country_mapping.keys() and self.asn_country_mapping[x[0]]==c and self.asn_country_mapping[x[1]]!=c] for c in set(self.asn_country_mapping.values())}
        result = {c:[] for c in set(self.asn_country_mapping.values())}
        i=0;
        print (len(result))
        for c in set(self.asn_country_mapping.values()):
            i=i+1
            print(i)
            r=[x for x in self.asn_to_asn_relations if x[0] in self.asn_country_mapping.keys() and x[1] in self.asn_country_mapping.keys() and self.asn_country_mapping[x[0]] == c and self.asn_country_mapping[x[1]] != c]
            print(i)
            result[c]=r
        # result = {c:[] for c in set(self.asn_country_mapping.values())}
        # [result[self.asn_country_mapping[x[0]]].append(x) for x in self.asn_to_asn_relations if x[0] in self.asn_country_mapping.keys() and x[1] in self.asn_country_mapping.keys() and self.asn_country_mapping[x[0]] != self.asn_country_mapping[x[1]]]
        return result

    def get_inter_country_degree(self):
        return {singleCountryRelations[0]:len(singleCountryRelations[1]) for singleCountryRelations in self._get_inter_country_relations().items()}

    def get_intra_country_degree(self):
        return {singleCountryRelations[0]:len([relation for relation in singleCountryRelations[1] if relation[0]<relation[1] or (relation[1],relation[0]) not in singleCountryRelations[1]]) for singleCountryRelations in self._get_intra_country_relations().items()}

dates=calculate_country_to_asn_matrix().keys()
(p2p,p2c) = read_metadata_as_relationship()
country_asn_mapping_accross_years = calculate_country_to_asn_matrix()

p2pIntraData = {}
p2pInterData = {}
for date in dates:
    if(date==20090601):
        continue
    p2pForDate = p2p[date]
    country_asn_mapping = country_asn_mapping_accross_years[date]
    asnGraph = AsnData()
    asnGraph.feed_country_to_asn_mapping(country_asn_mapping)
    asnGraph.feed_asn_relations(p2pForDate)
    print(date)
    p2pIntraData[date]=asnGraph.get_intra_country_degree()
    print(1)
    p2pInterData[date]=asnGraph.get_inter_country_degree()
    print(2)

p2cIntraData = {}
p2cInterData = {}
for date in dates:
    p2cForDate = p2c[date]
    country_asn_mapping = country_asn_mapping_accross_years[date]
    asnGraph = AsnData()
    asnGraph.feed_country_to_asn_mapping(country_asn_mapping)
    asnGraph.feed_asn_relations(p2cForDate)

    p2cInterData[date] = asnGraph.get_inter_country_degree()
    p2cIntraData[date] = asnGraph.get_intra_country_degree()

plot(p2pIntraData,'p2pCountryDegreeIntra')
plot(p2cIntraData,'p2cCountryDegreeIntra')
plot(p2pInterData,'p2pCountryDegreeInter')
plot(p2cInterData,'p2cCountryDegreeInter')