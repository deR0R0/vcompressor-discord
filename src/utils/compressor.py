import os
import ffmpeg
import asyncio
from src.utils.exceptions import BitrateTooLowError, InvalidFileTypeError, TooManyAttemptsError
from src.Config import MIN_VID_BITRATE, MIN_AUDIO_BITRATE, MAX_AUDIO_BITRATE



def compress_video(absolute_path: str, output_path: str, target_size_mb: int, max_attempts: int = 3) -> str | None:
    """
    Compresses video files to a target size using ffmpeg.
    Credits to https://gist.github.com/ESWZY/a420a308d3118f21274a0bc3a6feb1ff for bitrate calculation method.
    """

    # add a check for max attempts
    if max_attempts <= 0:
        raise TooManyAttemptsError("Maximum compression attempts exceeded.")

    # check to make sure if the video file exists
    if not os.path.isfile(absolute_path):
        raise FileNotFoundError(f"File not found: {absolute_path}")
    
    # check to see if the video file is a good format we can use.
    if not absolute_path.lower().endswith(("mp4", "avi", "mov", "mkv", "flv", "asf", "ogg")):
        raise InvalidFileTypeError(f"Invalid file type: {absolute_path[absolute_path.rfind('.'):]}")
    
    # create a probe to get a buncha video information
    probe = ffmpeg.probe(absolute_path)

    # get vid duration
    duration = float(probe['format']['duration'])

    # get vid resolution
    video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
    if video_stream is None:
        raise InvalidFileTypeError("No video stream found.")
    width = int(video_stream['width'])
    height = int(video_stream['height'])
    resolution = min(width, height)

    # get audio bitrate
    audio_stream = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
    audio_bitrate = float(audio_stream['bit_rate']) if audio_stream and audio_stream.get('bit_rate') else 0.0


    # calculate total bitrate in bps. includes both audio AND video
    # target_size_mb * 1024 (kb) * 1024 (bytes) * 8 (bits) / (duration (seconds)
    target_bitrate_total = (target_size_mb * 1024 * 1024 * 8) / duration

    # find minimum video bitrate based on resolution
    if resolution > 2160:
        min_vid_bitrate = MIN_VID_BITRATE["above"]
    elif resolution > 1440:
        min_vid_bitrate = MIN_VID_BITRATE["2160"]
    elif resolution > 1080:
        min_vid_bitrate = MIN_VID_BITRATE["1440"]
    elif resolution > 720:
        min_vid_bitrate = MIN_VID_BITRATE["1080"]
    else:
        min_vid_bitrate = MIN_VID_BITRATE["720"]

    # calculate bare minimum total bitrate
    bare_min_total_bitrate = min_vid_bitrate + audio_bitrate

    # clamp audio bitrate to allowed range while respecting total target size
    if target_bitrate_total > MIN_AUDIO_BITRATE and audio_bitrate < MIN_AUDIO_BITRATE:
        audio_bitrate = MIN_AUDIO_BITRATE
    elif audio_bitrate > MAX_AUDIO_BITRATE:
        audio_bitrate = MAX_AUDIO_BITRATE

    if target_bitrate_total < bare_min_total_bitrate:
        print(resolution, min_vid_bitrate, audio_bitrate, target_bitrate_total)
        raise BitrateTooLowError(f"Calculated bitrate {target_bitrate_total}bps is too low. Minimum is {bare_min_total_bitrate}bps. Try shortening video length.")
    
    # in the original github gist, the user found the best min size
    # but it was pointless (because they just printed out a warning)
    # so we're just going to go ahead and just compress the video

    # find target audio bitrate
    if 10 * audio_bitrate > target_bitrate_total:
        audio_bitrate = target_bitrate_total / 10

    # find target video bitrate
    video_bitrate = target_bitrate_total - audio_bitrate
    video_bitrate = int(video_bitrate * 0.92) # give some buffer for the container overhead
    if video_bitrate < min_vid_bitrate:
        raise BitrateTooLowError(f"Calculated video bitrate {video_bitrate}kbps is too low. Minimum is {min_vid_bitrate}kbps. Try shortening video length.")
    
    # start ffmpeg compression

    video = ffmpeg.input(absolute_path)

    # we're just going to do the two pass method for all videos
    ffmpeg.output(video, os.devnull,
                    **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}
                  ).overwrite_output().run(quiet=True)
    ffmpeg.output(video, output_path,
                    **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac', 'b:a': int(audio_bitrate)}
                  ).overwrite_output().run(quiet=True)
    
    if os.path.getsize(output_path) > target_size_mb * 1024 * 1024:
        # attempt to compress it again
        return compress_video(absolute_path, output_path, target_size_mb, max_attempts - 1)
    elif os.path.getsize(output_path) <= target_size_mb * 1024 * 1024:
        return output_path
    else:
        return None


async def async_compress(absolute_path: str, output_path: str, target_size_mb: int, max_attempts: int = 3) -> str | None:
    return await asyncio.to_thread(compress_video, absolute_path, output_path, target_size_mb, max_attempts)