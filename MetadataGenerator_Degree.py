import os
import pickle
import matplotlib.pyplot as plt
import operator


SamplingYears = [2006, 2009, 2012, 2015, 2018];
selectedMonths = [6];
DataSets = ['lacnic', 'arin', 'apnic', 'afrinic', 'ripencc'];
countryToAsnMatrix = {}
metaDataPath = 'MetaData/as_relation/as_relation_matrix.networkx'

###plot parameters
plots_width = 10.14
plots_height = 10.14
path_of_plots = 'plots/degree/'


def calculate_country_to_asn_matrix():
    """
    Calculates mapping between "country_name" and "ASN".
    Read ASN MetaData files and then calculate countryToAsnMatrix.
    """
    for regionName in DataSets:
        if os.path.isfile('MetaData/' + regionName):
            ASN = load_obj('MetaData/' + regionName + '_asn')
            for year in ASN.keys():
                for month in ASN[year].keys():
                    for day in ASN[year][month].keys():
                        date = year * 10000 + month * 100 + day
                        if (year not in SamplingYears) or (month not in selectedMonths):
                            continue
                        #if not (date==20090601 or date==20060601): #not (date == 20090601 or date == 20120601):
                        #   continue
                        if date not in countryToAsnMatrix.keys():
                            countryToAsnMatrix[date] = {}
                        for country in ASN[year][month][day].keys():
                            try:
                                if country not in countryToAsnMatrix[date].keys():
                                    countryToAsnMatrix[date][country] = []
                                countryToAsnMatrix[date][country].\
                                    extend(calculate_list_of_asn_in_country(ASN[year][month][day][country]))
                            except Exception as e:
                                pass
                                print e
    return countryToAsnMatrix


def load_obj(file_name):
    """
    load input objects by filename
    """
    with open(file_name, 'rb') as f:
        return pickle.load(f)


def calculate_list_of_asn_in_country(asn_dirty_list):
    """cleansing an ASN Dirty List; for example:
       input: 134214,1,allocated|134206,1,allocated|134187,1,allocated|134171,1,allocated
       output:[134214,134206,134187,134171,134144]
    """
    return [asnData.split(',')[0] for asnData in asn_dirty_list.split('|')]


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


def feed_p2p_data():
    """
    Preparing p2p data (intra and inter country degree) for plots
    """
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
        print " -feed_p2p_data for date: "+ str(date)+" done"

    return p2pInterData, p2pIntraData


def feed_p2c_data():
    """
    Preparing p2c data (intra and inter country degree) for plots
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
        print " -feed_p2c_data for date: "+ str(date)+" done"
    return p2cInterData,p2cIntraData


class AsnData:
    """
    Constructs data and implemets fuctions for calculation of degree
    """
    def __init__(self):
        self.asn_country_mapping = {}
        self.asn_to_asn_relations = set()
        self.asnNumbers = set();

    def feed_country_to_asn_mapping(self,data):
        self.asn_country_mapping = {asnNumber:countryName for countryName in data.keys() if countryName not in ['','TotalNumber'] for asnNumber in data[countryName]}
        self.asnNumbers = set(self.asn_country_mapping.keys())

    def feed_asn_relations(self,relations):
        self.asn_to_asn_relations = set([(source, target, self.asn_country_mapping[source] if source in self.asnNumbers else None, self.asn_country_mapping[target] if target in self.asnNumbers else None) for source in relations for target in relations[source]])

    def _get_intra_country_relations(self):
        result = {c:[x for x in self.asn_to_asn_relations if x[2] == c and x[3] == c] for c in set(self.asn_country_mapping.values())}
        return result

    def _get_inter_country_relations(self):
        result = {c:[x for x in self.asn_to_asn_relations if x[2] == c and x[3]is not None and x[3] != c] for c in set(self.asn_country_mapping.values())}
        return result

    def get_inter_country_degree(self):
        return {singleCountryRelations[0]:len(singleCountryRelations[1]) for singleCountryRelations in self._get_inter_country_relations().items()}

    def get_intra_country_degree(self):
        return {singleCountryRelations[0]:len([relation for relation in singleCountryRelations[1] if relation[0]<relation[1] or (relation[1],relation[0]) not in singleCountryRelations[1]]) for singleCountryRelations in self._get_intra_country_relations().items()}


def each_year_data_country_degrees_func(list_of_splitted_data):
    years = sorted(list_of_splitted_data.keys())
    new_list_sorted_by_degree = {y: sorted(list_of_splitted_data[y], key=operator.itemgetter(1)) for y in years}
    country_names_sorted_by_degree = [new_list_sorted_by_degree[y][i][0] for y in years for i in range(len(new_list_sorted_by_degree[y]))]
    data_country_degrees = {y: [(tupple[0], tupple[1]) for tupple in list_of_splitted_data[y]] for y in years}
    each_year_data_country_degrees = {y: [data_country_degrees[y][i][1] for i in range(len(country_names_sorted_by_degree))] for y in years}
    return each_year_data_country_degrees


def get_country_degree_by_name(list, country_name):
    return [x for x in list if x[0] == country_name][0][1];


def plot_all_figures(number_of_splitted_plots, p2c_inter_data, p2c_intra_data, p2p_inter_data, p2p_intra_data):
    """
    Calls functions to draw plots:
        p2p Country Degree Intra: plot for degree of 'p2p relations' between all IXPs within a country.
        p2c Country Degree Intra: plot for degree of 'provider to customer relations' between all IXPs within a country.
        p2p Country Degree Inter: plot for degree of 'p2p relations' between IXP in a country and all other ones.
        p2c Country Degree Inter: plot for degree of 'provider to customer relations' between IXPs in a country and all other ones.
    """
    split_data_and_do_plot(sorted_by_degree_based_on_most_recent_year(unifying_country_names_for_all_years(p2p_intra_data)), "p2pCountryDegreeIntra_", number_of_splitted_plots)
    split_data_and_do_plot(sorted_by_degree_based_on_most_recent_year(unifying_country_names_for_all_years(p2c_intra_data)), 'p2cCountryDegreeIntra_', number_of_splitted_plots)
    split_data_and_do_plot(sorted_by_degree_based_on_most_recent_year(unifying_country_names_for_all_years(p2p_inter_data)), 'p2pCountryDegreeInter_', number_of_splitted_plots)
    split_data_and_do_plot(sorted_by_degree_based_on_most_recent_year(unifying_country_names_for_all_years(p2c_inter_data)), 'p2cCountryDegreeInter_', number_of_splitted_plots)


def unifying_country_names_for_all_years(input_list):
    years = input_list.keys()
    country_names = set([item[0] for y in years for item in input_list[y].items()])
    data_country_degrees = {y: [(c, input_list[y][c] if c in input_list[y].keys() else 0) for c in country_names] for y in years}
    return data_country_degrees


def sorted_by_degree_based_on_most_recent_year(input_dic):
    """
    :param input_dic: {year: [(countryname,degree)]}
    :return: sorted list by degrees based on last year data
    """
    years = input_dic.keys()
    max_year = max(years)
    max_year_data = input_dic[max_year];
    max_year_sorted_data_based_on_degree = sorted(max_year_data, key=lambda x:x[1])
    max_year_countries = [c[0] for c in max_year_sorted_data_based_on_degree]

    sorted_data = {y: [(c, get_country_degree_by_name(input_dic[y], c)) for c in max_year_countries] for y in years if y != max_year}

    sorted_data[max_year] = max_year_sorted_data_based_on_degree
    return sorted_data


def split_data_and_do_plot(sorted_list_by_degree, base_name_of_plot, number_of_splitted_plots=1):
    """
    Feed splitted data to plot function.
    :param sorted_list_by_degree:
    :param base_name_of_plot: base name of plots
    :param number_of_splitted_plots: If you want sorted_list_by_degree be plotted in number_of_splitted_plots figure set this parameter
    """
    splitted_list = calculate_list_of_splitted_data(sorted_list_by_degree, number_of_splitted_plots)
    for i in range(len(splitted_list)):
        single_chunk = splitted_list[i];
        plot(single_chunk, base_name_of_plot + str(i), plots_width, plots_height, path_of_plots, ylabel='degree')


def calculate_list_of_splitted_data(sorted_list, number_of_splitted_plots):
    """
    Splits sorted_list dictionary into number_of_splitted_plots number of lists
    :param sorted_list: {year:[(countryName,degree)]
    :param number_of_splitted_plots:
    :return: [{year:[(countryName,degree)]}]
    """
    years = sorted_list.keys();
    chunk_size = len(sorted_list[years[0]])/number_of_splitted_plots - 1
    data = {y:split_list(sorted_list[y], chunk_size) for y in years}
    chunk_count = len(data[years[0]])
    result = [{y:data[y][i] for y in years} for i in range(chunk_count)]
    return result;


def split_list(list_to_be_splitted, chunk_size):
    """
    Splits input list to chunk_size number of lists.
    :param list_to_be_splitted:
    :param chunk_size:
    :return:
    """
    return [list_to_be_splitted[offs:offs + chunk_size] for offs in range(0, len(list_to_be_splitted), chunk_size)]


def plot(list_of_splitted_data, name, size_inch_w, size_inch_h, save_path, ylabel): #{year:[(countryName,degree)]}
    """
    :param list_of_splitted_data: data to plot
    :param name: Name of plot
    :param inch: size of plot
    :return: Save plot files in PDF format to "plots/degree/"
    """

    years = sorted(list_of_splitted_data.keys())
    width = 0.5
    fig,ax=plt.subplots()
    fig.set_size_inches(size_inch_w, size_inch_h)

    [ax.bar([j+i*(width/len(years)) for j in range(len(list_of_splitted_data[years[i]]))],[x[1] for x in list_of_splitted_data[years[i]]],width/len(years),label=str(years[i])) for i in range(len(years))]
    ax.set_ylabel(ylabel)
    sample_year = years[i]
    country_names = [x[0] for x in list_of_splitted_data[sample_year]]
    ax.set_title(name)
    ax.set_xticks([i for i in range(len(list_of_splitted_data[sample_year]))])
    ax.set_xticklabels(country_names)
    ax.legend()
    #fig.savefig(save_path+name+".pdf", bbox_inches='tight')

    fig.savefig(save_path+name+".png", bbox_inches='tight')
    print "plot "+name+" has been save in "+save_path


def main():
    global dates, p2p, p2c, country_asn_mapping_accross_years
    dates = calculate_country_to_asn_matrix().keys()
    country_asn_mapping_accross_years = calculate_country_to_asn_matrix()
    print "Calculating country to asn matrix done"

    (p2p, p2c) = read_metadata_as_relationship(metaDataPath)
    print "Reading metadata from " + metaDataPath + " done"

    print "Start Processing (Feeding data and Caclulating degrees)..."
    p2c_inter_data, p2c_intra_data = feed_p2c_data()
    p2p_inter_data, p2p_intra_data = feed_p2p_data()
    print "Processing done."

    print("Start plotting...")
    plot_all_figures(8, p2c_inter_data, p2c_intra_data, p2p_inter_data, p2p_intra_data)
    print ("Done!")


main()