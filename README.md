# Covid-19 Dashboard Webapp

A dashboard that displays location-based COVID-19 data and related news articles, with updates that can be scheduled by the user. It was written in Python using the Flask module and uses the News API and Public Health England APIs to retrieve location-based COVID-19 data and COVID-19 related news articles. I developed this program as part of a programming module for my studies at the University of Exeter.

This project can be found at https://github.com/alexcairns02/covid-dashboard.

## Installation

Make sure you have Python 3.9.9 installed. You will also need to make sure the ```uk_covid19``` and ```flask``` libraries are installed before running:

```bash
pip install uk_covid19
```
```bash
pip install flask
```

You will need to create an API key for [News API](https://newsapi.org/)

Add your API key to config.json under ```"APIKey"``` and change the location data to suit your interest. The config file should look something like this:

```json
{
    "APIKey": "c49hgksncu79hn5krbjif445itm85",
    "Location": "Exeter",
    "LocationType": "ltla",
    "Nation": "England"
}
```

## Usage

Run main.&#65279;py by navigating to this folder in the terminal and entering the command:

```bash
python main.py
``` 

After running, access the webapp in your browser at http://127.0.0.1:5000/index.

The dashboard should display local cases, national cases, hospitalisations and total national deaths. It should also have a list of relevant news articles on the right hand side. Articles can be removed from the list by clicking their close [x] button. Under the COVID-19 data should be a form that can be used to schedule updates by entering a time (hour:minute) and update name and selecting whether to update the COVID-19 data or news articles (or both). The user can also set the update to repeat daily at the given time. After submitting, the update should appear as part of a list of scheduled updates on the left hand side of the screen.

## Testing

To test the code: install pytest, nagivate to this folder in your terminal, and then enter the command ```pytest```.

```bash
pip install pytest
```

The program comes with a log file, pysys.log. This file logs events that occur within the program, such as update scheduling and articles being removed. It also logs errors that occur without the program halting.

## Authors

Python written by Alexander Cairns

HTML template written by Matt Collison

Tests written by Matt Collison and Alexander Cairns