"""Covid-19 Dashboard webapp program that uses the flask module.
Also uses modules made by me for retrieving UK Covid-19 data
and related news articles"""

import time
import os
import logging
from flask import Flask, render_template, request, send_from_directory
from covid_data_handler import update_covid_data, schedule_covid_updates
from covid_data_handler import updates, covid_data, scheduler
from covid_news_handling import update_news, remove_article, news_data, removed_articles

logging.basicConfig(filename="pysys.log", level=logging.INFO)

app = Flask(__name__)

#List of scheduled update widgets on the left hand of the screen
gui_updates = []

def remove_update(title:str):
    """Called when the user closes an update widget
    removes it from the list of updates so it is not rendered"""

    if gui_updates:
        #Finds the item in the list of updates that has the given title
        to_remove = next((item for item in gui_updates if item["title"] == title), None)
        if to_remove:
            #Removes this item from the list
            gui_updates.remove(to_remove)

def get_title(update_title:str) -> str:
    """Method for making sure all updates have unique identifiers by reassigning taken titles"""
    if update_title in updates and not update_title[-1].isnumeric():
        #Adds a "1" to the end of an update title if it is taken
        #and the last character is not already a digit
        update_title += "1"
    i = 0
    while update_title in updates:
        #Increments the digit while the title is still taken
        i += 1
        update_title = update_title[:-1] + str(i)
    return update_title

def schedule_update(update:dict, desc:str):
    """Uses sched to schedule updates that the user has specified"""
    #Time in seconds until the update should occur is calculated using current time
    time_now = time.gmtime()
    hours = int(update["time"][:2]) - time_now.tm_hour
    mins = int(update["time"][3:]) - time_now.tm_min + hours*60 - 1
    secs = (mins*60 + (60 - time_now.tm_sec)) % 86400 #Seconds in a day

    #A new item is added to the dictionary of updates
    #with the update title as the key and an empty list as the value
    #This list will hold all the scheduled functions relating to this update event
    updates[update["title"]] = []

    #Updates are scheduled for covid and news data respectively, if specified
    if update["covid"]:
        schedule_covid_updates(secs, update["title"])
    if update["news"]:
        updates[update["title"]].append(scheduler.enter(secs,0,update_news))

    #Removes the update widget when the time has elapsed and the update has occurred
    updates[update["title"]].append(scheduler.enter(secs,1,remove_update,(update["title"],)))
    #Means that the update item gets cleared from the dictionary when it is complete
    updates[update["title"]].append(scheduler.enter(secs,1,updates.pop,(update["title"],)))

    #If the update is set to repeat, an event is scheduled
    #that reschedules the same update again when it is complete
    if update["repeats"]:
        #A new update widget also has to be added because the old one will be removed once complete
        gui_update = {"title": update["title"], "content": desc}
        updates[update["title"]].append(scheduler.enter(secs,2,gui_updates.append,(gui_update,)))
        updates[update["title"]].append(scheduler.enter(secs,2,schedule_update,(update,desc,)))

    logging.info("Scheduled update: %s", update["title"])
    logging.info(desc)

def deschedule_update(title:str):
    """Uses sched to cancel a scheduled update"""
    if updates:
        if title in updates:
            for event in updates[title]:
                #Cancels all scheduled events relating to the update
                scheduler.cancel(event)
            #Update is removed from the dictionary
            updates.pop(title)
            logging.info("Cancelled update: %s", title)
        else:
            logging.error("%s is not a scheduled update", title)
    else:
        logging.error("No updates to deschedule")

@app.route("/index")
def main() -> str:
    """Main program script. Runs when /index page is loaded"""
    #If user tries to remove an article, finds this article
    #and removes it using remove_article method in covid_news_handling
    to_remove = request.args.get("notif")
    if to_remove:
        for item in news_data:
            if item["title"] == to_remove:
                remove_article(item)

    #If user enters an update to schedule, retrieves this information and adds an update to the list
    update_time = request.args.get("update")
    if update_time:
        update_title = get_title(request.args.get("two"))
        repeat_update = request.args.get("repeat") is not None
        do_update_covid_data = request.args.get("covid-data") is not None
        do_update_news_data = request.args.get("news") is not None
        if do_update_covid_data and do_update_news_data:
            content = "Updating COVID-19 data and news articles at " + update_time
        elif do_update_covid_data:
            content = "Updating COVID-19 data at " + update_time
        elif do_update_news_data:
            content = "Updating news articles at " + update_time
        else:
            content = "Updating at " + update_time
        if repeat_update:
            content += " with repeats"

        if do_update_covid_data or do_update_news_data:
            gui_updates.append({"title": update_title, "content": content})
            update = {"title": update_title,
                "time": update_time,
                "repeats": repeat_update,
                "covid": do_update_covid_data,
                "news": do_update_news_data}
            schedule_update(update, content)
        else:
            logging.error("Empty update request")

    #If user tries to remove an update, finds this update and removes it from the list
    update_to_remove = request.args.get("update_item")
    if update_to_remove and gui_updates:
        deschedule_update(update_to_remove)
        remove = next((item for item in gui_updates if item["title"] == update_to_remove), None)
        if remove:
            gui_updates.remove(remove)

    #Makes sure none of the removed articles are rendered
    news_to_render = []
    for item in news_data:
        if item["url"] not in removed_articles:
            news_to_render.append(item)

    #blocking=False means program does not wait for scheduled events before rendering the page
    scheduler.run(blocking=False)

    #Uses flask to render index.html with the following variables assigned
    return render_template("index.html",
        title="COVID-19 Dashboard",
        favicon="favicon.ico",
        image="image.png",
        location=covid_data["location"],
        nation_location=covid_data["nation"],
        local_7day_infections=covid_data["local_cases"],
        national_7day_infections=covid_data["national_cases"],
        hospital_cases=covid_data["hospital_cases"],
        deaths_total=covid_data["deaths"],
        news_articles=news_to_render,
        updates=gui_updates)

@app.route('/favicon.ico')
def favicon():
    """Runs when the favicon is requested"""
    return send_from_directory(os.path.join(app.root_path, 'static'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    update_news()
    update_covid_data()
    app.run()
