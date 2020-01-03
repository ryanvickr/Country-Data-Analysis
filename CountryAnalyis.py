# Created By: Ryan Vickramasinghe

import pandas as pd
import numpy as np

def cleanEnergyData(energy):
    # remove garbage columns
    energy.drop(['Unnamed: 0', 'Unnamed: 1'], axis = 1, inplace = True)
    # update columns
    energy.columns = ['Country', 'Energy Supply', 'Energy Supply per Capita', '% Renewable']
    # remove numerical values
    energy['Country'] = energy['Country'].str.replace('\d+', '')
    # remove parentheses
    energy['Country'] = energy['Country'].str.replace(r"\(.*\)","").str.strip()
     # replace missing data with NaN
    energy = energy.replace('...', np.NaN)
    # fix country names
    energy['Country'] = energy['Country'].replace('Republic of Korea', 'South Korea')
    energy['Country'] = energy['Country'].replace('United States of America', 'United States')
    energy['Country'] = energy['Country'].replace('United Kingdom of Great Britain and Northern Ireland', 'United Kingdom')
    energy['Country'] = energy['Country'].replace('China, Hong Kong Special Administrative Region', 'Hong Kong')
    # convert pentajoules to gigajoules
    energy['Energy Supply'] = energy['Energy Supply']*1000000

    return energy

def cleanGDPData(GDP):
    GDP['Country Name'] = GDP['Country Name'].replace('Korea, Rep.', 'South Korea')
    GDP['Country Name'] = GDP['Country Name'].replace('Iran, Islamic Rep.', 'Iran')
    GDP['Country Name'] = GDP['Country Name'].replace('Hong Kong SAR, China', 'Hong Kong')

    return GDP

# Cleans all data, merges 3 files, and only includes the top 15 countries by Scimago rank
def cleanAndMergeTop15():
    # import energy data (remove header/footer)
    energy = pd.read_excel('Energy Indicators.xls', skiprows=17, skipfooter=38)
    energy = cleanEnergyData(energy)

    # import world bank data
    GDP = pd.read_csv('world_bank.csv', skiprows=4)
    GDP = cleanGDPData(GDP)

    # import Sciamgo rank data
    ScimEn = pd.read_excel('scimagojr-3.xlsx')

    # prepare GDP data for merging (set index)
    GDPValidYears = GDP[['Country Name', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015']]

    # prepare Scimago data for merging (set rank, index)
    ScimEnValidData = ScimEn.where(ScimEn['Rank'] < 16).dropna()
    ScimEnValidData['Rank'] = ScimEnValidData['Rank'].astype(int)

    # merge Scimago rank data with energy data
    mergeScimEn_Energy = pd.merge(ScimEnValidData, energy, how='left', on='Country')

    # merge above with GDP data
    result = pd.merge(mergeScimEn_Energy, GDPValidYears, how='left', left_on='Country', right_on='Country Name')
    result.drop('Country Name', axis=1,inplace=True)
    result.set_index('Country', inplace=True)

    return result

# return a dataframe containing top 15 countries, and and average gdp from the last 10 years (2006-2015)
def averageGDP(top15):
    avgGDP = top15.copy()
    avgGDP['avgGDP'] = avgGDP[['2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015']].mean(axis=1)

    return avgGDP['avgGDP'].sort_values(0, ascending=False)


# get the merged and cleaned data:
result = cleanAndMergeTop15()

print(result)
result.to_csv('output.csv', sep=',')

# get the average gdp over the last 10 years
avgGDP = averageGDP(result)
print('\n--------------\n')
print(avgGDP)
avgGDP.to_csv('avgGDP.csv', sep=',', header='True')