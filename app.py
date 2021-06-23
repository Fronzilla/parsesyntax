import os
from typing import Optional, Dict

import requests
from aiohttp import web

from parsesyntax import SyntaxTree

syntax_tree = SyntaxTree()


async def _parse_syntax(link: str) -> Dict:
    """
    :param link: Целевая страница
    :return:
    """
    return await syntax_tree.get(link)


async def handle(request):
    """
    :return: Response
    """
    url: Optional[str] = request.query['url']
    try:
        result = await _parse_syntax(url)
    except requests.exceptions.ConnectionError:
        return web.json_response({'error': 'nodename nor servname provided, or not known'}, status=500)

    return web.json_response(result, status=200)


async def init():
    """
    :return: Application
    """
    app = web.Application()
    app.router.add_get("/", handle)
    return app


if __name__ == "__main__":
    application = init()
    web.run_app(application, port=os.getenv('PORT'))

# проверить размер иконки и если она квардратнеая - больний приортрирет
# Определить название бренда ?
