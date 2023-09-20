import pandas as pd
from datetime import datetime
import pandas_datareader as pdr
import requests
from bs4 import BeautifulSoup
import re



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


def get_fomc_data_fraser(decades:list = [1980, 1990, 2000, 2010, 2020]) -> pd.DataFrame:
    """
    Retrieves historical FOMC meeting dates and their corresponding statuses ('Scheduled', 'Unscheduled', 'Cancelled', 'Notation Vote') 
    from the FRASER database (https://fraser.stlouisfed.org/title/federal-open-market-committee-meeting-minutes-transcripts-documents-677).

    :param decades: (list) A list of integers representing decades, e.g., [1980, 1990, 2000, 2010, 2020].
    :return: (pd.DataFrame) A DataFrame indexed by 'FOMCDate', containing 'Status' and 'Days' columns.
    """
    
    def extract_last_day(match):
        month_name, day1, day2, year = match.groups()
        if day2:
            last_day = datetime(int(year), datetime.strptime(month_name, '%B').month, int(day2))
        else:
            last_day = datetime(int(year), datetime.strptime(month_name, '%B').month, int(day1))
        return last_day.strftime('%Y-%m-%d')

    def clean_decade_list_fraser(raw_list):
        extracted_dates = []
        extracted_texts = []

        date_pattern = re.compile(r'([A-Za-z]+) (\d+)(?:-(\d+))?, (\d{4})')

        for item in raw_list:
            date_match = date_pattern.search(item)
            text_match = re.search(r'\((.*?)\)', item)

            if date_match:
                extracted_date = extract_last_day(date_match)
                extracted_dates.append(extracted_date)
            else:
                extracted_dates.append('')

            if text_match:
                extracted_texts.append(text_match.group(1))
            else:
                extracted_texts.append('Scheduled')

        info_list = [item.replace('Meeting,', '') for item in raw_list]

        cleaned_df = pd.DataFrame({'FOMCDate': extracted_dates, 'Status': extracted_texts, 'Days': info_list}).set_index('FOMCDate')

        return cleaned_df

    fomc_meetings_df = pd.DataFrame()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    for decade in decades:
        url = f'https://fraser.stlouisfed.org/title/federal-open-market-committee-meeting-minutes-transcripts-documents-677?browse={decade}s'
        r = requests.get(url, headers=headers)
        
        if r.status_code == 200:
            html_content = r.text
        else:
            raise ValueError(f"Failed to retrieve data for {decade}s from FRASER database. Status code: {r.status_code}")

        soup = BeautifulSoup(html_content, 'html.parser')
        meeting_data = soup.find('div', class_='browse-by-list list')
        decades_data = meeting_data.find_all('ul')
        
        meetings = []
        for data in decades_data:
            decade_events = data.find_all('li') 
            decade_meetings = [event.get_text(strip=True) for event in decade_events]
            meetings += decade_meetings

        meetings = [item for item in meetings if not re.match(r'\d{4}s', item)]
        meetings = [item for item in meetings if item.startswith("Meeting")]
        decade_df = clean_decade_list_fraser(meetings)

        fomc_meetings_df = pd.concat([fomc_meetings_df, decade_df])

    return fomc_meetings_df



def get_fomc_data_fed() -> pd.DataFrame:
    """
    Retrieves historical FOMC meeting dates and their corresponding statuses ('Scheduled', 'Unscheduled', 'Cancelled', 'Notation Vote') 
    from the Federal Reserve Website (https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm).

    :return: (pd.DataFrame) A DataFrame indexed by 'FOMCDate', containing 'Status' and 'Days' columns.
    """
    
    def clean_year_table(table: BeautifulSoup) -> pd.DataFrame:
        """
        Extracts data from the year table in the FOMC calendar of the Federal Reserve website
        (https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) and returns it as a DataFrame.

        :param table: BeautifulSoup object representing the year table.
        :return: pd.DataFrame with columns 'Status' and 'Days', indexed by 'FOMCDate'.
        """

        # Extract year, months, and days of meetings
        year_txt = table.find('h4').text
        year = re.findall(r'\d+', year_txt)[0]

        month_elements = table.find_all('div', class_='fomc-meeting__month')
        month = [item.text.replace('/', ' - ') for item in month_elements]

        day_elements = table.find_all('div', class_='fomc-meeting__date')
        day = [item.text.replace('*', '') for item in day_elements]

        # Replace abbreviated month names
        month_mapping = {
            'Jan': 'January',
            'Feb': 'February',
            'Mar': 'March',
            'Apr': 'April',
            'May': 'May',
            'Jun': 'June',
            'Jul': 'July',
            'Aug': 'August',
            'Sep': 'September',
            'Oct': 'October',
            'Nov': 'November',
            'Dec': 'December'
        }

        # Define a regular expression pattern to match month abbreviations
        pattern = re.compile(r'\b(' + '|'.join(re.escape(key) for key in month_mapping.keys()) + r')\b')

        # Helper function
        def replace_month(match):
            return month_mapping[match.group(0)]

        month = [pattern.sub(replace_month, mn) for mn in month]

        # Extract status of meetings and update day
        status = []
        updated_day = []

        for item in day:
            match = re.search(r'\((.*?)\)', item)
            if match:
                status.append(match.group(1))
                updated_day.append(re.sub(r'\(.*\)', '', item))
            else:
                status.append('Scheduled')
                updated_day.append(item)

        replacements = {
            "notation vote": "Notation Vote",
            "unscheduled": "Unscheduled",
            "cancelled": "Cancelled",
        }

        status = [replacements.get(s.lower(), s) for s in status]
        day = [item.strip() for item in updated_day]

        # Generate lists for creating a DataFrame
        days = []
        fomc_date = []

        for m, d in zip(month, day):
            if '-' in m:
                # If there are two months separated by a hyphen in the month list
                month1, month2 = m.split('-')
                day1, day2 = d.split('-')
                days.append(f'{month1} {day1} - {month2} {day2}, {year}')
                fomc_date_obj = datetime.strptime(f'{month2} {day2}, {year}'.strip(), "%B %d, %Y")
                fomc_date.append(fomc_date_obj.strftime("%Y-%m-%d"))
            else:
                days.append(f'{m} {d}, {year}')
                d = d.split('-')[1] if len(d.split('-')) == 2 else d.split('-')[0]
                fomc_date_obj = datetime.strptime(f'{m} {d}, {year}'.strip(), "%B %d, %Y")
                fomc_date.append(fomc_date_obj.strftime("%Y-%m-%d"))

        # Create a DataFrame and return it
        year_df = pd.DataFrame({'FOMCDate': fomc_date, 'Status': status, 'Days': days}).set_index('FOMCDate')

        return year_df


    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    url = f'https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm'
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        html_content = r.text
    else:
        raise ValueError(f"Failed to retrieve data from Fed Website. Status code: {r.status_code}")
    soup = BeautifulSoup(html_content, 'html.parser')
    years_tbl = soup.find_all('div', class_='panel panel-default')

    fomc_meetings_df = pd.DataFrame()
    for table in years_tbl:
        year_df = clean_year_table(table)
        fomc_meetings_df = pd.concat([fomc_meetings_df, year_df])
    fomc_meetings_df.sort_index(inplace=True) 
    
    return fomc_meetings_df



def get_fomc_data() -> pd.DataFrame:
    """
    Retrieves historical FOMC meeting dates and their corresponding statuses ('Scheduled', 'Unscheduled', 'Cancelled', 'Notation Vote') 
    from the Fraser database and Federal Reserve website and combines them into a DataFrame. 
    
    Note: The Fraser database does not include upcoming meetings data while the Federal Reserve does.

    :return: (pd.DataFrame) A DataFrame indexed by 'FOMCDate', containing 'Status' and 'Days' columns.
    """
    # Get historical FOMC data from the Federal Reserve Website
    df_fed = get_fomc_data_fed()
    
    # Get historical FOMC data from the Fraser Database
    df_fraser = get_fomc_data_fraser()
    
    # Combine the two DataFrames, keeping rows from the Federal Reserve data for duplicate indexes
    result = df_fraser.combine_first(df_fed)
    
    return result
