"""This module uses the Public Health England API to retrieve UK Covid-19 data.
It also contains methods for processing this data and scheduling updates."""

from os import error, path
import sched
import time
import json
import logging
from uk_covid19 import Cov19API, exceptions

THIS_FOLDER = path.dirname(path.abspath(__file__))

with open(path.join(THIS_FOLDER, "config.json"), "r", encoding="UTF-8") as config_file:
    config = json.load(config_file)

    #Takes user-based variables from the config file
    LOCATION = config["Location"]
    LOCATION_TYPE = config["LocationType"]
    NATION = config["Nation"]

scheduler = sched.scheduler(time.time, time.sleep)

logging.basicConfig(filename="pysys.log", level=logging.INFO)

#Stores location-based COVID-19 data
covid_data = {}
#Stores scheduled updates
updates = {}

def parse_csv_data(csv_filename:str) -> list:
    """Takes in a json file and outputs a list of each line of the file"""
    with open(csv_filename, "r", encoding="UTF-8") as file:
        #Forms a list of each line in the file
        data = file.read().split("\n")
        #Removes any empty lines at the end
        while data[-1] == "":
            data.pop()
        return data

def process_covid_csv_data(covid_csv_data:list) -> tuple:
    """Returns cases in last 7 days, current hospitalisations,
    and total deaths from parsed covid csv data"""

    if not covid_csv_data:
        logging.error("No csv data was inputted")
        return 0, 0, 0

    #Builds a 2D list of the csv data
    for i, row in enumerate(covid_csv_data):
        covid_csv_data[i] = row.split(",")

    #Adds up cases for data entries representing the last 7 days
    cases_last_7 = 0
    for i in range(3, 10):
        cases_last_7 += int(covid_csv_data[i][6])

    current_hospitalisations = int(covid_csv_data[1][5])

    total_deaths = 0
    #Finds the latest data entry with a death count
    i = 1
    while covid_csv_data[i][4] == "":
        i += 1
    total_deaths = int(covid_csv_data[i][4])

    return cases_last_7, current_hospitalisations, total_deaths


def process_covid_json_data(covid_json_data:list) -> tuple:
    """Returns cases in last 7 days, current hospitalisations,
    and total deaths from covid json data"""

    if not covid_json_data:
        logging.error("No json data was recieved")
        return 0, 0, 0

    #Adds up cases for data entries representing the last 7 days
    cases_last_7 = 0
    for i in range(3, 10):
        if covid_json_data[i]["newCases"] is not None:
            cases_last_7 += covid_json_data[i]["newCases"]

    hospital_cases = 0
    i = 1
    #Searches through data entries until it finds one with the latest hospital cases
    while hospital_cases == 0 and i < len(covid_json_data):
        hospital_cases = covid_json_data[i]["hospitalCases"]
        if hospital_cases is None:
            hospital_cases = 0
        else:
            hospital_cases = int(hospital_cases)
        i += 1

    #Searches through data entries until it finds one with the latest death count
    total_deaths = 0
    i = 1
    while total_deaths == 0 and i < len(covid_json_data):
        total_deaths = covid_json_data[i]["cumDeaths"]
        if total_deaths is None:
            total_deaths = 0
        else:
            total_deaths = int(total_deaths)
        i += 1

    return cases_last_7, hospital_cases, total_deaths

def covid_API_request(location:str = "Exeter", location_type:str = "ltla") -> list:
    """Returns data from the Public Health England API about COVID-19 statistics"""
    filters = [
        "areaType=" + location_type,
        "areaName=" + location
    ]
    #Dictates which data fields should be extracted
    structure = {
        "areaCode": "areaCode",
        "areaName": "areaName",
        "areaType": "areaType",
        "date": "date",
        "cumDeaths": "cumDeaths28DaysByPublishDate",
        "hospitalCases": "hospitalCases",
        "newCases": "newCasesByPublishDate"
    }
    api = Cov19API(filters=filters, structure=structure)

    try:
        #Uses the API to retrieve covid data, and returns it
        return api.get_json()["data"]
    except exceptions.FailedRequestError:
        logging.error("Failed request. Invalid location type %s", location_type)
        return []
    except error:
        logging.error(error)
        return []

def update_covid_data():
    """Updates the covid_data dict to have the most recent data available"""
    #Retrieving covid data using API requests
    local_data = process_covid_json_data(covid_API_request(LOCATION, LOCATION_TYPE))
    national_data = process_covid_json_data(covid_API_request(NATION, "nation"))

    #Updating dictionary items with new values
    covid_data["location"] = LOCATION
    covid_data["nation"] = NATION
    covid_data["local_cases"] = local_data[0]
    covid_data["national_cases"] = national_data[0]
    covid_data["hospital_cases"] = national_data[1]
    covid_data["deaths"] = national_data[2]
    logging.info("Updated COVID-19 data")

def schedule_covid_updates(update_interval:int, update_name:str):
    """Uses sched to schedule a data update at a given interval"""
    updates[update_name] = []
    updates[update_name].append(scheduler.enter(update_interval, 0, update_covid_data))
