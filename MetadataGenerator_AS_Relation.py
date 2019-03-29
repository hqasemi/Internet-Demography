import urllib2, pickle, os, StringIO, gzip, bz2
import networkx as nx

# SamplingYears = range(1998,2020);
SamplingYears = [2006, 2009, 2012, 2015, 2018];
selectedMonths = [6];
DataSets = ['lacnic', 'arin', 'apnic', 'afrinic', 'ripencc'];

def setURLAddress(date):
    if date < 20151201:
        return 'http://data.caida.org/datasets/as-relationships/serial-1/'+str(date)+'.as-rel.txt.bz2'
    return 'http://data.caida.org/datasets/as-relationships/serial-2/'+str(date)+'.as-rel2.txt.bz2'
def FetchURL(urlToReadFrom):
    try:
        response = urllib2.urlopen(urlToReadFrom)
    except urllib2.HTTPError, e:
        print '\033[0;31m', 'Something went wrong, we cannot download the dataset. URL: ', urlToReadFrom, ' Error number: ', e.code, '\033[0;30m '
        return None
    if urlToReadFrom.find('.gz') >= 0:
        compressedFile = StringIO.StringIO()
        compressedFile.write(response.read())
        # Set the file's current position to the beginning of the file so that gzip.GzipFile can read its contents from the top.
        compressedFile.seek(0)
        decompressedFile = gzip.GzipFile(fileobj=compressedFile, mode='rb')
        html = decompressedFile.read()
    elif urlToReadFrom.find('.bz2') >= 0:
        compressedFile = StringIO.StringIO()
        compressedFile.write(response.read())
        # Set the file's current position to the beginning of the file so that gzip.GzipFile can read its contents from the top.
        compressedFile.seek(0)
        # Extract the training data
        html = bz2.decompress(compressedFile.read())
    else:
        html = response.read()
    return html
def save_obj(FileName, obj):
    with open(FileName, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
def load_obj(FileName):
    with open(FileName, 'rb') as f:
        return pickle.load(f)
def findDateOfFileName(FileName):
    if FileName.find('.gz') >= 0 or FileName.find('.bz2') >= 0:
        Date = [int(s) for s in [i for i in FileName.split('-') if (i.find('.') >= 0)][0].split('.') if s.isdigit()][0]
    else:
        Date = [int(s) for s in FileName.split('-') if s.isdigit()][0]
    return Date
def download_DataSets():
    for year in SamplingYears:
        for month in selectedMonths:
            Date = year*10000+month*100+01;
            if not os.path.isfile('AS_relateion_datasets/'+str(Date)+'.as-rel.txt'):
                urlAddress = setURLAddress(Date);
                html = FetchURL(urlAddress);
                if not html==None:
                    save_obj('AS_relateion_datasets/' + str(Date)+'.as-rel.txt', html);
def generate_metadata():
    [p2p, p2c, p2pM, p2cM] = [{}, {}, {}, {}]
    for year in SamplingYears:
        for month in selectedMonths:
            Date = year*10000+month*100+01;
            # if not os.path.isfile('MetaData/as_relation/'+str(Date)):
            if os.path.isfile('AS_relateion_datasets/'+str(Date)+'.as-rel.txt'):
                [p2p[Date], p2c[Date]] = ReadDataFromDataSet(Date);
                save_obj('MetaData/as_relation/'+str(Date),[p2p[Date],p2c[Date]]);
                [p2pM[Date], p2cM[Date]] = ReadDataFromDataSet_AS_Rel_Matrix(Date);
                save_obj('MetaData/as_relation/matrix_' + str(Date), [p2pM[Date], p2cM[Date]]);
def ReadDataFromDataSet(Date):
    html = load_obj('AS_relateion_datasets/'+str(Date)+'.as-rel.txt')

    [p2p, p2c] = [nx.Graph(), nx.Graph()];

    # Extract the data from dataset file and put it in the dictionaries
    for line in html.split('\n'):
        # a dataset may have COMMENT line starting with #
        if line.find('#')<0 and not line=='':
            eachEntry = line.split('|')
            if eachEntry[2] == '0':
                p2p.add_edge(eachEntry[0], eachEntry[1], weight=1);
            elif eachEntry[2] == '-1':
                p2c.add_edge(eachEntry[0], eachEntry[1], weight=1);

    return [p2p, p2c];
def ReadDataFromDataSet_AS_Rel_Matrix(Date):
    html = load_obj('AS_relateion_datasets/'+str(Date)+'.as-rel.txt')
    # p2p[i] is a list of all ASNs that i has a connection to them as peer
    # p2c[i] is a list of all ASNs that i has a connection to them as provider to customer
    [p2p, p2c] = [{}, {}];
    # Extract the data from dataset file and put it in the dictionaries
    for line in html.split('\n'):
        # a dataset may have COMMENT line starting with #
        if line.find('#') < 0 and not line == '':
            eachEntry = line.split('|')
            if eachEntry[2] == '0':
                if eachEntry[0] in p2p.keys():
                    p2p[eachEntry[0]].append(eachEntry[1]);
                else:
                    p2p[eachEntry[0]] = [eachEntry[0]];
                if eachEntry[1] in p2p.keys():
                    p2p[eachEntry[1]].append(eachEntry[0]);
                else:
                    p2p[eachEntry[1]] = [eachEntry[0]];
            elif eachEntry[2] == '-1':
                if eachEntry[0] in p2c.keys():
                    p2c[eachEntry[0]].append(eachEntry[1]);
                else:
                    p2c[eachEntry[0]] = [eachEntry[0]];
                # if eachEntry[1] in p2c.keys():
                #     p2c[eachEntry[1]].append(eachEntry[0]);
                # else:
                #     p2c[eachEntry[1]] = [eachEntry[0]];

    return [p2p, p2c];
def FinalProcess():
    [p2p, p2c, p2pM, p2cM] = [{}, {}, {}, {}]
    for year in SamplingYears:
        # for month in range(1, 13):
        for month in selectedMonths:
            Date = year * 10000 + month * 100 + 01;
            if os.path.isfile('MetaData/as_relation/' + str(Date)):
                print Date
                [p2p[Date], p2c[Date]] = load_obj('MetaData/as_relation/' + str(Date));
                [p2pM[Date], p2cM[Date]] = load_obj('MetaData/as_relation/matrix_' + str(Date));
    save_obj('MetaData/as_relation/as_relation_graph.networkx', [p2p,p2c]);
    save_obj('MetaData/as_relation/as_relation_matrix.networkx', [p2pM, p2cM]);
    # x = input('File created. Do you want to delete temporary metadata? (y/n)')
    # if x == 'y':
    #     for year in SamplingYears:
    #         for month in range(1, 13):
    #             Date = year * 10000 + month * 100 + 01;
    #             if os.path.isfile('MetaData/as_relation/' + str(Date)):
    #                 os.remove('MetaData/as_relation/' + str(Date));
def main():
    download_DataSets();
    generate_metadata();
    FinalProcess();

# main()
#[p2pM, p2cM] = load_obj('MetaData/as_relation/as_relation_matrix.networkx')
#print p2cM.keys()
#print len(p2cM[20180601]), p2cM[20180601].keys()
#print p2cM[20180601]['35236']


#g = nx.Graph()
#d = p2cM[20180601]
#print d


# g.add_nodes_from(d.keys())
#
# for k, v in d.items():
#     g.add_edges_from(([(k, t) for t in v]))
#
#R#print g.edges()
# print g.degree()
x = load_obj('MetaData/lacnic_asn')

print [asnData.split(',')[0] for asnData in x[2015][06][01]['BR'].split('|')]