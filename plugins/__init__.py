"""
Copyright (C) 2025 The Hyosh Coder Team @hyoshcoder (Don't Remove This Line)
This file is part of the Hyosh Coder Team's Mega Bot.
This file is free software: you can redistribute it and/or modify
"""



from aiohttp import web
from .route import route

async def web_server():
    web_app = web.Application(client_max_size=1024**3)
    web_app.add_routes(route)
    return web_app