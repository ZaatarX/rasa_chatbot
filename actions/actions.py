import os
import json
import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from dotenv import load_dotenv


class ActionGiveBalanceRequest(Action):
    def name(self) -> Text:
        return "action_give_balance_request"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        username = tracker.get_slot("username")
        password = tracker.get_slot("password")

        payload = {
            "userLogin": {
                "userIdentifier": username,
                "password": password
            }
        }

        payload = json.dumps(payload)

        headers = {
            'Content-Type': 'application/json',
            'servicekey': 'generateSessionToken',
            'sessionObject':
            "{\"platform\": \"CORE\", \"userLanguage\": \"en\"}"
        }

        url = os.getenv("HOST_URL")

        try:
            (res) = requests.post(url,
                                  data=payload,
                                  headers=headers,
                                  verify=False)

            res = json.loads(res.content)

            print("res: ", res)

            if res['errorCode'] == 90000:
                SlotSet('sessionToken',
                        res['additionalData']['output']['sessionToken'])

                dispatcher.utter_message(
                    text="Hi, {}! Do you want me to check your balance?".
                    format(username))
            else:
                print("error.")
                dispatcher.utter_message(
                    text="Seems like the credentials do not match our records 🙁"
                )

        except requests.ConnectionError as exc:
            print(f"An error occured while requesting {exc.errno!r}.")
            dispatcher.utter_message(
                text=f"An error occured while requesting {exc.errno!r}.")
        finally:
            return []


#import mysql.connector
#from mysql.connector import errorcode
'''
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
'''