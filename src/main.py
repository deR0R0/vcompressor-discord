import os
import threading
import src.Global # load global vars
from src.Global import client
from src.Config import IS_PRODUCTION

from src.utils.compressor import compress_video
from src.utils.jobmanager import add_job, remove_job, get_all_jobs

# load commands
from src.commands import video

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