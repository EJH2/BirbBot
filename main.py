from functools import lru_cache

import logging
import discord
import pydantic_settings


logger = logging.getLogger("discord")


class BotSettings(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(
        env_file=".env"
    )

    GUILD_ID: int
    APPROVED_ROLE_IDS: set[int]
    GATE_ROLE_ID: int
    BOT_TOKEN: str


@lru_cache
def get_settings() -> BotSettings:
    return BotSettings()

settings = get_settings()


class BirbBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.guild: discord.Guild = None
        self.approved_roles: set[discord.Role] = set()
        self.gate_role: discord.Role = None

    async def on_ready(self):
        logger.info(f'Logged on as {self.user}!')
        self.guild = discord.utils.get(self.guilds, id=settings.GUILD_ID)
        self.approved_roles = set(discord.utils.get(self.guild.roles, id=role_id) for role_id in settings.APPROVED_ROLE_IDS)
        self.gate_role = discord.utils.get(self.guild.roles, id=settings.GATE_ROLE_ID)


    async def on_member_update(self, _: discord.Member, after: discord.Member):
        if after.guild != self.guild or self.gate_role not in after.roles:
            return

        if set(after.roles) & self.approved_roles:
            await after.remove_roles(self.gate_role, reason="Role gate bypass")
            logger.info(f"Applied role gate bypass to {after.name}!")



intents = discord.Intents.none()
intents.guilds = True
intents.members = True

client = BirbBot(intents=intents)
client.run(settings.BOT_TOKEN)
