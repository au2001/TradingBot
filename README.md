# TradingBot

## Disclamer

**DO NOT USE THIS BOT. If you do, it is at your own risk.**\
**Only give it access to money you are willing to loose.**

## Explanation

This is an attempt at creating an *artificial intelligence* which trades automatically [Bitcoin](https://bitcoin.org/en/) (or, in fact, any cryptocurrency) on the [Coinbase](https://www.coinbase.com) platform.\
It uses [Keras](https://keras.io) and [TensorFlow](https://www.tensorflow.org) for neural networks and [CryptoCompare](https://www.cryptocompare.com) for historical data about cryptocurrency prices.

## Installing

To install the bot and make it run on your computer, follow these steps:
1. Clone or download the repository with `git clone git@github.com:au2001/TradingBot.git`
2. Go to the folder of this repository with `cd TradingBot`
3. Install Python [Virtualenv](https://virtualenv.pypa.io/en/stable/installation.html) with `pip install virtualenv` (recommended)
4. Create a virtual environement with `virtualenv venv` (recommended)
5. Activate the virtual environement with `source venv/bin/activate` (recommended)
6. Install the required dependencies with `pip install -r requirements.txt`
7. Deactivate the virtual environement with `deactivate` (recommended)
8. Create an environement file with `echo "COINBASE_API_KEY=xxx\nCOINBASE_SECRET_KEY=xxx\nCRYPTOCOMPARE_API_KEY=xxx" > .env` (recommended)

The bot installed, but some API keys are required for the bot to work correctly. See below.

## Setup

Once the bot is successfully installed, you need to configure its API accesses.\
This is done through environment variables.\
Note that theys keys must be kept secure as **they allow to wire money** from and to your wallets as well as registered credit cards and bank accounts **without any other confirmation**.

The easiest way is to use the `.env` file creating in the last step of the *Installing* part above.\
Open this file in your favorite editor and you should see the following:
> COINBASE_API_KEY=xxx\
> COINBASE_SECRET_KEY=xxx\
> CRYPTOCOMPARE_API_KEY=xxx

### Coinbase

To obtain your Coinbase API key and secret key, head to the [API settings](https://www.coinbase.com/settings/api) on Coinbase.\
There, create a new API key with access to at least **one cryptocurrency wallet (BTC)** and **one fiat wallet (USD)** as well as the permissions **`wallet:accounts:read`**, **`wallet:payment-methods:read`**, **`wallet:buys:create`** and **`wallet:sells:create`**.\
Your API key and secret key will be shown only once, so make sure to copy them in a secure location and then insert them in the environment variables.

### Cryptocompare

To obtain your Cryptocompare API key, first [create an account on Cryptocompare](https://www.cryptocompare.com).\
Then, head over to the [API keys tab](https://www.cryptocompare.com/cryptopian/api-keys), create a new API key with at least the permission **Poll Live and Historical Data** (**`r_price_poll_basic`**).\
You can then click *Copy* next to your newly created API key and paste it into the dedicated environment variable.

## Performance

### Current status

After several hours of training on a decent rig, the bot arrived to the following strategy:
> Predicted yield over 30 days: 0.00%\
> Investing 0% in cryptocurrency...

Meaning, the optimal startegy is not to invest at all in cryptocurrencies (Bitcoin in this case).

### Possible improvements

To obtain better results, a better training method is required.\
Unfortunately, expanding on the current model leads to an extremely slow training due to a bottleneck in the Python code (not on [Keras]()/[TensorFlow]()'s side).\
Thus adding more neurons, improving the evaluation function or increasing the evolution strategy's performance requires a complete rewrite of the training.
