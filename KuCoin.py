import asyncio
import json

import httpx as httpx
import websockets.client

from Coloring import yellow, magenta, green, red


class KuCoin:
    socket = None
    token = None

    def __init__(self, uri: str):
        self.uri = uri
        self.__listening: asyncio.Task
        self.socket: websockets.client.Connection
        self.token: str

    async def connect(self, url: str):
        print(magenta(f'Connecting to ') + url)
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(url)
                if r.status_code == 200:
                    result = json.loads(r.text)
                    self.token = result['data']['token']
                    self.uri = result['data']['instanceServers'][0]['endpoint']
                    print(green('Connection Successful'))
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
        print(magenta("Starting Socket ..."))
        self.socket = await websockets.client.connect(uri)
        print(green('Socket started'))

        async for message in self.socket:
            try:
                print("New Data Received ---> " + magenta(message))
                await asyncio.sleep(interval)
            except websockets.ConnectionClosed:
                continue

    async def send(self, data: str):
        print(f"Sending New Data: " + data)
        try:
            await self.socket.send(data)
            print(green(f"Data Sent Successfully: ") + data)
        except websockets.ConnectionClosedError as e:
            print(red(str(e)))

    async def price_subscribe(self):
        pass
