# Covid-19 Dashboard Webapp

A dashboard that displays location-based COVID-19 data and related news articles, with updates that can be scheduled by the user. It was written in Python using the Flask module and uses the News API and Public Health England APIs to retrieve location-based COVID-19 data and COVID-19 related news articles. I developed this program as part of a programming module for my studies at the University of Exeter.

## Installation

You will need to make sure the ```uk_covid19``` and ```flask``` libraries are installed before running:

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

After running, access the webapp in your browser at http://127.0.0.1:5000/index