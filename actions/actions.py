import os
import json
import requests
import mysql.connector
from mysql.connector import errorcode
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict
from dotenv import load_dotenv

load_dotenv()


class ValidateLoginForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_login_form"

    def validate_username(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

        print(tracker.get_slot("password"))
        print(slot_value)

        if tracker.get_slot("password") is not None:
            self.validate_password(slot_value, CollectingDispatcher, Tracker,
                                   DomainDict)
        else:
            return {"username": slot_value}

    def validate_password(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

        if tracker.get_slot("username") is not None:
            username = tracker.get_slot("username")
            password = tracker.get_slot("password")
            userValue = None
            passValue = None

            print(username)
            print("asdasdasd {}".format(password))

            payload = {
                "userLogin": {
                    "userIdentifier": username,
                    "password": "123456"
                }
            }

            payload = json.dumps(payload)

            headers = {
                'Content-Type':
                'application/json',
                'servicekey':
                'generateSessionToken',
                'sessionObject':
                "{\"platform\": \"CORE\", \"userLanguage\": \"en\"}"
            }

            url = os.getenv("HOST_URL")

            try:
                res = requests.post(url=url,
                                    headers=headers,
                                    data=payload,
                                    verify=False)

                res = json.loads(res.content)

                if res['errorCode'] == 90000:
                    userValue = username
                    passValue = password

                    dispatcher.utter_message(
                        text="Hi, {}! Do you want me to check your balance?".
                        format(username))

                    return {
                        'password':
                        passValue,
                        'is_authenticated':
                        "ok",
                        'sessionToken':
                        res['additionalData']['output']['sessionToken'],
                        'username':
                        userValue
                    }
                else:
                    dispatcher.utter_message(
                        text=
                        "Seems like the credentials do not match our records 🙁"
                    )

                    return {'username': userValue, 'password': passValue}

            except requests.ConnectionError as e:
                print("Couldn't connect: {}.".format(e))
                dispatcher.utter_message(
                    text=
                    "I'm having some connectivity issues right now. Could you try later?"
                )

                return {'password': slot_value}

        else:
            return {"password": slot_value}


class ValidateNameForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_name_form"

    def validate_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

        name = tracker.get_slot('name')
        print(name)

        split_name = name.split()

        first_name = str(split_name[0])
        last_name = str(split_name[1])

        print(first_name)

        try:
            my_conn = mysql.connector.connect(host='localhost',
                                              user='root',
                                              password='admin',
                                              database='new_schema')

            cursor = my_conn.cursor()

            query = (
                "SELECT * FROM clients WHERE first_name = '{}' AND last_name = '{}'"
                .format(first_name, last_name))

            cursor.execute(query)

            dispatcher.utter_message(
                text=
                "Hello, {}! It's so nice to have you back! Would you like to login?"
                .format(name))

            return {'matched': "ok", 'name': name}

            #return {'name': name}

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
                dispatcher.utter_message(
                    text=
                    "Sorry, I'm facing some issues right now, please try again later..."
                )
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
                dispatcher.utter_message(
                    text=
                    "Sorry, I'm facing some issues right now, please try again later..."
                )
            else:
                print(err)
                dispatcher.utter_message(
                    text=
                    "Sorry, I'm facing some issues right now, please try again later..."
                )
        else:
            my_conn.close()

        return []