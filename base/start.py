from datetime import datetime, timedelta
import time
import sys
from pprint import pprint
import random
import pickle
import json
import requests
import os
from collections import deque
import boto3
import base64
from dateutil import parser

import dash
from dash import no_update as NUP
from dash import dcc, html
from dash.dependencies import ClientsideFunction
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import DashProxy, MultiplexerTransform, Output, Input, State


def full_s3_key(name, folder):
    return f'{folder}/{name}' if folder else name


def core_s3_key(name):
    return name.split('/')[-1]


def time_suffix(precision=1):
    return ''.join([v for v in str(datetime.utcnow()) if v.isnumeric()])[4:-precision]


def temp_local(name):
    body, ext = name.split('.')
    return f'temp{time_suffix()}.{ext}', ext


def clock():
    return datetime.now().strftime('%H:%M:%S')


class Storage:

    def __init__(self, credentials=None, space='robot-2048'):
        if credentials is not None:
            self.engine = boto3.resource(
                service_name='s3',
                endpoint_url=f'https://{credentials["region"]}.digitaloceanspaces.com',
                region_name=credentials['region'],
                aws_access_key_id=credentials['access_key'],
                aws_secret_access_key=credentials['secret_key']
            )
        else:
            self.engine = boto3.resource('s3')
        self.space = self.engine.Bucket(space)
        self.space_name = space

    def list_files(self, folder=None):
        files = [o.key for o in self.space.objects.all()]
        if folder:
            return [f for f in files if (f.startswith(f'{folder}/') and f != f'{folder}/')]
        else:
            return files

    def delete(self, name, folder=None):
        name = full_s3_key(name, folder)
        if name in self.list_files():
            self.engine.Object(self.space_name, name).delete()

    def copy(self, src, dst):
        self.space.copy({'Bucket': self.space_name, 'Key': src}, dst)

    def save_file(self, file, name, folder=None):
        self.space.upload_file(file, full_s3_key(name, folder))

    def save(self, data, name, folder=None):
        temp, ext = temp_local(name)
        with open(temp, 'w') as f:
            match ext:
                case 'json':
                    json.dump(data, f)
                case 'txt':
                    f.write(data)
                case 'pkl':
                    pickle.dump(data, f, -1)
                case _:
                    return
        self.save_file(temp, name, folder)
        os.remove(temp)

    def load(self, name, folder=None):
        full = full_s3_key(name, folder)
        if full not in self.list_files():
            return
        temp, ext = temp_local(name)
        self.space.download_file(full, temp)
        match ext:
            case 'json':
                with open(temp, 'r', encoding='utf-8') as f:
                    result = json.load(f)
            case 'txt':
                with open(temp, 'r') as f:
                    result = f.read()
            case 'pkl':
                with open(temp, 'rb') as f:
                    result = pickle.load(f)
            case _:
                result = None
        os.remove(temp)
        return result

    def add_to_memo(self, text):
        memo = self.load('memory_usage.txt') or ''
        self.save(memo + text + '\n', 'memory_usage.txt')

    def add_log(self, text, user):
        log_file = f'logs_{user}'
        if text:
            memo = self.load(log_file, 'user_logs') or ''
            memo += text + '\n'
            self.save(memo, log_file, 'user_logs')


working_directory = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(working_directory, 'config.json'), 'r') as f:
    CONF = json.load(f)
dash_intervals = CONF['intervals']
dash_intervals['refresh'] = dash_intervals['refresh_sec'] * 1000
dash_intervals['check_run'] = dash_intervals['refresh_sec'] * 2
dash_intervals['vc'] = dash_intervals['vc_sec'] * 1000
dash_intervals['next'] = dash_intervals['refresh_sec'] + 180
LOWEST_SPEED = 50

LOCAL = os.environ.get('S3_URL', 'local')
if LOCAL == 'local':
    ROOT_URL = 'http://localhost:5000'
else:
    ROOT_URL = 'back_2048:5000'

s3_credentials = {
    'region': os.environ.get('S3_REGION', None),
    'access_key': os.environ.get('S3_ACCESS_KEY', None),
    'secret_key': os.environ.get('S3_SECRET_KEY', None)
}

S3 = Storage(s3_credentials)
