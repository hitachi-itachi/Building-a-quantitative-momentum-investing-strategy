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
print(final_dataframe)

