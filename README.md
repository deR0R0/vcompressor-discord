# VCompressor

As Discord makes more and more changes to their upload limits, the need for compressing videos become more prevalant. This discord bot allows users to upload their videos on another site, and have the video compressed down to the 10 MB limit Discord placed.

I don't know if there are any other features this bot needs, but feel free to create an issue if you want another!

## Bot invite link

[Guild Invite Link](https://discord.com/oauth2/authorize?client_id=1443725587712839702&permissions=1126176932546624&integration_type=0&scope=bot)
[User Install Link](https://discord.com/oauth2/authorize?client_id=1443725587712839702&permissions=1126176932546624&integration_type=1&scope=bot)

## Self-Hosting

1. Clone the repo
2. `cd` into the directory (most likely vcompressor-discord) after the clone
3. Create a python virtual environment using `python3 -m venv virenv`
4. Edit the `./virenv/bin/activate` script by adding the following line to it:
`export DISCORDTOKEN="token"` (ofc, replace token with your actual discord token)
5. Install all the depends: `python3 -m pip install -r requirements.txt` (if your requirements install fails on audioops, just remove it from the file)
6. If the ./src/data folder, ./src/data/jobs.json file, ./src/data/video folder does not exist, please create it
7. When hosting in a production environment (i'm using gunicorn), make sure the `IS_PRODUCTION` variable in `Config.py` is set to `True`.
8. Run the two scripts at the same time, for example, I made a run.sh script that runs both the bot and the website at the same time. Then, I configured systemd to run the run.sh script.

> [!IMPORTANT]
> If you're using systemd, make sure you set the working directory to the project folder otherwise the module imports will fail!

Final note: I also used cloudflared (cloudflare tunnels) to get my site public on my domain!

## Commands

`/video` - Creates a job and a link the user can visit to upload their videos. Bot will then send the compressed version of the video.

## Credits

https://gist.github.com/ESWZY/a420a308d3118f21274a0bc3a6feb1ff

For bitrate calculations. This is the backbone of the entire project

## Problems

These are the problems I went through while coding this project. (and how I fixed them)

1. I first made the compressor (the core part of the project). I searched online and found a stack overflow that lead to a Github Gist that explained the process. My first implementation (not a copy of the Gist) had an issue where it would always be more than the target limit I set. Though, I quickly fixed this by just simply multiplying the video bitrate by a constant ratio to fix this.
2. While trying to implement the command for the discord bot, I originally had it so the user uploaded the file on Discord. But, I quickly found out that Discord also puts a file limit on command arguments (understandable). To fix this issue, I had to redirect the user to a site that I host on a different thread.

## Future Plans

1. Chunk uploads to avoid the cloudflare tunnel's strict 100 MB upload limit. Priority: HIGH.
2. I plan on making a better way to track what part of the compression process. This can be implemented in the jobs system: storing the status as a tuple. Priority: LOW.

## Changelog

11/29/25 - Initial Bot. Probably working.
12/3/25 - Fixed production code issues.