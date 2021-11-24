pip uninstall asyncio
python -m aiohttp.web -H 0.0.0.0 -P 8000 app:get_app
