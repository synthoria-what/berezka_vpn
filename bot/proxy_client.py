from marzban import MarzbanAPI, UserCreate, UserModify, ProxySettings
import os
from dotenv import load_dotenv
from logger import Logger


class ProxyClient:
    api_url: str
    def __init__(self, api_url):
        self.api_url = api_url