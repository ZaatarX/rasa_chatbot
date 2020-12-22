# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

# This is a simple example for a custom action which utters "Hello World!"

import json
import requests
import httpx
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

        payload = {
            "userLogin": {
                "userIdentifier": "syn17",
                "password": "123456"
            }
        }

        payload = json.dumps(payload)

        headers = {
            'Content-Type': 'application/json',
            'servicekey': 'generateSessionToken',
            'sessionObject':
            "{\"platform\": \"CORE\", \"userLanguage\": \"en\"}"
        }

        #client = httpx.Client()
        close_client = True
        url = "https://unicoredemomaia.westus2.cloudapp.azure.com:3081/callservice"

        try:
            (res) = requests.post(url,
                                  data=payload,
                                  headers=headers,
                                  verify=False)

            res = json.loads(res.content)

            print("res: ", res)

            if res['errorCode'] == 90000:
                sessionToken = res['additionalData']['output']['sessionToken']

                dispatcher.utter_message(
                    text="Your session token is: {}".format(sessionToken))
            else:
                print("error.")
                dispatcher.utter_message(
                    text="There was an error: {}".format(res.status_code))

        except requests.ConnectionError as exc:
            print(f"An error occured while requesting {exc.errno!r}.")
            dispatcher.utter_message(
                text=f"An error occured while requesting {exc.errno!r}.")
        finally:
            return []


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
