import asyncio
import datetime
import json
import random
import traceback
from asyncio import CancelledError

import httpx as httpx
import websockets.client
from asgiref.sync import sync_to_async
from django.utils.timezone import make_aware

from CryptoWatcher.functions.Coloring import yellow, magenta, green, red, cyan, bright
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
        print(bright(f'KuCoin ({yellow(datetime.datetime.now())}) ---> ') + f'Connecting to ' + url)
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(url)
                if r.status_code == 200:
                    result = json.loads(r.text)
                    self.token = result['data']['token']
                    self.uri = result['data']['instanceServers'][0]['endpoint']
                    self.pingInterval = result['data']['instanceServers'][0]['pingInterval'] / 1000
                    print(
                        bright(f'KuCoin ({yellow(datetime.datetime.now())}) ---> ') + green('Connection Successful'))
                else:
                    print(bright(f'KuCoin ({yellow(datetime.datetime.now())}) ---> ') + red(str(r)))
                    raise httpx.ConnectTimeout("Manual Raise")
        except httpx.ConnectTimeout as e:
            print(bright(f'KuCoin ({yellow(datetime.datetime.now())}) ---> ') + red(str(e)))
            print(bright(f'KuCoin ({yellow(datetime.datetime.now())}) ---> ') + yellow("Reconnecting ..."))
            await self.connect(url)

    async def get_symbol_list(self, url: str):
        print(bright(f'KuCoin ({yellow(datetime.datetime.now())}) ---> ') + f'Connecting to ' + url)
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(url)
                if r.status_code == 200:

                    with open("CryptoWatcher/statics/all_symbols.json", "w") as f:
                        data = json.loads(r.text)['data']
                        data = [item['symbol'] for item in data]
                        f.write(json.dumps(data))

                    print(bright(f'KuCoin ({yellow(datetime.datetime.now())}) ---> ') + green("List Received"))
                    print(bright(f'KuCoin ({yellow(datetime.datetime.now())}) ---> ')
                          + green('Connection Successful'))
                else:
                    raise httpx.ConnectTimeout(r.json()['msg'])
        except httpx.ConnectTimeout as e:
            print(bright(f'KuCoin ({yellow(datetime.datetime.now())}) ---> ') + red(str(e)))
            print(bright(f'KuCoin ({yellow(datetime.datetime.now())}) ---> ') + yellow("Reconnecting ..."))
            await self.get_symbol_list(url)

    async def start_listening(self, interval: float = 0):
        await self.connect('https://api.kucoin.com/api/v1/bullet-public')
        uri = self.uri + f"?token={self.token}&connectId=welcome"
        print(bright(f'KuCoin ({yellow(datetime.datetime.now())}) ---> ') + "Starting Socket ...")

        async def doing():
            try:
                self.socket = await websockets.client.connect(uri, ping_interval=None)
            except Exception as error:
                print(bright(f'KuCoin ({yellow(datetime.datetime.now())}) ---> ')
                      + f"{red(str(error))}, {yellow('Retrying Socket')}")
                await doing()

        await doing()
        print(bright(f'KuCoin ({yellow(datetime.datetime.now())}) ---> ') + green('Socket started'))

        await self.get_symbol_list("https://api.kucoin.com/api/v2/symbols")

        asyncio.create_task(self.ping_pong())

        pairs = Pair.objects.all()
        pair_str = ""
        async for pair in pairs:
            pair.subscribed = False
            pair_str += f"{pair.currency.upper()}-{pair.base.upper()},"
            self.loop.run_in_executor(None, pair.save)

        await self.subscribe(['market', 'snapshot'], pair_str[:-1])

        try:
            async for message in self.socket:
                try:
                    await self.message_analyze(message)
                    await asyncio.sleep(interval)

                    pairs = Pair.objects.filter(subscribed=False)

                    pair_str = ""
                    async for pair in pairs:
                        pair.subscribed = False
                        pair_str += f"{pair.currency.upper()}-{pair.base.upper()},"
                        self.loop.run_in_executor(None, pair.save)

                    await self.subscribe(['market', 'snapshot'], pair_str[:-1])

                except Exception as e:
                    print(red(e) + traceback.format_exc())
                    continue
        except CancelledError:
            pass

    async def send(self, data: str):
        try:
            await self.socket.send(data)
        except websockets.ConnectionClosedError as e:
            print(bright(f'KuCoin ({yellow(datetime.datetime.now())}) ---> ') + red(str(e)))

    async def ping_pong(self):
        self.ping_id = str(random.randrange(100000, 1000000))
        await self.send(json.dumps({"id": self.ping_id, "type": "ping"}))
        self.ping_is_ponged = False

        start = datetime.datetime.now()
        while not self.ping_is_ponged:
            await asyncio.sleep(1)
            now = datetime.datetime.now()
            if (now - start).seconds == 10:
                break

        if self.ping_is_ponged:
            print(bright(f'KuCoin ({yellow(datetime.datetime.now())}) ---> ') + cyan(
                "Ping, Ponged.") + f" Next ping in {self.pingInterval} seconds.")
        else:
            print(bright(f'KuCoin ({yellow(datetime.datetime.now())}) ---> ') + red(
                "Ping did not ponged. Sending new ping"))

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
                    pair.subscribed = True

                    self.loop.run_in_executor(None, pair.save)

                except Pair.DoesNotExist:
                    pass
                except Pair.DoesNotExist as e:
                    print(bright(f'KuCoin ({yellow(datetime.datetime.now())}) ---> ') + red(e))

                try:
                    pair = await Pair.objects.aget(currency=data['quoteCurrency'], base=data['baseCurrency'])
                    pair.price = 1 / float(data['lastTradedPrice'])
                    pair.price_date = make_aware(datetime.datetime.now())

                    self.loop.run_in_executor(None, pair.save)

                except Pair.DoesNotExist:
                    pass
                except Exception as e:
                    print(bright(f'KuCoin ({yellow(datetime.datetime.now())}) ---> ') + red(e))

        else:
            print(bright(
                f'KuCoin ({yellow(datetime.datetime.now())}) ---> ') + "Unhandled Message Received ---> " + magenta(
                message))

    async def subscribe(self, topic: list[str], value: str, id: int = random.randrange(100000, 1000000)):

        sub = json.dumps({
            "id": id,
            "type": "subscribe",
            "topic": f"/{'/'.join(topic)}:{value}",
            "response": False
        })
        if value:
            await self.send(sub)

    @staticmethod
    async def pair_string(pairs):
        pair_str = ','.join(
            [f"{pair.currency.upper()}-{pair.base.upper()},{pair.base.upper()}-{pair.currency.upper()}"async for pair in
             pairs])
        return pair_str
