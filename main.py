import asyncio
import os

import django


async def main():
    from KuCoin import KuCoin

    process = await asyncio.create_subprocess_shell(r"python manage.py runserver")
    await asyncio.sleep(2)
    print('##############################')

    loop = asyncio.get_event_loop()
    uri = 'wss://ws.postman-echo.com/raw'
    kucoin = KuCoin(uri)
    task = asyncio.create_task(kucoin.start_listening())

    while True:
        input_data = await loop.run_in_executor(None, input)


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CryptoWatcher.settings')
    django.setup()
    asyncio.run(main())
