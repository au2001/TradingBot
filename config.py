import os
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()

DEBUG = os.environ.get("DEBUG", "false").lower() in ["true", "yes", "y", "1"]
TRAIN = os.environ.get("TRAIN", "false").lower() in ["true", "yes", "y", "1"]

CRYPTOCOMPARE_API_KEY = os.environ.get("CRYPTOCOMPARE_API_KEY", "")

COINBASE_API_KEY = os.environ.get("COINBASE_API_KEY", "")
COINBASE_SECRET_KEY = os.environ.get("COINBASE_SECRET_KEY", "")

COINBASE_VARIABLE_FEE = Decimal(os.environ.get("COINBASE_VARIABLE_FEE", "0.0149"))

CRYPTO_CURRENCY = os.environ.get("CRYPTO_CURRENCY", "BTC")
FIAT_CURRENCY = os.environ.get("FIAT_CURRENCY", "USD")
