import asyncio
from marzban import MarzbanAPI, UserCreate, UserModify, ProxySettings, UsersResponse
from logger import Logger
from config import config

logger = Logger.getinstance()
class ProxyClient:
    TOKEN = None
    def __init__(self):
        self.username = config.mb_username
        self.password = config.mb_passw
        self.api_url = config.mb_api_url
        self.api = MarzbanAPI(self.api_url)

    async def get_token(self) -> None:
        logger.info("get_token")
        token_data = await self.api.get_token(self.username, self.password)
        if ProxyClient.TOKEN is None:
            ProxyClient.TOKEN = token_data.access_token
        else:
            return
        
    async def get_users(self) -> UsersResponse:
        print(ProxyClient.TOKEN)
        await self.get_token()
        print(ProxyClient.TOKEN)
        return await self.api.get_users(ProxyClient.TOKEN)



proxy = ProxyClient()

asyncio.run(proxy.get_users())