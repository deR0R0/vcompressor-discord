import os
import threading
from src.Global import client
from src.Config import IS_PRODUCTION


# load commands

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    print(f"Synced {len(await client.tree.sync())} commands.")

if __name__ == "__main__":
    if not IS_PRODUCTION:
        print("CURRENTLY RUNNING DEVELOPMENT VERSION. PLEASE DO NOT RUN THIS AS PRODUCTION BUT RATHER USE WSGI ON THE WEB SERVER.")
        from src.webserver.app import run # import the webserver run function
        t = threading.Thread(target=run)
        t.start()
    client.run(os.environ.get("DISCORDTOKEN"))