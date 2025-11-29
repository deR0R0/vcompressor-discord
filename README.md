# VCompressor

As Discord makes more and more changes to their upload limits, the need for compressing videos become more prevalant. This discord bot allows users to upload their videos on another site, and have the video compressed down to the 10 MB limit Discord placed.

I don't know if there are any other features this bot needs, but feel free to create an issue if you want another!

## Bot invite link

**Currently None** - I'll update this repo once I find a reliable hosting method.

## Self-Hosting

Just fork the repo and run the main.py file. In VSCode, make sure to set the CWD as the directory you opened.

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

I plan on making a better way to track what part of the compression process. This can be implemented in the jobs system: storing the status as a tuple. (?)

## Changelog

11/29/25 - Initial Bot. Probably working.