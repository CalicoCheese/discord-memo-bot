import discord
from client.listeners import listeners


class DMMessage:
    def __init__(self, client):
        self.bot = client

    @listeners
    def dm_message(self, message: discord.Message):
        return


def setup(client):
    client.add_listener_of_group(DMMessage(client))
