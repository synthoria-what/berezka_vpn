import asyncio
from marzban import MarzbanAPI, UserCreate, UserModify, ProxySettings, UsersResponse, UserResponse
from logger import Logger
from config import config, UserResponseF, TariffConfig

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
        
        
    async def get_users(self, offset: int | None = 0, limit: int | None = 10):
        await self.get_token()
        users = await self.api.get_users(ProxyClient.TOKEN, offset, limit)
        users_list = []
        for user in users.users:
            username = user.username
            sub_link = user.subscription_url
            status = user.status
            used_traffic = user.used_traffic
            created_at = user.created_at
            user_f = UserResponseF(username=username, status=status, used_traffic=used_traffic, sub_link=sub_link, created_at=created_at)
            users_list.append(user_f)
        return users_list
        
        
    async def get_users_total(self) -> UsersResponse:
        await self.get_token()
        users = await self.api.get_users(ProxyClient.TOKEN, limit=10)
        logger.info(f"users info: {users.total}")
        return users.total
    
    async def get_user(self, username: str) -> UserResponse:
        await self.get_token()
        return await self.api.get_user(username, ProxyClient.TOKEN)
    
    async def create_user(self, username: str, **kwargs) -> UserCreate:
        await self.get_token()
        base_params = dict(
                username=username,
                proxies={"vless": ProxySettings(flow="xtls-rprx-vision")},
                inbounds={"vless": ["VLESS TCP REALITY"]},
            )
        user = UserCreate(**base_params, **kwargs)
        add_user = await self.api.add_user(user, ProxyClient.TOKEN)
        return add_user.subscription_url
    
    async def delete_user(self, username: str) -> None:
        await self.get_token()
        return await self.api.remove_user(username, ProxyClient.TOKEN)
    
    async def edit_user(self, username: str, **kwargs: int) -> None:
        """
        expire: int - Параметр длительности подписки

        data_limit: int - Объем трафика подписки

        note: str - Описание ключа

        status: str - Статус ключа

        """
        try:
            logger.warning(f"kwargs data: {kwargs}")
            await self.get_token()
            user = UserModify(username=username, **kwargs)
            return await self.api.modify_user(username, user, ProxyClient.TOKEN)
        except Exception as ex:
            logger.info(f"Произошла ошибка при обновлении подписки: {ex}")