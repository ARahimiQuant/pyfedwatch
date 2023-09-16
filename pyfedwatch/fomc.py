import pandas as pd
import math

import matplotlib
import matplotlib.patches as patches
import matplotlib.pyplot as plt

from datetime import datetime
from calendar import monthrange
from dateutil.relativedelta import relativedelta
import holidays

class FOMC():
    
    def __init__(self, watch_date, fomc_dates, num_upcoming):
        
        # Check and initialize the calculation date
        if isinstance(watch_date, str):
            self.watch_date = datetime.strptime(watch_date, '%Y-%m-%d')
        elif isinstance(watch_date, datetime):
            self.watch_date = watch_date
        else:
            raise ValueError("Invalid format for watch_date. It should be a string in 'yyyy-mm-dd' format or a datetime object.")
        
        # Check and initialize FOMC dates list
        if all(isinstance(date, datetime) for date in fomc_dates):
            self.fomc_dates = fomc_dates
        elif all(isinstance(date, str) for date in fomc_dates):
            self.fomc_dates = [datetime.strptime(date, '%Y-%m-%d') for date in fomc_dates]
        else:
            raise ValueError("Invalid format for fomc_dates. It should be a list of datetime objects or a list of strings in 'yyyy-mm-dd' format.")
        
        # Sort fomc_dates list in ascending order
        self.fomc_dates = sorted(self.fomc_dates)
        
        # Initialize the requested number of upcoming FOMC meetings
        self.num_upcoming = num_upcoming
        
        # Initialize lists
        self.month_list = self.generate_month_list()
        self.contract_list = self.generate_contract_list()
        self.meeting_list = self.generate_meeting_list()
        self.order_list = self.generate_order_list()
        
        # sort fomc_dates
        self.summary = pd.DataFrame({'Contract': self.contract_list,
                                    'Meeting': self.meeting_list,
                                    'Order': self.order_list}, 
                                    index=self.month_list).rename_axis('YYYY-MM')
        
    
    def starting_no_fomc_month(self) -> tuple[int, int]:
        """
        Finds the first past month without an FOMC meeting. 

        :return: (tuple[int, int]) A tuple containing the year and month of the target month.
        """
        
        # Format FOMC date to YYYY-MM to avoid confusion with day numbers
        fomc_dates_formatted = [date.strftime('%Y-%m') for date in self.fomc_dates if date.strftime('%Y-%m') <= self.watch_date.strftime('%Y-%m')]
        
        target_month = self.watch_date
        starting_no_fomc = None
        
        while target_month.strftime('%Y-%m') >= fomc_dates_formatted[0]:
            if target_month.strftime('%Y-%m') not in fomc_dates_formatted:
                starting_no_fomc = target_month
                break;
            else:
                target_month = target_month - relativedelta(months=1)
        
        if starting_no_fomc == None:
            message = 'Starting No-FOMC Month not found! There might be an issue with the provided list of scheduled FOMC meetings.'
            raise ValueError(message)
                
        return starting_no_fomc.year, starting_no_fomc.month
                
    
    def ending_no_fomc_month(self) -> tuple[int, int]:
        """
        Finds the first upcoming month witout FOMC meeting, after the requested number of FOMC meetings.
        If calculation date to be in a month with FOMC meeting, does not count that month if that month's meeting is held. 
        
        :return: (Tuple[int, int]) A tuple containing the year and month of the target month.
        """
        
        fomc_dates_formatted = [date.strftime('%Y-%m') for date in self.fomc_dates if date >= self.watch_date]
        
        target_month = self.watch_date  
        ending_no_fomc = None      
        
        fomc_counter = 0
        while target_month.strftime('%Y-%m') <= fomc_dates_formatted[-1]:
            if target_month.strftime('%Y-%m') in fomc_dates_formatted:
                fomc_counter += 1
            else:
                ending_no_fomc = target_month
                if fomc_counter >= self.num_upcoming:
                    break;
                
            target_month = target_month + relativedelta(months=1)
        
        if fomc_counter < self.num_upcoming:
            message = f'Number of FOMC meetings taken into account is {fomc_counter}, for {self.num_upcoming} meetings, extend the list of scheduled FOMC meetings!'
            raise ValueError(message)
        
        if ending_no_fomc == None:
            message = 'Ending No-FOMC Month not found! There might be an issue with the provided list of scheduled FOMC meetings.'
            raise ValueError(message)
            
        return ending_no_fomc.year, ending_no_fomc.month
    
    
    def generate_month_list(self):
        """
        Generates a list of months in the YYYY-MM format, which corresponds to the months 
        for which futures contracts are required for FedWatch algorithm calculations.

        Before using this method, make sure to call "starting_no_fomc_month()" and "ending_no_fomc_month()" 
        to find the start and end month.

        :return: (list of str) A list of months in YYYY-MM format.
        """
        
        start_month = self.starting_no_fomc_month()
        end_month = self.ending_no_fomc_month()
        
        month_list = pd.date_range(start = f"{start_month[0]}-{start_month[1]:02d}", 
                                    end = f"{end_month[0]}-{end_month[1]:02d}", 
                                    freq='MS')
        
        month_list = [date.strftime('%Y-%m') for date in month_list]
    
        return month_list
    
    def generate_contract_list(self):
        """
        Generates a list of Fed Funds futures contract symbols according to the CME naming convention, 
        which are required for FedWatch algorithm calculations

        :return: (list of str) CME fed funds futures contratcs symbols.
        """
        
        # Generate CME fed funds futures contracts month code
        cme_month_codes = {
            1: 'F', 2: 'G', 3: 'H', 4: 'J', 5: 'K', 6: 'M',
            7: 'N', 8: 'Q', 9: 'U', 10: 'V', 11: 'X', 12: 'Z'
        }
        
        # Separate year and month from the month list
        year_month = [date.split('-') for date in self.month_list]

        # Create a list of contracts
        contract_list = ['ZQ' + cme_month_codes[int(month)] + year[-2:] for year, month in year_month]
        
        return contract_list
    
    def generate_meeting_list(self):
        """
        Generates a list of FOMC meeting dates according to the month list, 
        which includes meeting date in YYYY-MM-DD string format for month
        with FOMC meeting and "No FOMC" for months without meeting.

        :return: (list of str) FOMC meeting date in YYYY-MM-DD format or "No FOMC".
        """
        
        # Create a new list based on original_dates
        fomc_meetings = []

        for date in self.month_list:
            year_month = date.split('-')
            matching_dates = [f"{date.strftime('%Y-%m-%d')}" for date in self.fomc_dates if date.year == int(year_month[0]) and date.month == int(year_month[1])]
            
            if matching_dates:
                fomc_meetings.append(matching_dates[0])
            else:
                fomc_meetings.append('No FOMC')
                
        return fomc_meetings
    
    
    def generate_order_list(self):
        """
        Generates a list of FOMC meeting orders based on the month list and watch_date. 
        For months with FOMC meetings, the integers represent the number of upcoming or past meetings relative to watch_date.

        :return: (list of int) 0 for months without FOMC meetings and integers for months with FOMC meetings.
        """
        # Extract year and month from the calculation date
        calc_yr, calc_mn = self.watch_date.year, self.watch_date.month
        
        # Find the month index of calculation date in month_list
        idx = next((i for i, month in enumerate(self.month_list) if month == f"{calc_yr}-{calc_mn:02d}"), None)
        
        # Create upcoming and past meetings list
        if self.meeting_list[idx] == 'No FOMC' or datetime.strptime(self.meeting_list[idx], '%Y-%m-%d') <= self.watch_date:
            fomc_list_bwd = self.meeting_list[:idx+1]
            fomc_list_bwd.reverse()
            fomc_list_fwd = self.meeting_list[idx+1:]
        else:
            fomc_list_bwd = self.meeting_list[:idx]
            fomc_list_bwd.reverse()
            fomc_list_fwd = self.meeting_list[idx:]
            
        # Create fomc upcoming meetings order list
        fomc_order_fwd = []
        meeting_counter = 1
        for date in fomc_list_fwd:
            if date == 'No FOMC':
                fomc_order_fwd.append(0)
            else:
                fomc_order_fwd.append(meeting_counter)
                meeting_counter += 1
                
        # Create fomc past meetings order list
        fomc_order_bwd = []
        meeting_counter = -1
        for date in fomc_list_bwd:
            if date == 'No FOMC':
                fomc_order_bwd.append(0)
            else:
                fomc_order_bwd.append(meeting_counter)
                meeting_counter -= 1
        fomc_order_bwd.reverse()  
        
        return fomc_order_bwd + fomc_order_fwd
    
    def plot_fomc_calendar(self):
        """
        Plots a calendar that includes months for which their relevant fed funds futures contract data are required for FedWatch calculations.
        Highlights the calculation day and FOMC meetings on the calendar.

        :return: (matplotlib figure) Matplotlib figure of the calendar.
        """
        # internal ploting function - label_month
        def label_month(year, month, ax, i, j, cl="black"):
            months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
            mn_code = ['F','G','H','J','K','M','N','Q','U','V','X','Z']
            month_label = f"{months[month-1]} {year} - ZQ{mn_code[month-1]}{str(year)[-2:]}"
            ax.text(i, j, month_label, color=cl, va="center", fontsize=11)
            
        # internal ploting function - label_weekday
        def label_weekday(ax, i, j, cl="black"):
            x_offset_rate = 1
            for weekday in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
                ax.text(i, j, weekday, ha="center", va="center", color=cl)
                i += x_offset_rate

        # internal ploting function - label_day
        def label_day(ax, day, i, j, cl="black"):
            ax.text(i, j, int(day), ha="center", va="center", color=cl)

        # internal ploting function - check_color_day
        def check_color_day(year, month, day, weekday):
            if (year, month, day) in holiday_list:
                return "red"     # holidays
            if weekday == 6:     # Sunday
                return "red"
            if weekday == 5:     # Saturday
                return "red"
            return "black"
    
        # internal ploting function - check_fill_day
        def check_fill_day(year, month, day, weekday):
            if (year, month, day) in fillday_list:
                return True
            
        # internal ploting function - check_calc_day
        def check_calc_day(year, month, day, weekday):
            if (year, month, day) == (self.watch_date.year, self.watch_date.month, self.watch_date.day):
                return True
    
        # internal ploting function - fill_box
        def fill_box(ax, i, j, edgecolor , facecolor):
            ax.add_patch(
                patches.Rectangle(
                    (i - 0.5, j - 0.5),
                    1,
                    1,
                    edgecolor=edgecolor,
                    facecolor=facecolor,
                    alpha=0.3,
                    fill=True,
                )
            )
            
        # internal ploting function - month_calendar
        def month_calendar(ax, year, month, fill):
            date = datetime(year, month, 1)
            weekday, num_days = monthrange(year, month)
            x_start = 1 - 0.5
            y_start = 5 + 0.5
            x_offset_rate = 1
            y_offset = -1
            label_month(year, month, ax, x_start, y_start + 2)
            label_weekday(ax, x_start, y_start + 1)
            j = y_start
            for day in range(1, num_days + 1):
                i = x_start + weekday * x_offset_rate
                color = check_color_day(year, month, day, weekday)
                if fill and check_fill_day(year, month, day, weekday):
                    fill_box(ax, i, j, "blue", "darkblue")
                if fill and check_calc_day(year, month, day, weekday):
                    fill_box(ax, i, j, "red", "darkred")
                label_day(ax, day, i, j, color)
                weekday = (weekday + 1) % 7
                if weekday == 0:
                    j += y_offset
        
        # FOMC meeting days as fill day list
        fillday_list = []
        for date_str in self.meeting_list:
            if date_str != 'No FOMC':
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                date_tuple = (date_obj.year, date_obj.month, date_obj.day)
                fillday_list.append(date_tuple)
        
        # Create holiday list 
        holiday_list = []

        years = [int(date_str.split("-")[0]) for date_str in self.month_list]
        us_holidays = holidays.US(years=years)

        for date, name in sorted(list(us_holidays.items())):
            holiday_list.append((date.year, date.month, date.day))
            
        # Initializing number of rows, columns and size of the calendar
        ncol = 4
        nrow = math.ceil(len(self.month_list)/4)
        figsize = (15, nrow*3)
        fig, axs = plt.subplots(figsize=figsize, nrows=nrow, ncols=ncol)
        
        # Set title of the plot
        watch_date_str = self.watch_date.strftime('%B %d, %Y')
        fig.suptitle(f"FOMC Calendar: on {watch_date_str} for {self.num_upcoming} Upcoming Meetings", 
                    fontsize=14, fontweight='bold', y=1.03)

        # Add a footnote to the plot
        plt.figtext(
            0.03, -0.01,
            r'$\bf{Note}$: The calendar includes the months for which corresponding Fed Funds Futures contracts pricing data ' 
            f'is required for FedWatch calculations. It starts with a no-FOMC month and continues for the requested \nnumber ' 
            f'of upcoming meetings, looking forward from the watch date, until another no-FOMC month. FOMC meeting days are ' 
            f'indicated with blue shaded boxes, and the red shaded box represents the watch day.',
            fontsize=10, horizontalalignment='left')

        fig.tight_layout();
        
        # Start populating the plot!
        ax_counter = 0
        for ax in axs.reshape(-1):
            # Create 7*7 grid for each subplot
            ax.axis([0, 7, 0, 7])
            ax.axis("on")
            ax.grid(True)
            
            # Hide x-axis ticks and lables for each subplot
            for tick in ax.xaxis.get_major_ticks():
                tick.tick1line.set_visible(False)
                tick.tick2line.set_visible(False)
                tick.label1.set_visible(False)
                tick.label2.set_visible(False)
                
            # Hide y-axis ticks and lables for each subplot
            for tick in ax.yaxis.get_major_ticks():
                tick.tick1line.set_visible(False)
                tick.tick2line.set_visible(False)
                tick.label1.set_visible(False)
                tick.label2.set_visible(False)
            
            # Hide subplot if it is not in the list of months, otherwise populate it
            if ax_counter >= len(self.month_list):
                ax.set_visible(False)
            else:
                date_obj = datetime.strptime(self.month_list[ax_counter], "%Y-%m")
                month_calendar(ax, year=date_obj.year, month=date_obj.month, fill=True)
            ax_counter += 1
               
        return fig