# before 2019


import os.path
import sys
import os
from datetime import datetime
import hashlib
import logging
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from locale import setlocale, LC_NUMERIC

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

__all__ = []
__version__ = 0.1
__date__ = '2022-04-19'
__updated__ = '2022-04-19'

DEBUG = 1
TESTRUN = 0
PROFILE = 0
PLOT_FEATURES_PER_INCH = 6
PLOT_WIDTH = 6

def plotDiseaseData():
    pass


def plotIFsbyLocation():
    plotFolder = os.path.join(os.path.dirname(gDiseaseListFile), "plots")
    if not os.path.exists(plotFolder):
        logging.info("--plot folder <" + plotFolder + "> doesn't exist, creating")
        os.makedirs(plotFolder)
    for diseaseFile in dfDiseaseList:
        diseaseName = os.path.basename(diseaseFile).split(".")[0]
        outputFolder = os.path.join(plotFolder, diseaseName)
        if not os.path.exists(outputFolder):
            logging.info("--output folder <" + outputFolder + "> doesn't exist, creating")
            os.makedirs(outputFolder)

        logging.info('--' + diseaseName)
        dfStats=pd.read_csv(diseaseFile)
        plotPubsByYear(diseaseName, dfStats, outputFolder)
        plotBoxplotAll(diseaseName, dfStats, outputFolder)
        plotViolinAll(diseaseName, dfStats, outputFolder)

        if int(gSplitYear) != 0:
            plotBoxplotBeforeSplitYear(diseaseName, dfStats, outputFolder, gSplitYear)
            plotBoxplotOnOrAfterSplitYear(diseaseName, dfStats, outputFolder, gSplitYear)
            plotViolinBeforeSplitYear(diseaseName, dfStats, outputFolder, gSplitYear)
            plotViolinOnOrAfterSplitYear(diseaseName, dfStats, outputFolder, gSplitYear)

def plotPubsByYear(disease, dfStats, plotFolder):

    sYear=dfStats[dfStats['year']!=0]['year'].value_counts()
    lYear={'year':sYear.index.astype(int), 'values': sYear.values.astype(int)}
    dfYear=pd.DataFrame(lYear)

    res=sns.relplot(x='year', y='values', size='values', hue='year', data=dfYear)
    for axes in res.axes.flat:
        _ = axes.set_xticklabels(axes.get_xticklabels(), fontsize=12, rotation=45)
    res._legend.remove()

    yint = []
    locs, labels = plt.yticks()
    for each in locs:
        yint.append(int(each))
    plt.yticks(yint)
    plotTitle = "[" + disease + "] total publications by year"
    plt.title(plotTitle, fontsize=14, color='darkslategray')

    plt.xlabel('Year', fontsize=12, color='darkslategray')
    plt.ylabel('No of Publications', fontsize=14, color='darkslategray')

    plotFilename = disease  + "__" + "no_of_pubs_by_year." + gOutputPlotFormat
    plotFilePath = os.path.join(plotFolder, plotFilename)
    plt.savefig(plotFilePath, dpi=int(gPlotResolutionDPI), bbox_inches='tight')
    plt.close()

#############################################################################
#
#                      BOXPLOTS
#
#############################################################################


def plotBoxplotAll(disease, dfStats, plotFolder):
    logging.getLogger('matplotlib').disabled = True
    noOfFirstFeatures = len(dfStats[dfStats['firstCountry'].isna() == False]['firstCountry'].unique())
    plt.figure(figsize=(int(PLOT_WIDTH), int(noOfFirstFeatures/PLOT_FEATURES_PER_INCH)+1))

    #first country
    sbBoxplot=sns.boxplot(x=dfStats['impactFactor'],
                          y=dfStats[dfStats['firstCountry'] != 'unknown']['firstCountry'],
                          palette="Blues")
    plotTitle = "[" + disease + "] IFs by first author country"
    sbBoxplot.set_title(plotTitle, fontsize=18, color='darkslategray')
    plt.xlabel("impact factor", labelpad=24, fontsize=15)
    plt.ylabel("country", labelpad=44, fontsize=15)
    plt.xlim(0, round(int(dfStats[dfStats['firstCountry'].isna() == False]['impactFactor'].max())*10)/10 + 10)

    plotFilename = disease  + "__" + "IF_by_firstcountry__boxplot." + gOutputPlotFormat
    plotFilePath = os.path.join(plotFolder, plotFilename)
    plt.savefig(plotFilePath, dpi=int(gPlotResolutionDPI), bbox_inches='tight')
    plt.close()

    #last country
    noOfLastFeatures = len(dfStats[dfStats['lastCountry'].isna() == False]['lastCountry'].unique())
    plt.figure(figsize=(int(PLOT_WIDTH), int(noOfLastFeatures/PLOT_FEATURES_PER_INCH)+1))

    sbBoxplot=sns.boxplot(x=dfStats['impactFactor'],
                          y=dfStats[dfStats['lastCountry'] != 'unknown']['lastCountry'],
                          palette="Blues")
    plotTitle = "[" + disease + "] IFs by last author country"
    sbBoxplot.set_title(plotTitle, fontsize=18, color='darkslategray')
    plt.xlabel("impact factor", labelpad=24, fontsize=15)
    plt.ylabel("country", labelpad=44, fontsize=15)
    plt.xlim(0, round(int(dfStats[dfStats['lastCountry'].isna() == False]['impactFactor'].max())*10)/10 + 10)

    plotFilename = disease  + "__" + "IF_by_lastcountry__boxplot." + gOutputPlotFormat
    plotFilePath = os.path.join(plotFolder, plotFilename)
    plt.savefig(plotFilePath, dpi=int(gPlotResolutionDPI), bbox_inches='tight')
    plt.close()

    # first Region
    for indexS, stat in dfStats.iterrows():
        if pd.isna(stat['firstCountry']):
            dfStats.at[indexS, "firstRegion"] = "unknown"
        else:
            dfStats.at[indexS, "firstRegion"] = getRegionFromCountry(stat['firstCountry'])

    sbBoxplot=sns.boxplot(x=dfStats['impactFactor'],
                          y=dfStats[dfStats['firstRegion'] != 'unknown']['firstRegion'],
                          palette="Blues")
    plotTitle = "[" + disease + "] IFs by first author region"
    sbBoxplot.set_title(plotTitle, fontsize=18, color='darkslategray')
    plt.xlabel("impact factor", labelpad=24, fontsize=15)
    plt.ylabel("region", labelpad=44, fontsize=15)
    plt.xlim(0, round(int(dfStats[dfStats['firstRegion'] != 'unknown']['impactFactor'].max())*10)/10 + 10)

    plotFilename = disease + "__" + "IF_by_firstregion__boxplot." + gOutputPlotFormat
    plotFilePath = os.path.join(plotFolder, plotFilename)
    plt.savefig(plotFilePath, dpi=int(gPlotResolutionDPI), bbox_inches='tight')
    plt.close()

    # last Region
    for indexS, stat in dfStats.iterrows():
        if pd.isna(stat['lastCountry']):
            dfStats.at[indexS, "lastRegion"] = "unknown"
        else:
            dfStats.at[indexS, "lastRegion"] = getRegionFromCountry(stat['lastCountry'])

    sbBoxplot=sns.boxplot(x=dfStats['impactFactor'],
                          y=dfStats[dfStats['lastRegion'] != 'unknown']['lastRegion'],
                          palette="Blues")
    plotTitle = "[" + disease + "] IFs by last author region"
    sbBoxplot.set_title(plotTitle, fontsize=18, color='darkslategray')
    plt.xlabel("impact factor", labelpad=24, fontsize=15)
    plt.ylabel("region", labelpad=44, fontsize=15)
    plt.xlim(0, round(int(dfStats[dfStats['firstRegion'] != 'unknown']['impactFactor'].max())*10)/10 + 10)

    plotFilename = disease + "__" + "IF_by_lastregion__boxplot." + gOutputPlotFormat
    plotFilePath = os.path.join(plotFolder, plotFilename)
    plt.savefig(plotFilePath, dpi=int(gPlotResolutionDPI), bbox_inches='tight')
    plt.close()


def plotBoxplotBeforeSplitYear(disease, dfStats, plotFolder, splitYear):
    dfStatsBeforeSplit = dfStats[dfStats['year']<int(splitYear)]

    logging.getLogger('matplotlib').disabled = True
    noOfFirstFeatures = len(dfStatsBeforeSplit[dfStatsBeforeSplit['firstCountry'] != 'unknown']['firstCountry'].unique())
    plt.figure(figsize=(int(PLOT_WIDTH), int(noOfFirstFeatures/PLOT_FEATURES_PER_INCH)+1))

    # first country
    sbBoxplot=sns.boxplot(x=dfStatsBeforeSplit['impactFactor'],
                          y=dfStatsBeforeSplit[dfStatsBeforeSplit['firstCountry']!='unknown']['firstCountry'],
                          palette="Blues")
    plotTitle = "[" + disease + "] IFs by first author country before " + str(splitYear)
    sbBoxplot.set_title(plotTitle, fontsize=18, color='darkslategray')
    plt.xlabel("impact factor", labelpad=24, fontsize=15)
    plt.ylabel("country", labelpad=44, fontsize=15)
    plt.xlim(0, round(int(dfStats[dfStats['firstCountry'].isna() == False]['impactFactor'].max())*10)/10 + 10)

    plotFilename = disease  + "__IFs_firstcountry_before__"  + str(splitYear) + "__boxplot." + gOutputPlotFormat
    plotFilePath = os.path.join(plotFolder, plotFilename)
    plt.savefig(plotFilePath, dpi=int(gPlotResolutionDPI), bbox_inches='tight')
    plt.close()

    # last country
    noOfLastFeatures = len(dfStatsBeforeSplit[dfStatsBeforeSplit['lastCountry'] != 'unknown']['lastCountry'].unique())
    plt.figure(figsize=(int(PLOT_WIDTH), int(noOfLastFeatures/PLOT_FEATURES_PER_INCH)+1))

    sbBoxplot=sns.boxplot(x=dfStatsBeforeSplit['impactFactor'],
                          y=dfStatsBeforeSplit[dfStatsBeforeSplit['lastCountry']!='unknown']['lastCountry'],
                          palette="Blues")
    plotTitle = "[" + disease + "] IFs by last author country before " + str(splitYear)
    sbBoxplot.set_title(plotTitle, fontsize=18, color='darkslategray')
    plt.xlabel("impact factor", labelpad=24, fontsize=15)
    plt.ylabel("country", labelpad=44, fontsize=15)
    plt.xlim(0, round(int(dfStats[dfStats['lastCountry'].isna() == False]['impactFactor'].max())*10)/10 + 10)

    plotFilename = disease  + "__IFs_lastcountry_before__"  + str(splitYear) + "__boxplot." + gOutputPlotFormat
    plotFilePath = os.path.join(plotFolder, plotFilename)
    plt.savefig(plotFilePath, dpi=int(gPlotResolutionDPI), bbox_inches='tight')
    plt.close()

    # first Region
    for indexS, stat in dfStats.iterrows():
        if pd.isna(stat['firstCountry']):
            dfStats.at[indexS, "firstRegion"] = "unknown"
        else:
            dfStats.at[indexS, "firstRegion"] = getRegionFromCountry(stat['firstCountry'])

    sbBoxplot=sns.boxplot(x=dfStats['impactFactor'],
                          y=dfStats[(dfStats['year']< int(splitYear)) & (dfStats['firstRegion']!='unknown')]['firstRegion'],
                          palette="Blues")
    plotTitle = "[" + disease + "] IFs by first author region before " + str(splitYear)
    sbBoxplot.set_title(plotTitle, fontsize=18, color='darkslategray')
    plt.xlabel("impact factor", labelpad=24, fontsize=15)
    plt.ylabel("region", labelpad=44, fontsize=15)
    plt.xlim(0, round(int(dfStats[dfStats['firstRegion'] != 'unknown']['impactFactor'].max())*10)/10 + 10)

    plotFilename = disease  + "__IFs_firstregion_before__"  + str(splitYear) + "__boxplot." + gOutputPlotFormat
    plotFilePath = os.path.join(plotFolder, plotFilename)
    plt.savefig(plotFilePath, dpi=int(gPlotResolutionDPI), bbox_inches='tight')
    plt.close()

    # last Region
    for indexS, stat in dfStats.iterrows():
        if pd.isna(stat['lastCountry']):
            dfStats.at[indexS, "lastRegion"] = "unknown"
        else:
            dfStats.at[indexS, "lastRegion"] = getRegionFromCountry(stat['lastCountry'])

    sbBoxplot=sns.boxplot(x=dfStats['impactFactor'],
                          y=dfStats[(dfStats['year']< int(splitYear)) & (dfStats['lastRegion']!='unknown')]['lastRegion'],
                          palette="Blues")
    plotTitle = "[" + disease + "] IFs by last author region before " + str(splitYear)
    sbBoxplot.set_title(plotTitle, fontsize=18, color='darkslategray')
    plt.xlabel("impact factor", labelpad=24, fontsize=15)
    plt.ylabel("region", labelpad=44, fontsize=15)
    plt.xlim(0, round(int(dfStats[dfStats['lastRegion'] != 'unknown']['impactFactor'].max())*10)/10 + 10)

    plotFilename = disease  + "__IFs_lastregion_before__"  + str(splitYear) + "__boxplot." + gOutputPlotFormat
    plotFilePath = os.path.join(plotFolder, plotFilename)
    plt.savefig(plotFilePath, dpi=int(gPlotResolutionDPI), bbox_inches='tight')
    plt.close()



def plotBoxplotOnOrAfterSplitYear(disease, dfStats, plotFolder, splitYear):
    dfStatsAfterSplit=dfStats[dfStats['year']>=int(splitYear)]

    logging.getLogger('matplotlib').disabled = True
    noOfFirstFeatures = len(dfStatsAfterSplit[dfStatsAfterSplit['firstCountry'] != 'unknown']['firstCountry'].unique())
    plt.figure(figsize=(int(PLOT_WIDTH), int(noOfFirstFeatures/PLOT_FEATURES_PER_INCH)+1))

    # first country
    sbBoxplot=sns.boxplot(x=dfStatsAfterSplit['impactFactor'],
                          y=dfStatsAfterSplit[dfStatsAfterSplit['firstCountry']!='unknown']['firstCountry'],
                          palette="Blues")
    plotTitle = "[" + disease + "] IFs by first author country on or after " + str(splitYear)
    sbBoxplot.set_title(plotTitle, fontsize=18, color='darkslategray')
    plt.xlabel("impact factor", labelpad=24, fontsize=15)
    plt.ylabel("country", labelpad=44, fontsize=15)
    plt.xlim(0, round(int(dfStats[dfStats['firstCountry'].isna() == False]['impactFactor'].max())*10)/10 + 10)

    plotFilename = disease  + "__IFs_firstcountry_onOrAfter__"  + str(splitYear) + "__boxplot." + gOutputPlotFormat
    plotFilePath = os.path.join(plotFolder, plotFilename)
    plt.savefig(plotFilePath, dpi=int(gPlotResolutionDPI), bbox_inches='tight')
    plt.close()

    # last country
    noOfLastFeatures = len(dfStatsAfterSplit[dfStatsAfterSplit['lastCountry'] != 'unknown']['lastCountry'].unique())
    plt.figure(figsize=(int(PLOT_WIDTH), int(noOfLastFeatures/PLOT_FEATURES_PER_INCH)+1))

    sbBoxplot=sns.boxplot(x=dfStatsAfterSplit['impactFactor'],
                          y=dfStatsAfterSplit[dfStatsAfterSplit['lastCountry']!='unknown']['lastCountry'],
                          palette="Blues")
    plotTitle = "[" + disease + "] IFs by last author country on or after " + str(splitYear)
    sbBoxplot.set_title(plotTitle, fontsize=18, color='darkslategray')
    plt.xlabel("impact factor", labelpad=24, fontsize=15)
    plt.ylabel("country", labelpad=44, fontsize=15)
    plt.xlim(0, round(int(dfStats[dfStats['lastCountry'].isna() == False]['impactFactor'].max())*10)/10 + 10)

    plotFilename = disease  + "__IFs_lastcountry_onOrAfter__"  + str(splitYear) + "__boxplot." + gOutputPlotFormat
    plotFilePath = os.path.join(plotFolder, plotFilename)
    plt.savefig(plotFilePath, dpi=int(gPlotResolutionDPI), bbox_inches='tight')
    plt.close()

    # first Region
    for indexS, stat in dfStats.iterrows():
        if pd.isna(stat['firstCountry']):
            dfStats.at[indexS, "firstRegion"] = "unknown"
        else:
            dfStats.at[indexS, "firstRegion"] = getRegionFromCountry(stat['firstCountry'])

    sbBoxplot=sns.boxplot(x=dfStats['impactFactor'],
                          y=dfStats[(dfStats['year']>= int(splitYear)) & (dfStats['firstRegion']!='unknown')]['firstRegion'],
                          palette="Blues")
    plotTitle = "[" + disease + "] IFs by first author region on or after " + str(splitYear)
    sbBoxplot.set_title(plotTitle, fontsize=18, color='darkslategray')
    plt.xlabel("impact factor", labelpad=24, fontsize=15)
    plt.ylabel("region", labelpad=44, fontsize=15)
    plt.xlim(0, round(int(dfStats[dfStats['firstRegion'] != 'unknown']['impactFactor'].max())*10)/10 + 10)

    plotFilename = disease  + "__IFs_firstregion_onOrAfter__"  + str(splitYear) + "__boxplot." + gOutputPlotFormat
    plotFilePath = os.path.join(plotFolder, plotFilename)
    plt.savefig(plotFilePath, dpi=int(gPlotResolutionDPI), bbox_inches='tight')
    plt.close()

    # last Region
    for indexS, stat in dfStats.iterrows():
        if pd.isna(stat['lastCountry']):
            dfStats.at[indexS, "lastRegion"] = "unknown"
        else:
            dfStats.at[indexS, "lastRegion"] = getRegionFromCountry(stat['lastCountry'])

    sbBoxplot=sns.boxplot(x=dfStats['impactFactor'],
                          y=dfStats[(dfStats['year']>= int(splitYear)) & (dfStats['lastRegion']!='unknown')]['lastRegion'],
                          palette="Blues")
    plotTitle = "[" + disease + "] IFs by last author region on or after " + str(splitYear)
    sbBoxplot.set_title(plotTitle, fontsize=18, color='darkslategray')
    plt.xlabel("impact factor", labelpad=24, fontsize=15)
    plt.ylabel("region", labelpad=44, fontsize=15)
    plt.xlim(0, round(int(dfStats[dfStats['lastRegion'] != 'unknown']['impactFactor'].max())*10)/10 + 10)

    plotFilename = disease  + "__IFs_lastregion_onOrAfter__"  + str(splitYear) + "__boxplot." + gOutputPlotFormat
    plotFilePath = os.path.join(plotFolder, plotFilename)
    plt.savefig(plotFilePath, dpi=int(gPlotResolutionDPI), bbox_inches='tight')
    plt.close()


#############################################################################
#
#                      VIOLIN PLOTS
#
#############################################################################

def plotViolinAll(disease, dfStats, plotFolder):
    logging.getLogger('matplotlib').disabled = True
    noOfFirstFeatures = len(dfStats[dfStats['firstCountry'] != 'unknown']['firstCountry'].unique())
    plt.figure(figsize=(int(PLOT_WIDTH), int(noOfFirstFeatures/PLOT_FEATURES_PER_INCH)+1))
    plt.ioff()

    # first Country
    sbViolin=sns.violinplot(y='firstCountry', x='impactFactor',
                   data=dfStats, fontsize=12, linewidth=0.5)
    plotTitle = "[" + disease + "] IFs by first author country"
    sbViolin.set_title(plotTitle, fontsize=18, color='darkslategray')
    plt.xlabel("impact factor", labelpad=24, fontsize=15)
    plt.ylabel("country", labelpad=44, fontsize=15)
    plt.xlim(0, round(int(dfStats[dfStats['firstCountry'].isna() == False]['impactFactor'].max())*10)/10 + 10)

    plotFilename = disease + "__" + "IF_by_firstcountry__violinplot." + gOutputPlotFormat
    plotFilePath = os.path.join(plotFolder, plotFilename)
    plt.savefig(plotFilePath, dpi=int(gPlotResolutionDPI), bbox_inches='tight')
    plt.close()

    # last Country
    noOfLastFeatures = len(dfStats[dfStats['lastCountry'] != 'unknown']['lastCountry'].unique())
    plt.figure(figsize=(int(PLOT_WIDTH), int(noOfLastFeatures/PLOT_FEATURES_PER_INCH)+1))
    sbViolin=sns.violinplot(y='lastCountry', x='impactFactor',
                   data=dfStats, fontsize=12, linewidth=0.5)
    plotTitle = "[" + disease + "] IFs by last author country"
    sbViolin.set_title(plotTitle, fontsize=18, color='darkslategray')
    plt.xlabel("impact factor", labelpad=24, fontsize=15)
    plt.ylabel("country", labelpad=44, fontsize=15)
    plt.xlim(0, round(int(dfStats[dfStats['lastCountry'].isna() == False]['impactFactor'].max())*10)/10 + 10)



    plotFilename = disease + "__" + "IF_by_lastcountry__violinplot." + gOutputPlotFormat
    plotFilePath = os.path.join(plotFolder, plotFilename)
    plt.savefig(plotFilePath, dpi=int(gPlotResolutionDPI), bbox_inches='tight')
    plt.close()

    # first Region
    for indexS, stat in dfStats.iterrows():
        if pd.isna(stat['firstCountry']):
            dfStats.at[indexS, "firstRegion"] = "unknown"
        else:
            dfStats.at[indexS, "firstRegion"] = getRegionFromCountry(stat['firstCountry'])

    sbViolin=sns.violinplot(y='firstRegion', x='impactFactor',
                   data=dfStats[dfStats['firstRegion'] != 'unknown'], fontsize=12, linewidth=0.5)
    plotTitle = "[" + disease + "] IFs by first author region"
    sbViolin.set_title(plotTitle, fontsize=18, color='darkslategray')
    plt.xlabel("impact factor", labelpad=24, fontsize=15)
    plt.ylabel("region", labelpad=44, fontsize=15)
    plt.xlim(0, round(int(dfStats[dfStats['firstRegion'] != 'unknown']['impactFactor'].max())*10)/10 + 10)


    plotFilename = disease + "__" + "IF_by_firstregion__violinplot." + gOutputPlotFormat
    plotFilePath = os.path.join(plotFolder, plotFilename)
    plt.savefig(plotFilePath, dpi=int(gPlotResolutionDPI), bbox_inches='tight')
    plt.close()


    # last Region
    for indexS, stat in dfStats.iterrows():
        if pd.isna(stat['lastCountry']):
            dfStats.at[indexS, "lastRegion"] = "unknown"
        else:
            dfStats.at[indexS, "lastRegion"] = getRegionFromCountry(stat['lastCountry'])

    sbViolin=sns.violinplot(y='lastRegion', x='impactFactor',
                   data=dfStats[dfStats['lastRegion'] != 'unknown'], fontsize=12, linewidth=0.5)
    plotTitle = "[" + disease + "] IFs by last author region"
    sbViolin.set_title(plotTitle, fontsize=18, color='darkslategray')
    plt.xlabel("impact factor", labelpad=24, fontsize=15)
    plt.ylabel("region", labelpad=44, fontsize=15)
    plt.xlim(0, round(int(dfStats[dfStats['lastRegion'] != 'unknown']['impactFactor'].max())*10)/10 + 10)

    plotFilename = disease + "__" + "IF_by_lastregion__violinplot." + gOutputPlotFormat
    plotFilePath = os.path.join(plotFolder, plotFilename)
    plt.savefig(plotFilePath, dpi=int(gPlotResolutionDPI), bbox_inches='tight')
    plt.close()




def plotViolinBeforeSplitYear(disease, dfStats, plotFolder, splitYear):

    dfStatsBeforeSplit=dfStats[dfStats['year']<int(splitYear)]
    logging.getLogger('matplotlib').disabled = True
    noOfFirstFeatures = len(dfStatsBeforeSplit[dfStatsBeforeSplit['firstCountry'] != 'unknown']['firstCountry'].unique())
    plt.figure(figsize=(int(PLOT_WIDTH), int(noOfFirstFeatures/PLOT_FEATURES_PER_INCH)+1))

    # first Country
    sbViolin=sns.violinplot(y='firstCountry', x='impactFactor',
                   data=dfStatsBeforeSplit,fontsize=12, linewidth=0.5)

    plotTitle = "[" + disease + "] IFs by first author country before " + str(splitYear)
    sbViolin.set_title(plotTitle, fontsize=18, color='darkslategray')
    plt.xlabel("impactFactor", labelpad=14, fontsize=14)
    plt.ylabel("country", labelpad=14, fontsize=14)
    plt.xlim(0, round(int(dfStats[dfStats['firstCountry'].isna() == False]['impactFactor'].max())*10)/10 + 10)

    plotFilename = disease  + "__IFs_firstcountry_before__"  + str(splitYear) + "__violinplot." + gOutputPlotFormat
    plotFilePath = os.path.join(plotFolder, plotFilename)
    plt.savefig(plotFilePath, dpi=int(gPlotResolutionDPI), bbox_inches='tight')
    plt.close()

    # last Country
    noOfLastFeatures = len(dfStatsBeforeSplit[dfStatsBeforeSplit['lastCountry'] != 'unknown']['lastCountry'].unique())
    plt.figure(figsize=(int(PLOT_WIDTH), int(noOfLastFeatures/PLOT_FEATURES_PER_INCH)+1))
    sbViolin=sns.violinplot(y='lastCountry', x='impactFactor',
                   data=dfStatsBeforeSplit,fontsize=12, linewidth=0.5)

    plotTitle = "[" + disease + "] IFs by last author country before " + str(splitYear)
    sbViolin.set_title(plotTitle, fontsize=18, color='darkslategray')
    plt.xlabel("impactFactor", labelpad=14, fontsize=14)
    plt.ylabel("country", labelpad=14, fontsize=14)
    plt.xlim(0, round(int(dfStats[dfStats['lastCountry'].isna() == False]['impactFactor'].max())*10)/10 + 10)

    plotFilename = disease  + "__IFs_lastcountry_before__"  + str(splitYear) + "__violinplot." + gOutputPlotFormat
    plotFilePath = os.path.join(plotFolder, plotFilename)
    plt.savefig(plotFilePath, dpi=int(gPlotResolutionDPI), bbox_inches='tight')
    plt.close()


    # first Region
    for indexS, stat in dfStats.iterrows():
        if pd.isna(stat['firstCountry']):
            dfStats.at[indexS, "firstRegion"] = "unknown"
        else:
            dfStats.at[indexS, "firstRegion"] = getRegionFromCountry(stat['firstCountry'])

    sbViolin = sns.violinplot(y='firstRegion', x='impactFactor',
                   data=dfStats[(dfStats['year']< int(splitYear)) & (dfStats['firstRegion']!='unknown')],
                   fontsize=12, linewidth=0.5)

    plotTitle = "[" + disease + "] IFs by first author region before " + str(splitYear)
    sbViolin.set_title(plotTitle, fontsize=18, color='darkslategray')
    plt.xlabel("impact factor", labelpad=24, fontsize=15)
    plt.ylabel("region", labelpad=44, fontsize=15)
    plt.xlim(0, round(int(dfStats[dfStats['firstRegion'] != 'unknown']['impactFactor'].max())*10)/10 + 10)

    plotFilename = disease  + "__IFs_firstregion_before__"  + str(splitYear) + "__violinplot." + gOutputPlotFormat
    plotFilePath = os.path.join(plotFolder, plotFilename)
    plt.savefig(plotFilePath, dpi=int(gPlotResolutionDPI), bbox_inches='tight')
    plt.close()

    # last Region
    for indexS, stat in dfStats.iterrows():
        if pd.isna(stat['lastCountry']):
            dfStats.at[indexS, "lastRegion"] = "unknown"
        else:
            dfStats.at[indexS, "lastRegion"] = getRegionFromCountry(stat['lastCountry'])

    sbViolin = sns.violinplot(y='lastRegion', x='impactFactor',
                   data=dfStats[(dfStats['year'] < int(splitYear)) & (dfStats['firstRegion']!='unknown')],
                   fontsize=12, linewidth=0.5)
    plotTitle = "[" + disease + "] IFs by last author region before " + str(splitYear)
    sbViolin.set_title(plotTitle, fontsize=18, color='darkslategray')
    plt.xlabel("impact factor", labelpad=24, fontsize=15)
    plt.ylabel("region", labelpad=44, fontsize=15)
    plt.xlim(0, round(int(dfStats[dfStats['firstRegion'] != 'unknown']['impactFactor'].max())*10)/10 + 10)

    plotFilename = disease  + "__IFs_lastregion_before__"  + str(splitYear) + "__violinplot." + gOutputPlotFormat
    plotFilePath = os.path.join(plotFolder, plotFilename)
    plt.savefig(plotFilePath, dpi=int(gPlotResolutionDPI), bbox_inches='tight')
    plt.close()




def plotViolinOnOrAfterSplitYear(disease, dfStats, plotFolder, splitYear):

    dfStatsAfterSplit=dfStats[dfStats['year']>=int(splitYear)]
    logging.getLogger('matplotlib').disabled = True
    noOfFirstFeatures = len(dfStatsAfterSplit[dfStatsAfterSplit['firstCountry'] != 'unknown']['firstCountry'].unique())
    plt.figure(figsize=(int(PLOT_WIDTH), int(noOfFirstFeatures/PLOT_FEATURES_PER_INCH)+1))

    # first Country
    sbViolin=sns.violinplot(y='firstCountry', x='impactFactor',
                   data=dfStatsAfterSplit,fontsize=12, linewidth=0.5)

    plotTitle = "[" + disease + "] IFs by first author country on or after " + str(splitYear)
    sbViolin.set_title(plotTitle, fontsize=18, color='darkslategray')
    plt.xlabel("impact factor", labelpad=24, fontsize=15)
    plt.ylabel("country", labelpad=44, fontsize=15)
    plt.xlim(0, round(int(dfStats[dfStats['firstCountry'].isna() == False]['impactFactor'].max())*10)/10 + 10)

    plotFilename = disease  + "__IFs_firstcountry_onOrAfter__"  + str(splitYear) + "__violinplot." + gOutputPlotFormat
    plotFilePath = os.path.join(plotFolder, plotFilename)
    plt.savefig(plotFilePath, dpi=int(gPlotResolutionDPI), bbox_inches='tight')
    plt.close()

    # last Country
    noOfLastFeatures = len(dfStatsAfterSplit[dfStatsAfterSplit['lastCountry'] != 'unknown']['lastCountry'].unique())
    plt.figure(figsize=(int(PLOT_WIDTH), int(noOfLastFeatures/PLOT_FEATURES_PER_INCH)+1))
    sbViolin=sns.violinplot(y='lastCountry', x='impactFactor',
                   data=dfStatsAfterSplit,fontsize=12, linewidth=0.5)

    plotTitle = "[" + disease + "] IFs by last author country on or after " + str(splitYear)
    sbViolin.set_title(plotTitle, fontsize=18, color='darkslategray')
    plt.xlabel("impact factor", labelpad=24, fontsize=15)
    plt.ylabel("country", labelpad=44, fontsize=15)
    plt.xlim(0, round(int(dfStats[dfStats['lastCountry'].isna() == False]['impactFactor'].max())*10)/10 + 10)

    plotFilename = disease  + "__IFs_lastcountry_onOrAfter__"  + str(splitYear) + "__violinplot." + gOutputPlotFormat
    plotFilePath = os.path.join(plotFolder, plotFilename)
    plt.savefig(plotFilePath, dpi=int(gPlotResolutionDPI), bbox_inches='tight')
    plt.close()

    # first Region
    for indexS, stat in dfStats.iterrows():
        if pd.isna(stat['firstCountry']):
            dfStats.at[indexS, "firstRegion"] = "unknown"
        else:
            dfStats.at[indexS, "firstRegion"] = getRegionFromCountry(stat['firstCountry'])

    sbViolin = sns.violinplot(y='firstRegion', x='impactFactor',
                   data=dfStats[(dfStats['year']>= int(splitYear)) & (dfStats['firstRegion']!='unknown')],
                   fontsize=12, linewidth=0.5)

    plotTitle = "[" + disease + "] IFs by first author region on or after " + str(splitYear)
    sbViolin.set_title(plotTitle, fontsize=18, color='darkslategray')
    plt.xlabel("impact factor", labelpad=24, fontsize=15)
    plt.ylabel("region", labelpad=44, fontsize=15)
    plt.xlim(0, round(int(dfStats[dfStats['firstRegion'] != 'unknown']['impactFactor'].max())*10)/10 + 10)

    plotFilename = disease  + "__IFs_firstregion_onOrAfter__"  + str(splitYear) + "__violinplot." + gOutputPlotFormat
    plotFilePath = os.path.join(plotFolder, plotFilename)
    plt.savefig(plotFilePath, dpi=int(gPlotResolutionDPI), bbox_inches='tight')
    plt.close()

    # last Region
    for indexS, stat in dfStats.iterrows():
        if pd.isna(stat['lastCountry']):
            dfStats.at[indexS, "lastRegion"] = "unknown"
        else:
            dfStats.at[indexS, "lastRegion"] = getRegionFromCountry(stat['lastCountry'])

    sbViolin = sns.violinplot(y='firstRegion', x='impactFactor',
                   data=dfStats[(dfStats['year']>= int(splitYear)) & (dfStats['firstRegion']!='unknown')],
                   fontsize=12, linewidth=0.5)
    plotTitle = "[" + disease + "] IFs by last author region on or after " + str(splitYear)
    sbViolin.set_title(plotTitle, fontsize=18, color='darkslategray')
    plt.xlabel("impact factor", labelpad=24, fontsize=15)
    plt.ylabel("region", labelpad=44, fontsize=15)
    plt.xlim(0, round(int(dfStats[dfStats['firstRegion'] != 'unknown']['impactFactor'].max())*10)/10 + 10)

    plotFilename = disease  + "__IFs_lastregion_onOrAfter__"  + str(splitYear) + "__violinplot." + gOutputPlotFormat
    plotFilePath = os.path.join(plotFolder, plotFilename)
    plt.savefig(plotFilePath, dpi=int(gPlotResolutionDPI), bbox_inches='tight')
    plt.close()


def getRegionFromCountry(qCountry):
    #print(qCountry)

    for indexC, countryEntry in dfCountryData.iterrows():
        if not qCountry:
            return ""
        for country in countryEntry['country'].split("|"):
            if country in qCountry:
                return countryEntry['region']
    return ""


def loadDiseaseList():
    global dfDiseaseList
    fDL = open(gDiseaseListFile, "r")
    dfDiseaseList = fDL.read().splitlines()
    logging.info("--loaded <" + str(len(dfDiseaseList)) + "> diseases")


def loadCountryData():
    global dfCountryData
    dfCountryData = pd.read_csv(gCountryDataFile, sep="\t")
    dfCountryData['country'] = dfCountryData['country'].str.rstrip()
    dfCountryData['subregion'] = dfCountryData['subregion'].str.rstrip()
    dfCountryData['region'] = dfCountryData['region'].str.rstrip()

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg


def parseArgs(argv):
    '''parse out Command line options.'''

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    #program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s
    i
      Created by Simon Rayner on %s.
      Copyright 2022 Oslo University Hospital. All rights reserved.
    
      Licensed under the Apache License 2.0
      http://www.apache.org/licenses/LICENSE-2.0
    
      Distributed on an "AS IS" basis without warranties
      or conditions of any kind, either express or implied.
    
    USAGE
    ''' % (program_name, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-d", "--disease_list_file", dest="diseaselistfile", action="store", help="list of diseases with entrez results [default: %(default)s]")
        parser.add_argument("-y", "--split_year", dest="splityear", action="store", help="split data on this year [default: %(default)s]")
        parser.add_argument("-r", "--resolution", dest="plotresolutiondpi", action="store", help="resolution for generated plots [default: %(default)s]")
        parser.add_argument("-f", "--plot_format", dest="plotformat", action="store", help="output format for plots (tiff vs jpg ..) [default: %(default)s]")
        parser.add_argument("-c", "--country_data_file", dest="countrydatafile", action="store", help="country data file [default: %(default)s]")

        # Process arguments
        args = parser.parse_args()

        global gDiseaseListFile
        gDiseaseListFile = args.diseaselistfile
        global gSplitYear
        gSplitYear = args.splityear
        global gPlotResolutionDPI
        gPlotResolutionDPI = args.plotresolutiondpi
        global gOutputPlotFormat
        gOutputPlotFormat = args.plotformat
        global gCountryDataFile
        gCountryDataFile = args.countrydatafile



        logging.info("disease list file is <" + gDiseaseListFile + ">")
        logging.info("split year is <" + gSplitYear + ">")
        logging.info("plot output format is <" + gOutputPlotFormat + ">")
        logging.info("plot resolution is <" + str(gPlotResolutionDPI) + "> dpi")

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception as e:
        print(e)
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2


def initLogger(md5string):

    ''' setup log file based on project name'''
    projectBaseName = os.path.basename(gDiseaseListFile).split(".")[0]
    now = datetime.now()
    dt_string = now.strftime("%Y%m%d_%H%M%S")
    logFolder = os.path.join(os.path.dirname(gDiseaseListFile), "logfiles")
    if not os.path.exists(logFolder):
        print("--log folder <" + logFolder + "> doesn't exist, creating")
        os.makedirs(logFolder)
    logfileName = os.path.join(logFolder, projectBaseName + "__" + dt_string + "__" + md5string +".log")
    handler = logging.StreamHandler(sys.stdout)
    logging.basicConfig(level=logging.INFO)

    fileh = logging.FileHandler(logfileName, 'a')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fileh.setFormatter(formatter)

    log = logging.getLogger() # root logger
    log.setLevel(logging.INFO)
    for hdlr in log.handlers[:]:  # remove all old handlers
        log.removeHandler(hdlr)
    log.addHandler(fileh)      # set the new handler
    log.addHandler(handler)
    logging.info("+" + "*"*78 + "+")
    logging.info("project log file is <" + logfileName + ">")
    logging.info("+" + "*"*78 + "+")
    logging.debug("debug mode is on")


def main(argv=None): # IGNORE:C0111

    setlocale(LC_NUMERIC, 'no_NO')
    if argv is None:
        argv = sys.argv

    md5String = hashlib.md5(b"CBGAMGOUS").hexdigest()
    parseArgs(argv)
    initLogger(md5String)

    loadDiseaseList()
    loadCountryData()
    plotIFsbyLocation()


if __name__ == '__main__':

    if DEBUG:
        pass
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        #profile_filename = 'fairpype.virusPipe_profile.txt'
        #cProfile.run('main()', profile_filename)
        #statsfile = open("profile_stats.txt", "wb")
        #p = pstats.Stats(profile_filename, stream=statsfile)
        #stats = p.strip_dirs().sort_stats('cumulative')
        #stats.print_stats()
        #statsfile.close()
        #sys.exit(0)

    sys.exit(main())







