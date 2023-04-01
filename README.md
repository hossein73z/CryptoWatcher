**Still In Development**

My app to monitor cryptocurrency coin and token prices and set alert for them.
For now, you can add new crypto pairs to database and watch price on your browser

install requirements and run `python manage.py runproject`

Used **Django** for web interface, **websockets** for connecting to KuCoin API (Binance is not accessible in my region) and async coroutines to make these work together.

ToDos:
  - Connect telegram bot for management and alert and stuff
  - Make an easy interface for put orders in the exchange
  - calculate realized and unrealized profit and loss
  - change take-profit and stop-loss orders based on the real-time price of the crypto pairs
  - I don't have anything more in mind for now, but sky is the limit 😂😂
