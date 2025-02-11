
# Copyright (C) 2025 The Hyosh Coder Team @hyoshcoder (Don't Remove This Line)
# This file is part of the Hyosh Coder Team's Mega Bot.
# This file is free software: you can redistribute it and/or modify

from bot import Bot
import pyrogram.utils

pyrogram.utils.MIN_CHANNEL_ID = -1002175858655

if __name__ == "__main__":
    Bot().run()