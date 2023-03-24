import asyncio
import datetime
import json
import random

import httpx as httpx
import websockets.client

from Coloring import yellow, magenta, green, red, cyan


class KuCoin:
    socket = None
    token = None
    pingInterval = 0
    ping_is_ponged = False

    def __init__(self, uri: str, loop=asyncio.get_event_loop()):
        self.ping_id = 0
        self.uri = uri
        self.loop = loop
        self.socket: websockets.client.Connection
        self.token: str

    async def connect(self, url: str):
        print(f'Connecting to ' + url, end=" ")
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(url)
                if r.status_code == 200:
                    result = json.loads(r.text)
                    self.token = result['data']['token']
                    self.uri = result['data']['instanceServers'][0]['endpoint']
                    self.pingInterval = result['data']['instanceServers'][0]['pingInterval'] / 1000
                    print(green('(Connection Successful)'))
                else:
                    print(red(str(r)))
                    raise httpx.ConnectTimeout("Manual Raise")
        except httpx.ConnectTimeout as e:
            print(red(str(e)))
            print(yellow("Reconnecting ..."))
            await self.connect(url)

    async def start_listening(self, interval: float = 0):
        await self.connect('https://api.kucoin.com/api/v1/bullet-public')
        uri = self.uri + f"?token={self.token}&connectId=welcome"
        print("Starting Socket ...", end=" ")
        self.socket = await websockets.client.connect(uri)
        print(green('(Socket started)'))

        asyncio.create_task(self.ping_pong())

        async for message in self.socket:
            try:
                print("New Data Received ---> " + magenta(message))
                self.message_analyze(message)
                await asyncio.sleep(interval)
            except websockets.ConnectionClosed:
                continue

    async def send(self, data: str):
        try:
            await self.socket.send(data)
        except websockets.ConnectionClosedError as e:
            print(red(str(e)))

    async def ping_pong(self):
        self.ping_id = str(random.randrange(100000, 1000000))
        print(yellow('Pinging ... '), end=" ")
        await self.send(json.dumps({"id": self.ping_id, "type": "ping"}))
        print(green('(Pinged)'))
        self.ping_is_ponged = False

        start = datetime.datetime.now()
        while not self.ping_is_ponged:
            await asyncio.sleep(1)
            now = datetime.datetime.now()
            if (now - start).seconds == 10:
                break

        if self.ping_is_ponged:
            print(cyan("Ping, Ponged.") + f" Next ping in {self.pingInterval} seconds.")
        else:
            print(red("Ping did not ponged. Sending new ping"))

        await asyncio.sleep(self.pingInterval)
        await self.ping_pong()

    def message_analyze(self, message: str):
        data = json.loads(message)
        if data['type'] == "pong":
            if data['id'] == self.ping_id:
                self.ping_is_ponged = True

    async def subscribe(self, currency: str = None, base: str = None):

        sub = json.dumps({
            "id": 1545910660739,
            "type": "subscribe",
            "topic": "/market/snapshot:BTC-ETH",
            "response": True
        })
        await self.send(sub)
