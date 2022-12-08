import numpy as np
import pandas as pd
import requests
import math
from scipy import stats #for percentile score calculation
import xlsxwriter

stocks = pd.read_csv('sp_500_stocks.csv')
from secrets import IEX_CLOUD_API_TOKEN #you have to download the file containing api token which should not get push to the github

#We are making an api call here
symbol = 'AAPL'
api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/stats?token={IEX_CLOUD_API_TOKEN}' #gave us 400 because we didnt input ?token={IEX_CLOUD_API_TOKEN}
data = requests.get(api_url).json()
stocks = stocks[~stocks['Ticker'].isin(['DISCA', 'HFC','VIAC','WLTW'])] #some of the stocks have been delisted by the API hence we use this to filter out the stock.
#print(data) #checking whether the api call succeeds or not

print(data['year1ChangePercent']) #finding 1 year change of apple stock using the api get request


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


symbol_groups = list(chunks(stocks['Ticker'], 100)) #we use the chunk function to divide the symbol group into 100.
symbol_strings = [] #then we create an empty list called symbol string
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i])) #every 100 stocks in the symbol group list we create a comma seperated list of string
#     print(symbol_strings[i])

#for symbol_string in symbol_strings:
    #print(symbol_string)
my_columns = ['Ticker', 'Price', 'One-Year Price Return', 'Number of Shares to Buy'] #column name of the dataframe

final_dataframe = pd.DataFrame(columns = my_columns) #creation of dataframe columns

for symbol_string in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=price,stats&token={IEX_CLOUD_API_TOKEN}' #we wanna change it to sandbox url. we are looking at price and token endpoint
    data = requests.get(batch_api_call_url).json() #convert the data into json format
    #print(symbol_string.split(','))
    #print(data['AAPL']['stats'])
    for symbol in symbol_string.split(","):  #for every ticker in this list, we want to append the releevant metricts to the final dataframe
            final_dataframe = final_dataframe.append(
            pd.Series(
               [
                   symbol,
                   data[symbol]['price'], #if we wrote the code to here we are going to have an error because the dataframe is expecting 4
                   data[symbol]['stats']['year1ChangePercent'],                  #4 value and we are only getting two value.
                   'N/A'



               ],
               index = my_columns),
                   ignore_index = True

        )
#print(final_dataframe)

final_dataframe.sort_values('One-Year Price Return', ascending = False, inplace = True) #sort the dataframe with "one year price return according to asecnding order so that highest momemtum stock will be on top
# with the inplace method it will modify the original dataframe instead of giving us a temporary copy.
final_dataframe = final_dataframe[:50] #modify the dataframe so it only contains 50 stocks with the highest momentum
final_dataframe.reset_index(inplace = True)  #change the index so that it runs from 0-49
#print(final_dataframe) #then we finally print out the final dataframe

def portfolio_input():
    global portfolio_size
    portfolio_size = input('Enter the size of your portfolio:')

    try:
        float(portfolio_size)
    except ValueError:
        print('That is not a number! \nPLeasetry again:')
        portfolio_size = input('Enter the size of your portfolio:')

portfolio_input()
print(portfolio_size)


position_size = float(portfolio_size)/len(final_dataframe.index)
for i in range(0, len(final_dataframe)):
    final_dataframe.loc[i, 'Number of Shares to Buy '] = math.floor(position_size/final_dataframe.loc[i, 'Price'])

#print(final_dataframe)

hqm_columns = [
    'Ticker',
    'Price',
    'Number of Shares to Buy',
    'One-Year price Return',
    'One-Year Return Percentile',
    'Six-Month Price Return',
    'Six-Month Return Percentile',
    'Three-Month Price Return',
    'Three-Month Return Percentile',
    'One-Month Price Return',
    'One-Month Return Percentile'

]
hqm_dataframe = pd.DataFrame(columns = hqm_columns)
for symbol_string in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=price,stats&token={IEX_CLOUD_API_TOKEN}'  # we wanna change it to sandbox url. we are looking at price and token endpoint
    data = requests.get(batch_api_call_url).json()  # convert the data into json format
    for symbol in symbol_string.split(','):
        hqm_dataframe = hqm_dataframe.append(
            pd.Series(
            [
                symbol,
                data[symbol]['price'],
                'N/A',
                data[symbol]['stats']['year1ChangePercent'],
                'N/A',
                data[symbol]['stats']['month6ChangePercent'],
                'N/A',
                data[symbol]['stats']['month3ChangePercent'],
                'N/A',
                 data[symbol]['stats']['month1ChangePercent'],
                'N/A'
            ],
            index = hqm_columns),
            ignore_index = True
        )

#print(hqm_dataframe)


