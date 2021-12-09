"""This module uses the News API to retrieve Covid-19-related news articles.
It has methods for updating the list of articles and removing items."""

import datetime
import json
from os import error, path
import logging
import requests

THIS_FOLDER = path.dirname(path.abspath(__file__))

with open(path.join(THIS_FOLDER, "config.json"), "r", encoding="UTF-8") as config_file:
    #Takes users API key from the config file
    KEY = json.load(config_file)["APIKey"]

logging.basicConfig(filename="pysys.log", level=logging.INFO)

#List of news articles
news_data = []
#Set of articles the user has specified to be removed
removed_articles = set()

def news_API_request(covid_terms:str = "Covid COVID-19 coronavirus") -> list:
    """Returns news articles relating to COVID-19 retrieved from News API"""
    if KEY == "":
        logging.error("No API Key provided for News API")
        return []

    date = datetime.date.today()

    #List of new articles to return
    results = []
    #Goes through each specified term to look for articles
    for term in covid_terms.split(" "):
        #Arguments for the API request are specified in the url
        url = f"""https://newsapi.org/v2/everything?q={term}
            &from={date}&sortBy=popularity&apiKey={KEY}"""

        try:
            #Requests for news data from the API
            new_articles = requests.get(url).json()["articles"]

            for new_item in new_articles:
                #Checks to see if the article has already been requested
                new_duplicate = next((article for article in results
                    if article["url"] == new_item["url"]), None)

                #Or if it is already in the list of news data
                old_duplicate = next((article for article in news_data
                    if article["url"] == new_item["url"]), None)

                #Has the user removed this article?
                removed = new_item["url"] in removed_articles

                if not (new_duplicate or old_duplicate or removed):
                    results.append(new_item)

        except KeyError:
            logging.error("Invalid API Key")
            return []

        except error:
            logging.error(error)
            return []

    return results

def update_news(terms:str = "Covid COVID-19 coronavirus"):
    """Updates news_data by sending a new request"""
    news_data.extend(news_API_request(terms))
    logging.info("Updated news data")

def remove_article(article:dict):
    """Removes an article by adding it to the list of removed articles"""
    if article:
        removed_articles.add(article["url"])
        logging.info("Article removed: %s", article["title"])
    else:
        logging.error("No article specified to remove")
