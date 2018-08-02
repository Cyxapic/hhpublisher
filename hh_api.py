import os
import platform
import argparse
import json

import requests


class DataAPI:

    settings_path = os.path.join(os.getcwd(), 'settings.json')

    def _get_file(self):
        with open(self.settings_path, 'r') as file:
            return json.load(file)

    def _create_settings(self):
        print("Сначала созданим настройки!")
        token = input('Введите токе HH API: ')
        resume_id = input('Введите ID резюме HH: ')
        data = {'token': token,
                'resume_id': resume_id}
        with open(self.settings_path, 'w') as file:
            json.dump(data, file)

    def handler(self):
        if not os.path.exists(self.settings_path):
            self._create_settings()
        return self._get_file()


class Resume:
    MESSAGES = {
        500: ('Error', 'Server dont response or invalid data!'),
        429: ('Error', 'You are trying to update your resume too often'),
        403: ('Error', 'Token TTL has expired. Get a new token on https://dev.hh.ru/admin/'),
        204: ('Success', 'Your resume was updated'),
    }

    def __init__(self, data_api=None):
        '''
        data_api = {
            'token': 'TOKEN',
            'resume_id' 'RESUME_ID'
        }
        '''
        if not data_api:
            exit('No data HH API')
        self.URL = f"https://api.hh.ru/resumes/{data_api['resume_id']}/publish"
        self.HEADERS = {"Authorization": f"Bearer {data_api['token']}"}

    def _send_notify(self, title, message):
        msg = {
            'Linux': f'notify-send "{title}" "{message}"',
            'Darwin': f"""osascript -e 'display notification "{message}"
                         with title "{title}"' """,
        }
        os.system(msg[platform.system()])

    def send_request(self):
        r = requests.post(self.URL, headers=self.HEADERS)
        self._send_notify(*self.MESSAGES.get(r.status_code, 500))
