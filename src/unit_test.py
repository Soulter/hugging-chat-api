"""
For test hugchat
"""

# import os
import logging

from .hugchat.message import MessageStatus, ResponseTypes, Message, MSGTYPE_ERROR
import sys

logging.basicConfig(level=logging.DEBUG)


class MockResponse():
    """
    mock a respone from hugchat api
    """

    def __init__(self, response_list):
        self.index = 0
        self.response_list = response_list

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.response_list):
            raise StopIteration
        result = self.response_list[self.index]
        self.index += 1
        return result


class Test(object):
    """
    test hugchat api
    """

    def test_web_search_failed_results(self):
        response_list = [{
            "type":
            ResponseTypes.WEB,
            "messageType":
            MSGTYPE_ERROR,
            "message":
            "Failed to parse webpage",
            "args": [
                "This operation was aborted",
                "https://www.accuweather.com/en/gb/london/ec4a-2/weather-forecast/328328"
            ]
        }, {
            "type":
            ResponseTypes.WEB,
            "messageType":
            ResponseTypes.WEB,
            "sources": [{
                "title": "1",
                "link": "2",
                "hostname": "3"
            }]
        }, {
            "type":
            ResponseTypes.WEB,
            "messageType":
            MSGTYPE_ERROR,
            "message":
            "Failed to parse webpage",
            "args": [
                "This operation was aborted",
                "https://www.accuweather.com/en/gb/london/ec4a-2/weather-forecast/328328"
            ]
        }, {
            "type": ResponseTypes.FINAL,
            "messageType": "answer",
            "text": "Funny joke"
        }]

        mock = MockResponse(response_list)
        response = Message(mock, web_search=True)
        while True:
            try:
                print(response)
                response = next(response)
            except StopIteration:
                break
        assert len(response.web_search_sources
                   ) == 1  # only the second web search response is valid.
        assert response.text == "Funny joke"
