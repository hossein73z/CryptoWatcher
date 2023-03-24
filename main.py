import asyncio

from KuCoin import KuCoin


async def main():
    process = await asyncio.create_subprocess_shell(r"python manage.py runserver")
    await asyncio.sleep(2)
    print('##############################')

    loop = asyncio.get_event_loop()
    uri = 'wss://ws.postman-echo.com/raw'
    kucoin = KuCoin(uri)
    task = asyncio.create_task(kucoin.start_listening())

    while True:
        input_data = await loop.run_in_executor(None, input)
        if input_data == "123":
            await kucoin.subscribe()
        else:
            await kucoin.send(input_data)


if __name__ == '__main__':
    asyncio.run(main())
