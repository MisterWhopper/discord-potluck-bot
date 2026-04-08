from potluck import INotifier, NotifierCallback, IMessage, User
from typing import Protocol
from potbot import PotluckBot
from events import EventListener, EventType
import discord

class IBotAdapter(Protocol):
    event_listener: EventListener
    pass


class BotNotifier(INotifier):
    def __init__(self, adapter: IBotAdapter):
        self.adapter = adapter

    def forward_event_registration(self, event_type: EventType, callback: NotifierCallback):
        self.adapter.event_listener.register(event_type, callback)

    def run(self):
        self.adapter.run()
    
    async def send_announcement(self, message: IMessage): 
        pass

    async def send_message(self, message: IMessage, to_user: User): 
        pass

    async def update_message(self, message_id: int, new_message: IMessage): 
        pass

    pass


class PotBotAdapter(IBotAdapter):
    def __init__(self, client: PotluckBot):
        self.client = client
        self.event_listener = EventListener()

    def run(self):
        self.client.run()
