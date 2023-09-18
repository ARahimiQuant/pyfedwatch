import pandas as pd
from datetime import datetime
import pandas_datareader as pdr



def read_fomc_data(path: str) -> pd.DataFrame:
    """
    Reads FOMC meetings data from an Excel file located at the given path. Such a file is provided 
    in the "data/fomc" folder of the pyfedwatch repository. This function is used to retrieve FOMC 
    meeting dates for the pyfedwatch algorithm, but you can provide your own dates using your own 
    function and data sources.

    :param path: (str) Path to the directory containing the FOMC meetings data in Excel format.
    
    :return: (pd.DataFrame) A DataFrame containing FOMC meeting dates. Other columns are not utilized by the algorithm.
    """
    return pd.read_excel(f'{path}/fomc_data.xlsx')



def read_price_history(symbol: str, path: str) -> pd.DataFrame:
    """
    Reads and returns pricing data for Fed Funds futures contracts from an Excel file located at the specified path.
    Pricing data file names for contracts must adhere to the CME Globex code format, which is 'ZQ+MonthCode+YY'. Such 
    files are available in the 'data/contracts' folder of the pyfedwatch repository.
    
    This function is provided for demonstration purposes, and you have the flexibility to use your own function and data
    source (e.g., an API or database) to supply up-to-date pricing data to the pyfedwatch algorithm, as the data available 
    in the repository may not be regularly updated.
    
    :param symbol: (str) Symbol of the Fed Funds futures contract as Globex code, i.e. 'ZQ+MonthCode+YY', e.g., 'ZQH23' for March 2023.
    :param path: (str) The path to the directory containing historical prices of the contracts in the form of Excel files.
    
    :return: (pd.DataFrame) A DataFrame containing OHLCV, open interest, and contract symbol columns, with the Date index.
    """
    return pd.read_excel(f'{path}/{symbol}.xlsx', index_col=0)



def get_fedfunds_range() -> pd.DataFrame:
    """
    Retrieve and return the historical Federal Funds target rate lower (LL) and upper limits (UL) from the FRED database.

    Before December 16, 2008, the Federal Reserve used a single target rate without distinct lower and upper limits. Therefore,
    for dates prior to that, both the lower and upper limits in the output DataFrame will be equal. However, after that date,
    the lower and upper limits are distinct.

    :return: (pd.DataFrame) A DataFrame indexed by date containing historical Federal Funds target rate lower (LL) and upper limits (UL).
    """
    # Find current date
    current_date = datetime.now()

    try:
        # Get fed funds target rate lower and upper limits, for dates after 2008-12-16
        ff_ll = pdr.DataReader('DFEDTARL','fred',start=datetime(1960,1,1),end=current_date)
        ff_ul = pdr.DataReader('DFEDTARU','fred',start=datetime(1960,1,1),end=current_date)

        # Get target rate for dates before 2008-12-16, from "https://fred.stlouisfed.org/series/DFEDTAR", 
        ff_tgt = pdr.DataReader('DFEDTAR','fred',start=datetime(1960,1,1),end=current_date)
    
    except Exception as e:
        raise Exception(f"Error fetching data from FRED: {e}")

    # Concat rate limits and target rate dataframes
    ff_range = pd.concat([ff_ll, ff_ul, ff_tgt], axis=1)

    # Fill lower/upper limits with target rates for dates before 2008-12-16 
    ff_range['DFEDTARL'].fillna(ff_range['DFEDTAR'], inplace=True)
    ff_range['DFEDTARU'].fillna(ff_range['DFEDTAR'], inplace=True)

    # Drop target rate column, DFEDTAR, cahnge the name of index and columns
    ff_range.drop('DFEDTAR', axis=1, inplace=True)
    ff_range.index.name = 'Date'
    ff_range.columns = ['LL','UL']
    
    return ff_range