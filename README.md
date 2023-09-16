<div align="center">
   <a href="https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html">
   <img src="./images/cme_fedwatch.png" width="100%" 
   style="margin-left: auto; margin-right: auto; display:block;">
   
   </a>
  </br>
</div>

# Welcome to the Python Implementation of CME FedWatch Tool!

<div align="center">
    <br>
</div>

>This public repository exists solely to explain how the CME FedWatch tool calculates FOMC rate move probabilities.

<div align="center">
    <br>
</div>

## What is the CME FedWatch Tool?

CME FedWatch tool is provided by the Chicago Mercantile Exchange (CME) and is used to estimate the probabilities of Federal Open Market Committee (FOMC) rate moves. The FOMC meetings are where decisions about interest rates are made, and the CME FedWatch Tool helps market participants assess the likelihood of rate changes based on fed funds futures prices. If you are not familar with the tool, take a look at the tool's [demo video](https://www.cmegroup.com/education/videos/introduction-to-cme-fedwatch.html) and also the [CME FedWatch Webpage](https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html) to find out what is the likelihood that the Fed will change the Federal target rate at upcoming FOMC meetings, according to interest rate traders, in real time. You can also find the tools's methodology, which is briefly described [here](https://www.cmegroup.com/education/demos-and-tutorials/fed-funds-futures-probability-tree-calculator.html). 

## What is PyFedWatch?

PyFedWatch is a Python implementation of the CME FedWatch Tool. It is packaged to enable Python developers to access and utilize the functionality of the CME FedWatch Tool programmatically. PyFedWatch is designed to provide Python users with a way to estimate FOMC rate move probabilities using Python code. In summary, the CME FedWatch Tool is a financial tool offered by the CME, while PyFedWatch is a Python package that replicates similar functionality, allowing developers to work with FOMC rate move probabilities within the Python programming environment.

## PyFedWatch Scope

The scope of PyFedWatch is focused solely on the implementation of the FedWatch methodology. Providing the fed funds futures pricing data and FOMC meetings data is beyond the scope of this package. However, we have included sample data to demonstrate how the package can be used in practice. The package does not offer up-to-date data preparation as part of its functionality. PyFedWatch follows a methodology that differs slightly from the one described on the CME website but provides the same probabilities as the tool displayed on the website.

## PyfedWatch Outputs



<br>

> FOMC Calendar:
```
import pyfedwatch as fw

fomc = fw.fomc.FOMC(watch_date = '2023-03-10',
                    fomc_dates = fomc_dates,
                    num_upcoming = 9)
fig = fomc.plot_fomc_calendar()
```

<div align="center">
   <img src="./images/fomc_calendar.png" width="100%" 
   style="margin-left: auto; margin-right: auto; display:block;">
   
   </a>
  </br>
</div>

<br>

> Calculated probabilities of target rates for the upcoming 9 FOMC meetings with a watch date of March 10, 2023:
```
import pyfedwatch as fw


fedwatch = fw.fedwatch.FedWatch(
                        watch_date = '2023-03-10',
                        fomc_dates = fomc_dates,
                        num_upcoming = 9,
                        user_func = read_price_history,
                        path = '../data/contracts')

fedwatch.generate_hike_info(watch_date_rate=(4.5,4.75))
```

<div align="center">
   <img src="./images/rate_expectations.png" width="95%" 
   style="margin-left: auto; margin-right: auto; display:block;">
   
   </a>
  </br>
</div>

## Contact Information

You can contact me via email: a.rahimi.aut@gmail.com
