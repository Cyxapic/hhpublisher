import os
import platform
import argparse
import json
import getpass

import requests


class DataAPI:

    settings_path = os.path.join(os.getcwd(), 'settings.json')

    def _get_file(self):
        with open(self.settings_path, 'r') as file:
            return json.load(file)

    def _create_settings(self):
        print("Сначала созданим настройки!")
        TOKEN = input('Введите токе HH API: ')
        RESUME_ID = input('Введите ID резюме HH: ')
        SENDMAIL = input('Отправлять на почту уведомления? y/n: ')
        SENDMAIL = 'Y' if SENDMAIL.upper() == 'Y' else 'N'
        data = {'TOKEN': TOKEN,
                'RESUME_ID': RESUME_ID,
                'SENDMAIL': SENDMAIL,}
        if SENDMAIL == 'Y':
            MAIL_HOST = input('Введите host (прим. smtp.yandex.ru): ')
            EMAIL_PORT = input('Введите port (прим. 587): ')
            EMAIL_HOST_USER = input('Введите user (прим. test@yandex.ru): ')
            EMAIL_HOST_PASSWORD = getpass.getpass()
            EMAIL = input('Введите куда отправяем (прим. to_test@yandex.ru): ')
            data.update({
                    'MAIL_HOST': MAIL_HOST,
                    'EMAIL_PORT': EMAIL_PORT,
                    'EMAIL_HOST_USER': EMAIL_HOST_USER,
                    'EMAIL_HOST_PASSWORD': EMAIL_HOST_PASSWORD,
                    'EMAIL': EMAIL,
                })
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
            'TOKEN': 'TOKEN',
            'RESUME_ID': 'RESUME_ID',
            'SENDMAIL': 'Y'/'N',
        }
        '''
        if not data_api:
            exit('No data HH API')
        self.data_api = data_api
        self.URL = f"https://api.hh.ru/resumes/{data_api['RESUME_ID']}/publish"
        self.HEADERS = {"Authorization": f"Bearer {data_api['TOKEN']}"}

    def send_request(self):
        r = requests.post(self.URL, headers=self.HEADERS)
        self._send_notify(*self.MESSAGES.get(r.status_code, 500))

    def _send_notify(self, title, message):
        msg = {
            'Linux': f'notify-send "{title}" "{message}"',
            'Darwin': f"""osascript -e 'display notification "{message}"
                         with title "{title}"' """,
        }
        if self.data_api['SENDMAIL'] == 'Y':
            self._email_notify(title, message)
        else:
            os.system(msg[platform.system()])

    def _email_notify(self, title, message):
        msg = (
            f'From: {self.data_api["EMAIL_HOST_USER"]}\n'
            f'To: {self.data_api["EMAIL"]}\n'
            'Content-Type: text/html; charset="utf-8"\n'
            f'Subject: {title}\n'
            f'{message}'
        )
        host = self.data_api['MAIL_HOST']
        port = self.data_api['EMAIL_PORT']
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(self.data_api['EMAIL_HOST_USER'],
                         self.data_api['EMAIL_HOST_PASSWORD'])
            server.sendmail(self.data_api['EMAIL_HOST_USER'],
                            self.data_api['EMAIL'],
                            msg)
