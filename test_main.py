from main import schedule_update
from main import deschedule_update
from main import updates
from main import get_title

def test_deschedule_update():
    update = {"title": "Update",
                "time": "17:23",
                "repeats": False,
                "covid": True,
                "news": False}
    schedule_update(update, "Updating COVID-19 data at 17:23")
    assert updates
    deschedule_update("update test")
    deschedule_update("Update")
    assert not updates

def test_schedule_update():
    assert not updates
    update = {"title": "Update",
                "time": "17:23",
                "repeats": False,
                "covid": True,
                "news": False}
    schedule_update(update, "Updating COVID-19 data at 17:23")
    assert updates

def test_get_title():
    updates.clear()
    update = {"title": "Update",
                "time": "17:23",
                "repeats": False,
                "covid": True,
                "news": False}
    schedule_update(update, "Updating COVID-19 data at 17:23")
    assert get_title("Update") == "Update1"
    update2 = {"title": "Update1",
                "time": "17:23",
                "repeats": False,
                "covid": True,
                "news": False}
    schedule_update(update2, "Updating COVID-19 data at 17:23")
    assert get_title("Update1") == "Update2"
    assert get_title("Update") == "Update2"
