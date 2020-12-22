# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

# This is a simple example for a custom action which utters "Hello World!"

import json
from os import close
import httpx
import asyncio
import mysql.connector
from mysql.connector import errorcode
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class ActionGiveBalanceRequest(Action):
    def name(self) -> Text:
        return "action_give_balance_request"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        account_number = tracker.get_slot("account_number")

        my_params = {
            "userLogin": {
                "userIdentifier": "syn17",
                "password": "123456"
            }
        }
        my_params = json.dumps(my_params)

        my_headers = {
            "Content-Type": "application/json",
            "servicekey": "generateSessionToken",
            "sessionObject": {
                "platform": "CORE",
                "userLanguage": "en"
            }
        }
        my_headers = json.dumps(my_headers)

        res = asyncio.run(self.get_res(my_params, my_headers))

        print("res: ", res)

        if res:
            print("if 200")
            sessionToken = "empty"

            #for token in res['additionalData']:
            #    sessionToken = token['sessionToken']

            dispatcher.utter_message(
                text="Your session token is: {}".format(sessionToken))

        else:
            print("error.")
            dispatcher.utter_message(
                text="There was an error: {}".format(res.status_code))

        return []

    async def get_res(self, my_params, my_headers):
        client = httpx.AsyncClient()
        close_client = True
        url = "https://unicoredemomaia.westus2.cloudapp.azure.com:3081"

        res = await client.post(url, headers=my_headers, data=my_params)

        if close_client:
            await client.aclose()

        return res


class ActionGiveBalance(Action):
    def name(self) -> Text:
        return "action_give_balance"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        account_number = tracker.get_slot("account_number")

        try:
            my_conn = mysql.connector.connect(host='localhost',
                                              user='root',
                                              password='admin',
                                              database='new_schema')

            cursor = my_conn.cursor()

            query = ("SELECT balance FROM balance WHERE account_number={}".
                     format(account_number))

            cursor.execute(query)

            blc = 0.0

            for balance in cursor:
                blc = balance

            dispatcher.utter_message(
                text="The balance for {} is: ${}".format(account_number, blc))
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        else:
            my_conn.close()

        return []
