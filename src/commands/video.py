import discord, asyncio, os

from src.utils.compressor import compress_video
from src.utils.jobmanager import add_job, remove_job, get_job_id
from src.Global import client
from src.Config import UPLOAD_LINK, VIDEO_FOLDER, SUPPORTED_TYPES

class LinkWebsite(discord.ui.View):
    def __init__(self, job_id: int, original_user: discord.User):
        super().__init__(timeout=30)
        self.button = discord.ui.Button(label="Upload", style=discord.ButtonStyle.url, url=f"{UPLOAD_LINK}?job_id={str(job_id)}")
        self.add_item(self.button)
        self.original_user = original_user

    async def on_timeout(self):
        remove_job(get_job_id(self.original_user.id)) # prio removing the job incase the bottom fails
        # delete message if they wait too long..
        if self.message:
            try:
                await self.message.delete()
            except discord.NotFound:
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
    await interaction.followup.send(content="Click the upload button and upload your video on the website!", view=LinkWebsite(job_id, interaction.user), ephemeral=True)

    checks = 0

    # continuously check for the upload
    while True:
        checks += 1

        # check for the file
        user_id_str = str(interaction.user.id)
        video_file = next(
            (
                name
                for name in os.listdir(VIDEO_FOLDER)
                if name.startswith(user_id_str)
                and os.path.splitext(name)[1].lower() in SUPPORTED_TYPES
                and os.path.isfile(os.path.join(VIDEO_FOLDER, name))
            ),
            None,
        )
        if video_file:
            video_path = os.path.join(VIDEO_FOLDER, video_file)
            break

        if checks > 10:
            await message.edit(content=":cry: You made me wait too long... Job canceled")
            remove_job(interaction.user.id)
            return
        
        await asyncio.sleep(3)


    # uploaded the file?
    # update the user on the current process and
    # start the compression status

    # remove the job first
    remove_job(get_job_id(interaction.user.id))

    # notify user
    await message.edit(content=":white_check_mark: Recieved your file!", view=None)
    await asyncio.sleep(1)
    await message.edit(content=":gear: Compressing your video right now...")


    # actually start compressing
    



    """
    # make a custom loading response
    await interaction.response.send_message(f":white_check_mark: {interaction.user.mention} just uploaded a video. Compressing now...")

    original_message = await interaction.original_response()

    await asyncio.sleep(1)

    await original_message.edit(content=f":envelope_with_arrow: {interaction.user.mention} Downloading compressed video...")
    
    # download the file
    folder_path = os.path.abspath("./src/data/videos/")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path) # make folder if doesn't exist

    absolute_path = os.path.join(folder_path, f"{interaction.user.id}.{file.filename[file.filename.rfind('.'):]}")

    await file.save(absolute_path)

    # compressing
    await original_message.edit(content=f":gear: {interaction.user.mention} Compressing video...")

    compress_video(absolute_path, os.path.join(folder_path, f"compressed_{interaction.user.id}.mp4"), target_size_mb=1)

    # send the compressed video
    await original_message.edit(content=f":inbox_tray: {interaction.user.mention} Uploading compressed video...")
    await interaction.followup.send(file=discord.File(os.path.join(folder_path, f"compressed_{interaction.user.id}.mp4")))

    # remove the files
    os.remove(absolute_path)
    os.remove(os.path.join(folder_path, f"compressed_{interaction.user.id}.mp4"))
    """