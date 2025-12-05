import discord, asyncio, os, re

from src.utils.compressor import async_compress
from src.utils.jobmanager import add_job, remove_job_by_user, get_job_id
from src.Global import client
from src.Config import UPLOAD_LINK, VIDEO_FOLDER, SUPPORTED_TYPES
from src.utils.exceptions import InvalidFileTypeError, BitrateTooLowError, TooManyAttemptsError

class LinkWebsite(discord.ui.View):
    def __init__(self, job_id: int, original_user: discord.User):
        super().__init__(timeout=30)
        self.button = discord.ui.Button(label="Upload", style=discord.ButtonStyle.url, url=f"{UPLOAD_LINK}?job_id={str(job_id)}")
        self.add_item(self.button)
        self.original_user = original_user

    async def on_timeout(self):
        remove_job_by_user(self.original_user.id) # prio removing the job incase the bottom fails
        # delete message if they wait too long..
        if self.message:
            try:
                await self.message.delete()
            except discord.NotFound:
                pass
        
def remove_trash(file1: str, file2: str):
    try:
        os.remove(file1)
        os.remove(file2)
    except FileNotFoundError:
        pass

@client.tree.command(name="video", description="Compresses a video file to the 10 MB discord limit then sends it.")
async def video(interaction: discord.Interaction):

    # send a message so we can edit it later
    await interaction.response.send_message(content="Hold on a sec...")
    message: discord.InteractionMessage = await interaction.original_response()

    # create a new job
    job_id = add_job(interaction.user.id)

    if job_id == -1:
        await message.edit(content="Sorry, you currently already have a job going. Please fulfill it or cancel it.")
        return
    
    await message.edit(content=":hourglass: Waiting for your upload. Look for another message by the bot!")

    # send the button as a ephmeral
    upload_button = await interaction.followup.send(content="Click the upload button and upload your video on the website!", view=LinkWebsite(job_id, interaction.user), ephemeral=True)

    checks = 0
    video_file = None

    # continuously check for the upload
    while True:
        checks += 1

        # check for the file
        video_folder_abs = os.path.abspath(VIDEO_FOLDER)
        for file in os.listdir(video_folder_abs):
            if file.startswith(str(interaction.user.id)):
                video_file = file
                
        if video_file:
            video_path = os.path.join(VIDEO_FOLDER, video_file)
            await upload_button.delete()
            break

        # waited too long
        if checks > 10:
            await message.edit(content=":cry: You made me wait too long... Job canceled")
            remove_job_by_user(interaction.user.id)
            return
        
        await asyncio.sleep(3)


    # uploaded the file?
    # update the user on the current process and
    # start the compression status

    # remove the job first
    remove_job_by_user(interaction.user.id)

    # notify user
    await message.edit(content=":white_check_mark: Recieved your file!", view=None)
    await asyncio.sleep(1)
    await message.edit(content=":gear: Compressing your video right now...")

    compressed_file = os.path.join(os.path.abspath(VIDEO_FOLDER), f"{str(interaction.user.id)}_compressed.mp4")

    # actually start compressing
    try:
        await async_compress(video_path, compressed_file, 10)
    except (InvalidFileTypeError, FileNotFoundError) as e:
        await message.edit(content=f":x: Couldn't process this file. Error: `{e}`")
        remove_trash(compressed_file, video_path)
        return
    except BitrateTooLowError as e:
        await message.edit(content=f":x: Compression failed: `{e}`")
        remove_trash(compressed_file, video_path)
        return
    except TooManyAttemptsError as e:
        await message.edit(content=f":x: Compression failed: `{e}`")
        remove_trash(compressed_file, video_path)
        return
    except Exception as e:
        await message.edit(content=f":x: Critical Error has occured! `{e}`")
        remove_trash(compressed_file, video_path)
        return

    await message.edit(content=":white_check_mark: Successfully Compressed!")

    await asyncio.sleep(1)
    
    await message.edit(content=":inbox_tray: Uploading your video now...")

    await message.edit(content=":wave: Your video has arrived!", attachments=[discord.File(compressed_file)])


    # clean up files
    remove_trash(compressed_file, video_path)