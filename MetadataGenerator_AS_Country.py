import urllib2, pickle, os, StringIO, gzip, bz2

# DataSets = ['ripencc']#, 'arin', 'afrinic', 'apnic']
DataSets = ['lacnic', 'ripencc', 'arin', 'afrinic', 'apnic']
# SamplingYears = range(2006, 2019, 3)
# SamplingYears = range(2001, 2019)
SamplingYears  = [2006, 2009, 2012, 2015, 2018];

#Zero mean ignore it, otherwise, only this mmdd will be considered
DateToCheck = 601

def setURLAddress(DataSetName, YearOfSampling):
    if DataSetName == 'arin':
        if YearOfSampling <= 2016:
            urlAddress = 'https://ftp.ripe.net/pub/stats/' + DataSetName + '/archive/' + str(YearOfSampling) + '/'
        else:
            urlAddress = 'https://ftp.ripe.net/pub/stats/' + DataSetName + '/'
    elif DataSetName == 'lacnic':
        if YearOfSampling == 2003:
            urlAddress = 'https://ftp.ripe.net/pub/stats/' + DataSetName + '/archive/' + str(YearOfSampling) + '/'
        else:
            urlAddress = 'https://ftp.ripe.net/pub/stats/' + DataSetName + '/'
    else:
        urlAddress = 'https://ftp.ripe.net/pub/stats/' + DataSetName + '/' + str(YearOfSampling) + '/'
    return urlAddress

def checkTheFilePlace(Date, YearOfSampling):
    Year = divmod(Date, 10000)[0]
    if YearOfSampling==Year:
        return True
    else:
        return False
def FinalProcess():
    [IPv4, IPv6, ASN] = [{} for i in range(0, 3)]
    for DataSetName in DataSets:
        for YearOfSampling in SamplingYears:
            if os.path.isfile('MetaData/temp/' + DataSetName + str(YearOfSampling)):
                [IPv4[YearOfSampling], IPv6[YearOfSampling], ASN[YearOfSampling]] = load_obj('MetaData/temp/' + DataSetName + str(YearOfSampling))
        save_obj('MetaData/' + DataSetName, [IPv4, IPv6, ASN])
        for YearOfSampling in SamplingYears:
            if os.path.isfile('MetaData/temp/' + DataSetName + str(YearOfSampling)):
                os.remove('MetaData/temp/' + DataSetName + str(YearOfSampling))
def FetchURL(urlToReadFrom):
    try:
        response = urllib2.urlopen(urlToReadFrom)
    except urllib2.HTTPError, e:
        print '\033[0;31m', 'Something went wrong, we cannot download the dataset. URL: ', urlToReadFrom, ' Error number: ', e.code, '\033[0;30m '
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
def download_ListOf_DatasetsFiles():
    for DataSetName in DataSets:
        oldURLAddress = ''
        for year in SamplingYears:
            # if not os.path.isfile('Dataset/' + DataSetName + '_list_' + str(year)):
            try:
                urlAddress = setURLAddress(DataSetName, year)
                if not oldURLAddress == urlAddress:
                    print 'Crawling ', urlAddress, '(', year, ')'
                    response = urllib2.urlopen(urlAddress)
                    html = response.read()
                    print DataSetName, year, 'List of dataset files are downloaded'
                listOf_DatasetFiles = removeUselessEntries(html, year)
                save_obj('Dataset/' + DataSetName + '_list_' + str(year), listOf_DatasetFiles)
                oldURLAddress = urlAddress;
                print DataSetName, year, 'list of dataset files is saved'
            # some years are not available in each directory (e.g., apnic is from 2001 while afric is from 2005)
            except urllib2.HTTPError, e:
                save_obj('Dataset/' + DataSetName + '_list_' + str(year), [])
                print '\033[0;32m', 'The url does not exist, i.e., data set does not exist. Error number: ', e.code, '\033[0;30m '
def save_obj(FileName, obj):
    with open(FileName, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
def load_obj(FileName):
    with open(FileName, 'rb') as f:
        return pickle.load(f)
def precomputation():
    DataSets = ['lacnic', 'ripencc', 'arin', 'afrinic', 'apnic']
    for DataSetName in DataSets:
        if os.path.isfile('MetaData/' + DataSetName + '_ipv4'):
            IPv4 = load_obj('MetaData/' + DataSetName + '_ipv4')
            IPv6 = load_obj('MetaData/' + DataSetName + '_ipv6')
            ASN = load_obj('MetaData/' + DataSetName + '_asn')
            save_obj('MetaData/' + DataSetName, [IPv4, IPv6, ASN])
            os.remove('MetaData/' + DataSetName + '_ipv4')
            os.remove('MetaData/' + DataSetName + '_ipv6')
            os.remove('MetaData/' + DataSetName + '_asn')
def findDateOfFileName(FileName):
    if FileName.find('.gz') >= 0 or FileName.find('.bz2') >= 0:
        Date = [int(s) for s in [i for i in FileName.split('-') if (i.find('.') >= 0)][0].split('.') if s.isdigit()][0]
    else:
        Date = [int(s) for s in FileName.split('-') if s.isdigit()][0]
    return Date
def removeUselessEntries(html,year):
    seenDate = {}
    result = []
    tmpIndx = 0
    # find the name of all existing datasets
    allFiles = html.split('"')
    # Read dataset file content
    for FileName in allFiles:
        if 'delegated-' in FileName in FileName and not '<' in FileName and '20' in FileName and not '.md5' in FileName and not '.asc' in FileName and not '.old' in FileName and not '.bak' in FileName and not 'key' in FileName:
            Date = findDateOfFileName(FileName)
            # Some datafiles are copied in a wrong directory, by the following 'if' we do not consider them
            if checkTheFilePlace(Date, year):
                if (Date - year * 10000) == DateToCheck or DateToCheck==0:
                    if not Date in seenDate.keys():
                        result.append(FileName);
                        seenDate[Date] = tmpIndx;
                        tmpIndx += 1;
                    #some entries are extended and the old version should be replaced by the extended version
                    elif 'extended' in FileName.split('-'):
                        result[seenDate[Date]] = FileName;
    return result;
def download_DataSets():
    for DataSetName in DataSets:
        for year in SamplingYears:
            listOf_dataFiles = load_obj('Dataset/' + DataSetName + '_list_' + str(year))
            urlAddress = setURLAddress(DataSetName, year)
            for fileName in listOf_dataFiles:
                Date = findDateOfFileName(fileName);
                if not os.path.isfile('DataSet/' + DataSetName + str(Date)):
                    html = FetchURL(urlAddress+fileName);
                    save_obj('DataSet/' + DataSetName + str(Date), html);
def generate_metadata():
    for DataSetName in DataSets:
        for year in SamplingYears:
            print 'generating metadata for ',DataSetName, year
            # if not os.path.isfile('MetaData/temp/' + DataSetName + str(year)):
            [IPv4, IPv6, ASN] = [{} for i in range(0, 3)];
            listOf_dataFiles = load_obj('Dataset/' + DataSetName + '_list_' + str(year))
            for fileName in listOf_dataFiles:
                ReadDataFromDataSet(DataSetName, findDateOfFileName(fileName), IPv4, IPv6, ASN)
            save_obj('MetaData/temp/' + DataSetName + str(year), [IPv4, IPv6, ASN])
def ReadDataFromDataSet(DataSetName, date, IPv4, IPv6, ASN):
    html = load_obj('DataSet/' + DataSetName + str(date))
    [day, month] = [divmod(date, 100)[1], int(divmod(date, 10000)[1] / 100)];
    if not month in IPv4.keys():
        [IPv4[month],IPv6[month], ASN[month]] = [{} for i in range(0,3)];
    [IPv4[month][day], IPv6[month][day], ASN[month][day]] = [{} for i in range(0, 3)];
    # Extract the data from dataset file and put it in the dictionaries
    for line in html.split('\n'):
        # a dataset may have BLANK line or COMMENT line starting with #
        if (not line == '') and (line.find('#')<0):
            eachEntry = line.split('|')
            if eachEntry[1] == '*':
                # each line is as following: DatasetName|*|Type(ipv4 or ipv6 or asn)|*|totalNumberInTheDataset|...
                if eachEntry[2] == 'ipv4':
                    IPv4[month][day]['TotalNumber'] = eachEntry[4]
                elif eachEntry[2] == 'ipv6':
                    IPv6[month][day]['TotalNumber'] = eachEntry[4]
                elif eachEntry[2] == 'asn':
                    ASN[month][day]['TotalNumber'] = eachEntry[4]
            elif eachEntry[0] == DataSetName:
                # each line is as following: DatasetName|CountryCode|Type(ipv4 or ipv6 or asn)|Value of ip or asn|number(IPs or ASNs)|....
                if eachEntry[2] == 'ipv4':
                    # we insert lines as following: {'CountryName': 'IPv4_1,Range,Alocated OR Assigned|IPv4_2,Range,Alocated OR Assigned|....'}
                    if not eachEntry[1] in IPv4[month][day].keys():
                        IPv4[month][day][eachEntry[1]] = eachEntry[3] + ',' + eachEntry[4] + ',' + eachEntry[6]
                    else:
                        IPv4[month][day][eachEntry[1]] = eachEntry[3] + ',' + eachEntry[4] + ',' + eachEntry[6] + '|' + \
                                                         IPv4[month][day][eachEntry[1]]
                elif eachEntry[2] == 'ipv6':
                    # we insert lines as following: {'CountryName': 'IPv6_1,CIDR,Alocated OR Assigned|IPv6_2,CIDR,Alocated OR Assigned|....'}
                    if not eachEntry[1] in IPv6[month][day].keys():
                        IPv6[month][day][eachEntry[1]] = eachEntry[3] + ',' + eachEntry[4] + ',' + eachEntry[6]
                    else:
                        IPv6[month][day][eachEntry[1]] = eachEntry[3] + ',' + eachEntry[4] + ',' + eachEntry[6] + '|' + \
                                                         IPv6[month][day][eachEntry[1]]
                elif eachEntry[2] == 'asn':
                    # we insert lines as following: {'CountryName': 'ASN,Numbers,Alocated OR Assigned|ASN2,Numbers,Alocated OR Assigned|....'}
                    if not eachEntry[1] in ASN[month][day].keys():
                        ASN[month][day][eachEntry[1]] = eachEntry[3] + ',' + eachEntry[4] + ',' + eachEntry[6]
                    else:
                        ASN[month][day][eachEntry[1]] = eachEntry[3] + ',' + eachEntry[4] + ',' + eachEntry[6] + '|' + \
                                                        ASN[month][day][eachEntry[1]]

def main():
    precomputation();
    download_ListOf_DatasetsFiles();
    download_DataSets();
    generate_metadata();
    FinalProcess();

main()
