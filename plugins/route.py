# Copyright (C) 2025 The Hyosh Coder Team @hyoshcoder (Don't Remove This Line)
# This file is part of the Hyosh Coder Team's Mega Bot.
# This file is free software: you can redistribute it and/or modify


from aiohttp import web


route = web.RouteTableDef()

@route.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("Megabot is running")