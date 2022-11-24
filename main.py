""" Lesson 2 for Devman """
import json
from typing import Any
from urllib.parse import urlparse
from environs import Env
from validators import url, ValidationFailure
from requests import post, Response
from requests.exceptions import HTTPError
#import bitly_api ### С этим, конечно, в 2 раза короче скрипт будет, но вам ведь не это надо :)))

def get_token() -> str:
    """ Returns a token for use bitly API """
    env: Env = Env()
    env.read_env()
    return env.str('TOKEN')


def get_shorten_link(link: str) -> str:
    """ Returns a shorten link via bit.ly """
    headers: dict = {
        'Authorization': f'Bearer {get_token()}',
        'Content-Type': 'application/json',
    }
    data: dict = {'long_url': link}
    try:
        response: Response = post('https://api-ssl.bitly.com/v4/shorten',
                                  headers=headers, data=json.dumps(data),
                                  timeout=30)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        return ''
    else:
        result: dict = json.loads(response.content)
        return result.get('link')


def get_clicks(link: str) -> int:
    """ Returns amount of clicks on given shorten link """
    headers: dict = {
        'Authorization': f'Bearer {get_token()}',
        'Content-Type': 'application/json',
    }
    params: tuple = (('unit', 'day'), ('units', '-1'))
    try:
        response: Response = post(f'https://api-ssl.bitly.com/v4/bitlinks/{link}/clicks/summary',
                                  params=params, headers=headers, timeout=30)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        if response.status_code == 405:
            print('Upgrade your bit.ly account.'
                  'Statistics now needs for payment in bitly policies.')
        return 0
    else:
        result: dict = json.loads(response.content)
        return result.get('total_clicks')


def is_url(link: str) -> bool:
    """ Checks parameter link is a valid URL """
    result: Any = url(link)
    return not isinstance(result, ValidationFailure)


def main() -> None:
    """ Main work process """
    link: str = ''
    while not is_url(link):
        link = input('Введите ссылку: ')
    domain = urlparse(link).netloc
    if domain == 'bit.ly':
        path = urlparse(link).path
        print(f'По Вашей ссылке прошли {get_clicks(domain + path)} раза')
    else:
        print('Битлинк: ', get_shorten_link(link))


if __name__ == '__main__':
    main()
