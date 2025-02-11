
# Copyright (C) 2025 The Hyosh Coder Team @hyoshcoder (Don't Remove This Line)
# This file is part of the Hyosh Coder Team's Mega Bot.
# This file is free software: you can redistribute it and/or modify

from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()
import logging
from logging.handlers import RotatingFileHandler

# Logging
LOG_FLIENAME = "logs/mega_bot.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler(
            LOG_FLIENAME,
            maxBytes=1024**3,
            backupCount=10,
        ),
        logging.StreamHandler(),
    ],
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
TG_BOT_WORKDIR = os.getenv("TG_BOT_WORKDIR")
PORT = os.getenv("PORT")
BOT_UPTIME = datetime.now()
WEBHOOK = bool(os.getenv("WEBHOOK"))
CLONEPLUGINPATH = os.getenv("CLONEPLUGINPATH")
MEGABOTURL = os.getenv("MEGABOTURL")

# Database
DB_URI = os.getenv("DB_URI")
DB_NAME = os.getenv("DB_NAME")

# Admins
ADMINS = os.getenv("ADMINS").split(" ")


# Bot
LOG_CHANNEL = os.getenv("LOG_CHANNEL")

logger = LOGGER(__name__)

# Verifie config
if not BOT_TOKEN:
    logger.error("BOT_TOKEN is not set")
    exit(1)
if not API_ID:
    logger.error("API_ID is not set")
    exit(1)
if not API_HASH:
    logger.error("API_HASH is not set")
    exit(1)
if not DB_URI:
    logger.error("DB_URI is not set")
    exit(1)
if not DB_NAME:
    logger.error("DB_NAME is not set")
    exit(1)
if not ADMINS:
    logger.error("ADMINS is not set")
    exit(1)
if not LOG_CHANNEL:
    logger.error("LOG_CHANNEL is not set")
    exit(1)