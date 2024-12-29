import requests as requests


URL_RECORD = "http://0.0.0.0:8000/record"
URL_COLLECT = "http://0.0.0.0:8000/collect"
DATA = {"engine_temperature": 0.3}
CONTENT_RECORD = {"success": True}
CONTENT_COLLECT = {
    "average_engine_temperature": 0.3,
    "current_engine_temperature": 0.3
}


def test_record_engine_temperature():
    data = DATA
    response = requests.post(URL_RECORD, json=data)
    assert response.content == CONTENT_RECORD


def test_collect_engine_temperature():
    response = requests.post(URL_COLLECT)
    assert response.content == CONTENT_COLLECT
