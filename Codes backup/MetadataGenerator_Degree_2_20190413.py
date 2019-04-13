import os
import pickle
import matplotlib.pyplot as plt
import operator
import logging

SamplingYears = [2006, 2009, 2012, 2015, 2018];
selectedMonths = [6];
DataSets = ['lacnic', 'arin', 'apnic', 'afrinic', 'ripencc'];
countryToAsnMatrix = {}
#logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


def load_obj(FileName):
    """load input by filename"""
    with open(FileName, 'rb') as f:
        return pickle.load(f)

def read_metadata_as_relationship(directory):
    """Read MetaData files placed in a directory
    input:
        complete path to directory witch contains matrixes
    outputs:
        p2pM: p2p Matrix
        p2cM: Provider to customer Matrix
    """
    [p2pM, p2cM] = load_obj(directory)
    return [p2pM, p2cM]

def calculateListOfAsnInCountry (asnDirtyList):
    """cleansing an ASN Dirty List; for example:
       input: 134214,1,allocated|134206,1,allocated|134187,1,allocated|134171,1,allocated
       output:[134214,134206,134187,134171,134144]
    """
    return [asnData.split(',')[0] for asnData in asnDirtyList.split('|')]


def calculate_country_to_asn_matrix():
    """
    Calculates mapping  between "country_name" and "ASN".
    Read ASN MetaData files and then calculate countryToAsnMatrix.
    """
    for regionName in DataSets:
        if os.path.isfile('MetaData/' + regionName):
            ASN = load_obj('MetaData/' + regionName + '_asn')
            for year in ASN.keys():
                for month in ASN[year].keys():
                    for day in ASN[year][month].keys():
                        date = year * 10000 + month * 100 + day #date = 20090601 #for test
                        if not (date==20090601 or date==20060601): #not (date == 20090601 or date == 20120601):
                            continue

                        if date not in countryToAsnMatrix.keys():
                            countryToAsnMatrix[date] = {}
                        for country in ASN[year][month][day].keys():
                            try:
                                if country not in countryToAsnMatrix[date].keys():
                                    countryToAsnMatrix[date][country] = []
                                countryToAsnMatrix[date][country].extend(calculateListOfAsnInCountry(ASN[year][month][day][country]))
                            except Exception as e:
                                pass
                                #print date
                                print e
    # print len(countryToAsnMatrix.keys())
    return countryToAsnMatrix


class AsnData:
    """
    Constructs data and implemets fuctions for calculatation of degree
    """
    def __init__(self):
        self.asn_country_mapping = {}
        self.asn_to_asn_relations = set()
        self.asnNumbers = set();

    def feed_country_to_asn_mapping(self,data):
        self.asn_country_mapping = {asnNumber:countryName for countryName in data.keys() if countryName not in ['','TotalNumber'] for asnNumber in data[countryName]}
        self.asnNumbers = set(self.asn_country_mapping.keys())

    def feed_asn_relations(self,relations):
        self.asn_to_asn_relations = set([(source,target,self.asn_country_mapping[source] if source in self.asnNumbers else None,self.asn_country_mapping[target] if target in self.asnNumbers else None) for source in relations for target in relations[source]])

    def _get_intra_country_relations(self):
        result = {c:[x for x in self.asn_to_asn_relations if x[2]==c and x[3]==c] for c in set(self.asn_country_mapping.values())}
        return result

    def _get_inter_country_relations(self):
        result = {c:[x for x in self.asn_to_asn_relations if x[2]==c and x[3]is not None and x[3] != c] for c in set(self.asn_country_mapping.values())}
        return result

    def get_inter_country_degree(self):
        return {singleCountryRelations[0]:len(singleCountryRelations[1]) for singleCountryRelations in self._get_inter_country_relations().items()}

    def get_intra_country_degree(self):
        return {singleCountryRelations[0]:len([relation for relation in singleCountryRelations[1] if relation[0]<relation[1] or (relation[1],relation[0]) not in singleCountryRelations[1]]) for singleCountryRelations in self._get_intra_country_relations().items()}


def each_year_data_country_degrees_func(list_of_splitted_data):
    years = sorted(list_of_splitted_data.keys())

    ###print "listOfSplittedData[y]: "+str(list_of_splitted_data[20090601])
    new_list_sorted_by_degree = {y: sorted(list_of_splitted_data[y], key=operator.itemgetter(1)) for y in years}
    country_names_sorted_by_degree = [new_list_sorted_by_degree[y][i][0] for y in years for i in range(len(new_list_sorted_by_degree[y]))]
    data_country_degrees = {y: [(tupple[0], tupple[1]) for tupple in list_of_splitted_data[y]] for y in years}

    print "data_country_degrees: "+str(data_country_degrees)

    each_year_data_country_degrees = {y: [data_country_degrees[y][i][1] for i in range(len(country_names_sorted_by_degree))] for y in years}
    return each_year_data_country_degrees


def unify_country_names_for_all_years(input_list):
    print "input_list: "+str(input_list)
    years = input_list.keys()
    print(input_list)
    country_names = set([item[0] for y in years for item in input_list[y].items()])
    data_country_degrees = {y: [(c, input_list[y][c] if c in input_list[y].keys() else 0) for c in country_names] for y in years}
    print "data_country_degrees: "+str(data_country_degrees)
    return data_country_degrees


def sorted_by_degree_based_on_most_recent_year(inputlist):
    years = inputlist.keys()
    max_year = max(years)
    max_year_data = inputlist[max_year];
    max_year_sorted_data_based_on_degree = sorted(max_year_data, key=lambda x:x[1])
    max_year_countries = [c[0] for c in max_year_sorted_data_based_on_degree]
    print "max_year_countries: "+str(max_year_countries)

    sorted_data = {y: [(c, inputlist[y][1]) for c in max_year_countries] for y in years if y!=max_year}  #####check this part####
    sorted_data[max_year] = max_year_sorted_data_based_on_degree
    return sorted_data


def plot(list_of_splitted_data, name): #{year:[(countryName,degree)]}
    #print listOfSplittedData
    years = sorted(list_of_splitted_data.keys())
    ##each_year_data_country_degrees = each_year_data_country_degrees_func(list_of_splitted_data) ##commented by Hesam

    width = 0.5
    fig,ax=plt.subplots()
    fig.set_size_inches(25.14, 25.14)

    [ax.bar([j+i*(width/len(years)) for j in range(len(list_of_splitted_data[years[i]]))],[x[1] for x in list_of_splitted_data[years[i]]],width/len(years),label=str(years[i])) for i in range(len(years))]
    ax.set_ylabel('degree')
    sample_year = years[i]
    country_names = [x[0] for x in list_of_splitted_data[sample_year]]
    ax.set_title(name)
    ax.set_xticks([i for i in range(len(list_of_splitted_data[sample_year]))])
    ax.set_xticklabels(country_names)
    ax.legend()
    fig.savefig('plots/degree/'+name+".pdf", bbox_inches='tight')


def feed_p2p_data():
    # Feed P2PData
    p2pIntraData = {}
    p2pInterData = {}
    for date in dates:
        p2pForDate = p2p[date]
        country_asn_mapping = country_asn_mapping_accross_years[date]
        asnGraph = AsnData()
        asnGraph.feed_country_to_asn_mapping(country_asn_mapping)
        asnGraph.feed_asn_relations(p2pForDate)

        p2pIntraData[date] = asnGraph.get_intra_country_degree()
        # print "p2pInterData: "+str(p2pInterData)
        p2pInterData[date] = asnGraph.get_inter_country_degree()
        print "feed_p2p_data for date: "+ str(date)

    return p2pInterData, p2pIntraData


def feed_p2c_data():
    """
    Preparing p2c data for plot
    """
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
        print(date)
    return p2cInterData,p2cIntraData


def split_data_and_do_plot (sorted_list_by_degree, name_of_plot, number_of_splitted_plots):
    """"""

    print "sorted_list_by_degree"+str(sorted_list_by_degree)
    print "listOfSplittedData(sortedListByDegree,NumberofSplittedPlots):"+ str(calculate_list_of_splitted_data(sorted_list_by_degree, number_of_splitted_plots))
    splitted_list=calculate_list_of_splitted_data(sorted_list_by_degree, number_of_splitted_plots)
    print "splitted_list: "+str(splitted_list)
    for i in range(len(splitted_list)):
        single_chunk = splitted_list[i];
        print "listOfSplittedData: "+str(single_chunk)
        plot(single_chunk, name_of_plot + str(i))



def SplitList(list, chunk_size):
    return [list[offs:offs+chunk_size] for offs in range(0, len(list), chunk_size)]

def calculate_list_of_splitted_data(sorted_list, number_of_splitted_plots):
    """
    in:{year:[(countryName,degree)]
    out:[{year:[(countryName,degree)]}]
    """
    years = sorted_list.keys();
    chunk_size = len(sorted_list[years[0]])/number_of_splitted_plots - 1
    data = {y:SplitList(sorted_list[y],chunk_size) for y in years}
    chunk_count = len(data[years[0]])
    result = [{y:data[y][i] for y in years} for i in range(chunk_count)]
    return result;
    # countryNames = [c[0] for c in sorted_list[max(sorted_list.keys())]]
    # countryChunks = SplitList(countryNames,len(countryNames)/number_of_splitted_plots)
    # [{y:[sorted_list[y][c] for c in countryChunks[i]] for y in years} for i in range(len(countryChunks))]
    #
    # years = sorted(sorted_list.keys())
    # return {splitedCountLoop:{y: [sorted_list[y][i] for i in range(len(sorted_list[y])/number_of_splitted_plots*splitedCountLoop, (len(sorted_list[y])/number_of_splitted_plots)*(splitedCountLoop+1))]} for y in years for splitedCountLoop in range(number_of_splitted_plots) }


def plot_all_figures(number_of_splitted_plots):
    print("Start plotting")
    p2c_inter_data, p2c_intra_data = feed_p2c_data()
    p2p_inter_data, p2p_intra_data = feed_p2p_data()
    print "----------------------------------"
    print(p2p_inter_data)
    print "----------------------------------"
    #print "sorted_list_by_degree(p2p_intra_data): "+str(sorted_list_by_degree(p2p_intra_data))
    split_data_and_do_plot(sorted_by_degree_based_on_most_recent_year(unify_country_names_for_all_years(p2p_intra_data)), "p2pCountryDegreeIntra_", number_of_splitted_plots)
    split_data_and_do_plot(sorted_by_degree_based_on_most_recent_year(unify_country_names_for_all_years(p2c_intra_data)), 'p2cCountryDegreeIntra_', number_of_splitted_plots)
    split_data_and_do_plot(sorted_by_degree_based_on_most_recent_year(unify_country_names_for_all_years(p2p_inter_data)), 'p2pCountryDegreeInter_', number_of_splitted_plots)
    split_data_and_do_plot(sorted_by_degree_based_on_most_recent_year(unify_country_names_for_all_years(p2c_inter_data)), 'p2cCountryDegreeInter_', number_of_splitted_plots)


def main():
    global dates, p2p, p2c, country_asn_mapping_accross_years
    dates = calculate_country_to_asn_matrix().keys()

    #logging


    (p2p, p2c) = read_metadata_as_relationship('MetaData/as_relation/as_relation_matrix.networkx')
    country_asn_mapping_accross_years = calculate_country_to_asn_matrix()
    print('reading done')
    logging.info("Reading Done!")
    plot_all_figures(8)


main()


