from covid_news_handling import news_API_request
from covid_news_handling import update_news
from covid_news_handling import remove_article
from covid_news_handling import removed_articles

def test_news_API_request():
    assert news_API_request()
    assert news_API_request('Covid COVID-19 coronavirus') == news_API_request()

def test_update_news():
    update_news('test')

def test_remove_article():
    remove_article({"url":"test", "title": "Test"})
    assert "test" in removed_articles
