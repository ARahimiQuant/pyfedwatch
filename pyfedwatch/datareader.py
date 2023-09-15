import pandas as pd



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
