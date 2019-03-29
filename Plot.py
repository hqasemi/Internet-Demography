import pickle, os, numpy as np, matplotlib.pyplot as plt, math, matplotlib

DataSets = ['lacnic', 'arin', 'apnic', 'afrinic', 'ripencc'];
# DataSets = ['ripencc'];
YearsToCheck = [2006, 2009, 2012, 2015, 2018];
slctdMonth = 6;
slctdDay = 1;
DatesToCheck = [i*10000+slctdMonth*100+slctdDay for i in YearsToCheck]#[20060601, 20090601, 20120601, 20150601, 20180601];

def preprocessing():
    for DataSetName in DataSets:
        if os.path.isfile('MetaData/'+DataSetName):
            [IPv4, IPv6, ASN] = load_obj('MetaData/' + DataSetName)
            for i in IPv4.keys():
                for j in IPv4[i].keys():
                    if not j == slctdMonth:
                        del IPv4[i][j]
                        del IPv6[i][j]
                        del ASN[i][j]
                    else:
                        for x in IPv4[i][j].keys():
                            if not x == slctdDay:
                                del IPv4[i][j][x]
                                del IPv6[i][j][x]
                                del ASN[i][j][x]
            save_obj('MetaData/' + DataSetName + '_ipv4', IPv4)
            save_obj('MetaData/' + DataSetName + '_ipv6', IPv6)
            save_obj('MetaData/' + DataSetName + '_asn', ASN)
            # os.remove('MetaData/' + DataSetName)
def save_obj(FileName,obj):
    with open(FileName, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
def load_obj(FileName):
    with open(FileName, 'rb') as f:
        return pickle.load(f)

def numberOfLinesPerCountry(inputDic, year, month, day):
    #excluding 'TotalNumber'
    country = [s for s in inputDic[year][month][day].keys() if not s=='TotalNumber'];
    numberOflines = [-1 for i in range(0,len(country))]
    tempIndex = 0;
    for i in country:
        numberOflines[tempIndex] = len(inputDic[year][month][day][i].split('|'))
        tempIndex += 1;
    return [country,numberOflines, inputDic[year][month][day]['TotalNumber']]
def numberOfElementPerCountry(inputDic, year, month, day):
    #excluding 'TotalNumber'
    country = [s for s in inputDic[year][month][day].keys() if not s=='TotalNumber']# and not s==''];
    numberOflines = [-1 for i in range(0,len(country))]
    numberOfElement = [-1 for i in range(0, len(country))]
    tempIndex = 0;
    for i in country:
        numberOflines[tempIndex] = len(inputDic[year][month][day][i].split('|'))
        numberOfElement[tempIndex] = 0;
        for j in inputDic[year][month][day][i].split('|'):
            numberOfElement[tempIndex] += int(j.split(',')[1])
        tempIndex += 1;
    return [country,numberOflines, numberOfElement, inputDic[year][month][day]['TotalNumber'], sum(numberOfElement)]
def country_AS(inputDic, year, month, day):
    #excluding 'TotalNumber'
    countries = [s for s in inputDic[year][month][day].keys() if not s=='TotalNumber']# and not s==''];
    ASes = {};
    for i in countries:
        ASes[i] = [];
        for j in inputDic[year][month][day][i].split('|'):
            try:
                tmp = int(j.split(',')[0])
            except:
                tmp = int(j.split(',')[0].split('.')[0])*65536+ int(j.split(',')[0].split('.')[1])
            ASes[i].append(tmp)
            # print ASes.keys()
            for x in range(1,int(j.split(',')[1])):
                ASes[i].append(tmp+int(x));
    return [countries,ASes]
def int_to_string_doubleDigit(x):
    if x < 10:
        return '0'+str(x);
    else:
        return str(x);
def remove_entry(txts, values, element_to_be_removed):
    for i in range(0, len(txts)):
        if element_to_be_removed in txts[i]:
            tmpLen = len(txts[i])-1;
            tmpIndx = txts[i].index(element_to_be_removed);
            txts[i][tmpIndx] = txts[i][tmpLen];
            values[i][tmpIndx] = values[i][tmpLen];
            txts[i].pop();
            values[i].pop();
    return [txts,values]
def remove_zero_values(txt,values):
    indexToBeRemoved = [];
    for j in range(0, len(txt)):
        tmp = 0;
        for i in range(0, len(values)):
            tmp+=values[i][j];
        if tmp == 0:
            indexToBeRemoved.append(j);

    for j in range(len(indexToBeRemoved)-1,-1,-1):
        txt.pop(j);
        for i in range(0,len(values)):
            values[i].pop(j);
    return [txt,values]
def make_same_size(txts, values):
    resTxt = [];
    for i in range(0, len(txts)):
        for cntry in txts[i]:
            if not cntry in resTxt:
                resTxt.append(cntry);

    resValues = [{} for i in range(0, len(values))];
    for i in range(0, len((values))):
        resValues[i] = [];
        for cntry in resTxt:
            if cntry in txts[i]:
                resValues[i].append(values[i][txts[i].index(cntry)]);
            else:
                resValues[i].append(0);
    return [resTxt, resValues];
def log(numberOflines):
    for i in range(0, len(numberOflines)):
        for j in range(0, len(numberOflines[i])):
            if not numberOflines[i][j] == 0:
                numberOflines[i][j] = math.log(numberOflines[i][j])
            else:
                numberOflines[i][j] = 0;#None;
    return numberOflines;
def load_year_month(years, months):
    [p2p, p2c] = [{}, {}]
    for year in years:
        for month in months:
            Date = year * 10000 + month * 100 + 01;
            if os.path.isfile('MetaData/as_relation/' + str(Date)):
                print Date
                [p2p[Date], p2c[Date]] = load_obj('MetaData/as_relation/' + str(Date));
    return [p2p,p2c]
def find_AS_for_each_region(datasetName):
    data = load_obj('MetaData/' + datasetName + '_asn')
    [countriesDic, ASDic] = [{} for i in range(0, 2)];
    for i in range(0, len(YearsToCheck)):
        [countriesDic[YearsToCheck[i]], ASDic[YearsToCheck[i]]] = country_AS(data, YearsToCheck[i], slctdMonth, slctdDay)

    return [countriesDic, ASDic];

def sort_basedon_year(txt,values,year):
    tmpInd = YearsToCheck.index(year);
    for i in range(0,len(values[tmpInd])-1):
        for j in range(i+1,len(values[tmpInd])):
            if values[tmpInd][i] < values[tmpInd][j]:
                temp = txt[j];
                txt[j] = txt[i];
                txt[i] = temp;
                for x in range(0,len(YearsToCheck)):
                    tmp = values[x][j];
                    values[x][j] = values[x][i];
                    values[x][i] = tmp;
    return [txt, values];
def plot_2D_old(XValues, xAxisLable, YValyes, yAxisLable, title, legends, fileName, maxNumberOfElementPerPlot ,typeOfPlot):
    MaxIteration = int(len(XValues)/(maxNumberOfElementPerPlot+1))+1;
    for itr in range(0,MaxIteration):
        [lowerBound, upperBound] = [itr * maxNumberOfElementPerPlot, (itr + 1) * maxNumberOfElementPerPlot];
        X = XValues[lowerBound:upperBound];
        Y = [{} for tmp1 in range(0,len(YValyes))];
        for tmp2 in range(0, len(YValyes)):
            Y[tmp2] = YValyes[tmp2][lowerBound:upperBound];
        fig, ax1 = plt.subplots()
        plt.xlabel(xAxisLable)
        plt.ylabel(yAxisLable)
        plt.title(title)
        if typeOfPlot == 'simple_xLabelString_withYears':
            # plt.plot(range(0, len(X)), Y[0],range(0, len(X)), Y[1])
            for i in range(0,len(Y)):
                plt.plot(range(0, len(X)), Y[i], label=legends[i])
            plt.xticks(range(0, len(X)), X)

            ax1.legend();
            fig.autofmt_xdate()

            fig = plt.gcf()
            fig.set_size_inches(22.5, 13.5)
            if MaxIteration > 1:
                fig.savefig('plots/' + fileName + '_part '+ str(itr) + '.png', dpi=200)
            else:
                fig.savefig('plots/' + fileName + '.png', dpi=200)

            # plt.show()
            # plt.savefig(fileName+'.png', bbox_inches='tight')
            plt.close()
def plot_2D(XValues, xAxisLable, YValyes, yAxisLable, title, legends, fileName, maxNumberOfElementPerPlot ,typeOfPlot):
    if typeOfPlot == 'simple_xLabelString_withYears':
        MaxIteration = int(len(XValues)/(maxNumberOfElementPerPlot+1))+1;
        for itr in range(0,MaxIteration):
            [lowerBound, upperBound] = [itr * maxNumberOfElementPerPlot, (itr + 1) * maxNumberOfElementPerPlot];
            X = XValues[lowerBound:upperBound];
            Y = [{} for tmp1 in range(0,len(YValyes))];
            for tmp2 in range(0, len(YValyes)):
                Y[tmp2] = YValyes[tmp2][lowerBound:upperBound];
            fig, ax1 = plt.subplots()
            plt.xlabel(xAxisLable)
            plt.ylabel(yAxisLable)
            plt.title(title)
            # plt.plot(range(0, len(X)), Y[0],range(0, len(X)), Y[1])
            for i in range(0,len(Y)):
                plt.plot(range(0, len(X)), Y[i], label=legends[i])
            plt.xticks(range(0, len(X)), X)

            ax1.legend();
            fig.autofmt_xdate()

            fig = plt.gcf()
            fig.set_size_inches(22.5, 13.5)
            if MaxIteration > 1:
                fig.savefig('plots/' + fileName + '_part '+ str(itr) + '.png', dpi=200)
            else:
                fig.savefig('plots/' + fileName + '.png', dpi=200)

            # plt.show()
            # plt.savefig(fileName+'.png', bbox_inches='tight')
            plt.close()
    elif typeOfPlot == 'log':
        plt.figure()  # you need to first do 'import pylab as plt'
        plt.grid(True);
        # linestyles = ['solid', 'dashed', 'dashdot', 'dotted']
        linestyles = ['-', '--', '-.', ':', '-']
        markers = ['o', 'v', '^', '<','>','.', '1','2','3','4']
        for i in range(0,len(YValyes)):
            # plt.loglog(XValues[i], YValyes[i], linestyle=linestyles[i], marker=markers[i])#, color='k')
            plt.loglog(XValues[i], YValyes[i], linestyle=linestyles[i])#, marker=markers[i])  # , color='k')
        # plt.loglog(XValues, YValyes)  # , 'o-')  # in-degree
        plt.legend(legends)
        plt.xlabel(xAxisLable)
        plt.ylabel(yAxisLable)
        plt.title(title)
        plt.xlim([0, 2 * 10 ** 2])
        plt.savefig('plots/' + fileName + '.png', dpi=200)
        # plt.show()
        plt.close()
def AS_Countries():
    preprocessing()
    for DataSetName in DataSets:
        # e.g., lacnic||asn|23523|2|reserved ------> this means that as numbers 23523 and 23524 are reserved
        for datatype in ['asn', 'ipv4', 'ipv6']:
            data = load_obj('MetaData/' + DataSetName + '_' + datatype)

            [countriesDic, numberOflines, totalNumberOfLines] = [{} for i in range(0,3)];
            for i in range(0,len(YearsToCheck)):
                [countriesDic[i], numberOflines[i], totalNumberOfLines[i]] = numberOfLinesPerCountry(data, YearsToCheck[i], slctdMonth, slctdDay)

            #remove un-assigned values from the list (the country name '' contains those values)
            [countriesDic, numberOflines] = remove_entry(countriesDic, numberOflines, '')

            #change the size of arrays to be equal to each other
            #'countries' before this function is a dictionary of arrays (each array for one year) but after this changes to
            # an array (all countries during all years)
            [countries, numberOflines] = make_same_size(countriesDic, numberOflines);

            [countries, numberOflines] = sort_basedon_year(countries,numberOflines,YearsToCheck[len(YearsToCheck)-1])

            # each plot contains at most 75 countries
            MaxNumberOfCountriesPerPlot = 76
            plot_2D(countries, 'Countries', numberOflines, 'number of ' + datatype + 's', DataSetName + ', ' + \
                    datatype, YearsToCheck, 'simple/'+ DataSetName + '_' + datatype, MaxNumberOfCountriesPerPlot ,'simple_xLabelString_withYears')
            #to have a comprehensive view of those figures with more than 58 countries
            if len(countries) > MaxNumberOfCountriesPerPlot:
                #each plot can contain up to 1000 countries
                plot_2D(countries, 'Countries', numberOflines, 'number of ' + datatype + 's', DataSetName + ', ' + \
                        datatype, YearsToCheck, 'simple/'+ DataSetName + '_' + datatype + '_WF', 1000, 'simple_xLabelString_withYears')

            # Ln
            numberOflines = log(numberOflines);
            # each plot contains at most 58 countries
            plot_2D(countries, 'Countries', numberOflines, 'Ln(number of ' + datatype + 's)', DataSetName + ', ' + \
                    datatype, YearsToCheck, 'log/'+ DataSetName + '_' + datatype+'_log', MaxNumberOfCountriesPerPlot, 'simple_xLabelString_withYears')
            #to have a comprehensive view of those figures with more than 58 countries
            if len(countries) > MaxNumberOfCountriesPerPlot:
                # each plot can contain up to 1000 countries
                plot_2D(countries, 'Countries', numberOflines, 'Ln(number of ' + datatype + 's)', DataSetName + ', ' + \
                        datatype, YearsToCheck, 'log/'+ DataSetName + '_' + datatype + '_WF'+'_log', 1000, 'simple_xLabelString_withYears')
def AS_Relation_Total():
    # [p2p,p2c] = load_obj('MetaData/as_relation/as_relation_graph.networkx')
    [p2p_values, p2p_hist] = [{}, {}];
    [p2c_values, p2c_hist] = [{}, {}];
    tmpIndx = 0;
    for Date in DatesToCheck:
        [p2p, p2c] = load_obj('MetaData/as_relation/' + str(Date));
        p2p_degrees = dict(p2p.degree())  # dictionary node:degree
        p2p_values[tmpIndx] = sorted(set(p2p_degrees.values()))
        p2p_hist[tmpIndx] = [p2p_degrees.values().count(x) for x in p2p_values[tmpIndx]]

        p2c_degrees = dict(p2c.degree())  # dictionary node:degree
        p2c_values[tmpIndx] = sorted(set(p2c_degrees.values()))
        p2c_hist[tmpIndx] = [p2c_degrees.values().count(x) for x in p2c_values[tmpIndx]]

        tmpIndx+=1;


    #plot last year comprises of both p2p and p2c
    plot_2D([p2p_values[tmpIndx-1], p2c_values[tmpIndx-1]], 'Degree', [p2p_hist[tmpIndx-1], p2c_hist[tmpIndx-1]], 'Number of nodes', 'ASN, Degree distribution, '+str(DatesToCheck[tmpIndx-1]),
            ['peer to peer', 'privider to customer'], 'asn_rel/' + str(DatesToCheck[tmpIndx-1])+' allAS', 1000000,'log')

    plot_2D(p2p_values, 'Degree', p2p_hist, 'Number of nodes',
            'ASN, Degree distribution, P2P', DatesToCheck, 'asn_rel/p2p_allYears_allAS', 1000000, 'log')

    plot_2D(p2c_values, 'Degree', p2c_hist, 'Number of nodes',
            'ASN, Degree distribution, P2C', DatesToCheck, 'asn_rel/p2c_allYears_allAS', 1000000, 'log')
def AS_Relation_Countries():
    [countries, ASes] = [{}, {}]
    for datasetName in DataSets:
        [countries[datasetName], ASes[datasetName]] = find_AS_for_each_region(datasetName);

    # [p2p,p2c] = load_obj('MetaData/as_relation/as_relation_graph.networkx')
    [p2p_values, p2p_hist] = [{}, {}];
    [p2c_values, p2c_hist] = [{}, {}];
    tmpIndx = 0;
    for Date in DatesToCheck:
        [p2p, p2c] = load_obj('MetaData/as_relation/' + str(Date));
        p2p_degrees = dict(p2p.degree())  # dictionary node:degree
        p2p_values[tmpIndx] = sorted(set(p2p_degrees.values()))
        p2p_hist[tmpIndx] = [p2p_degrees.values().count(x) for x in p2p_values[tmpIndx]]

        p2c_degrees = dict(p2c.degree())  # dictionary node:degree
        p2c_values[tmpIndx] = sorted(set(p2c_degrees.values()))
        p2c_hist[tmpIndx] = [p2c_degrees.values().count(x) for x in p2c_values[tmpIndx]]

        tmpIndx+=1;


    #plot last year comprises of both p2p and p2c
    plot_2D([p2p_values[tmpIndx-1], p2c_values[tmpIndx-1]], 'Degree', [p2p_hist[tmpIndx-1], p2c_hist[tmpIndx-1]], 'Number of nodes', 'ASN, Degree distribution, '+str(DatesToCheck[tmpIndx-1]),
            ['peer to peer', 'privider to customer'], 'asn_rel/' + str(DatesToCheck[tmpIndx-1])+' allAS', 1000000,'log')

    plot_2D(p2p_values, 'Degree', p2p_hist, 'Number of nodes',
            'ASN, Degree distribution, P2P', DatesToCheck, 'asn_rel/p2p_allYears_allAS', 1000000, 'log')

    plot_2D(p2c_values, 'Degree', p2c_hist, 'Number of nodes',
            'ASN, Degree distribution, P2C', DatesToCheck, 'asn_rel/p2c_allYears_allAS', 1000000, 'log')

# AS_Countries()
# AS_Relation_Total()


[countries, ASes] = [{}, {}]
for datasetName in DataSets:
    [countries[datasetName], ASes[datasetName]] = find_AS_for_each_region(datasetName);
AllASs = {};
for year in YearsToCheck:
    AllASs[year] = [];
for datasetName in DataSets:
    for year in YearsToCheck:
        for cntr in ASes[datasetName][year].keys():
            AllASs[year] = AllASs[year] + ASes[datasetName][year][cntr]
for year in YearsToCheck:
    print len(AllASs[year])
# for Date in DatesToCheck:
#     [p2p, p2c] = load_obj('MetaData/as_relation/' + str(Date));
#     print p2p.nodes()

