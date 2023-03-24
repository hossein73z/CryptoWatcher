import asyncio
import datetime
import json
import random

import httpx as httpx
import websockets.client
from django.utils.timezone import make_aware

from Coloring import yellow, magenta, green, red, cyan
from priceWatcher.models import Pair


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

        async def doing():
            try:
                self.socket = await websockets.client.connect(uri)
            except Exception as e:
                print(f"{red(str(e))}, {yellow('Retrying Socket')}")
                await doing()

        await doing()
        print(green('Socket started'))

        asyncio.create_task(self.ping_pong())
        pairs = Pair.objects.all()
        pair_string = await self.pair_string(pairs)
        await self.subscribe(['market', 'snapshot'], pair_string)

        async for message in self.socket:
            try:
                await self.message_analyze(message)
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

    async def message_analyze(self, message: str):
        data = json.loads(message)
        if data['type'] == "pong":
            if data['id'] == self.ping_id:
                self.ping_is_ponged = True
        elif data['type'] == "message":
            if data['subject'] == "trade.snapshot":
                data = data['data']['data']

                try:
                    pair = await Pair.objects.aget(currency=data['baseCurrency'], base=data['quoteCurrency'])
                    pair.price = data['lastTradedPrice']
                    pair.price_date = make_aware(datetime.datetime.now())

                    self.loop.run_in_executor(None, pair.save)

                except Pair.DoesNotExist:
                    pass
                except Pair.DoesNotExist as e:
                    print(red(e))

                try:
                    pair = await Pair.objects.aget(currency=data['quoteCurrency'], base=data['baseCurrency'])
                    pair.price = 1 / float(data['lastTradedPrice'])
                    pair.price_date = make_aware(datetime.datetime.now())

                    self.loop.run_in_executor(None, pair.save)

                except Pair.DoesNotExist:
                    pass
                except Exception as e:
                    print(red(e))

        else:
            print("New Data Received ---> " + magenta(message))

    async def subscribe(self, topic: list[str], value: str, id: int = random.randrange(100000, 1000000)):

        sub = json.dumps({
            "id": id,
            "type": "subscribe",
            "topic": f"/{'/'.join(topic)}:{value}",
            "response": True
        })
        await self.send(sub)

    @staticmethod
    async def pair_string(pairs):
        pair_str = ','.join([
            f"{pair.currency.upper()}-{pair.base.upper()},{pair.base.upper()}-{pair.currency.upper()}"
            async for pair in pairs
        ])
        return pair_str
