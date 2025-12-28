import os
import ffmpeg
import asyncio
from src.utils.exceptions import BitrateTooLowError, InvalidFileTypeError, TooManyAttemptsError
from src.Config import MIN_AUDIO_BITRATE



def compress_video(absolute_path: str, output_path: str, target_size_mb: int, size_ratio: float = 1.0, max_attempts: int = 3) -> str | None:
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

    # get audio bitrate
    audio_stream = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
    audio_bitrate = float(audio_stream['bit_rate']) if audio_stream and audio_stream.get('bit_rate') else 0.0

    # clamp the audio bitrate to min
    audio_bitrate = MIN_AUDIO_BITRATE

    # calculate total bitrate in bps. includes both audio AND video
    # target_size_mb * 1024 (kb) * 1024 (bytes) * 8 (bits) / (duration (seconds)
    target_bitrate_total = (target_size_mb * 1024 * 1024 * 8) / duration

    # make sure audio bitrate is not more than 5% of total bitrate
    if 20 * audio_bitrate > target_bitrate_total:
        audio_bitrate = target_bitrate_total / 20 # prio video quality over audio quality

    # find target video bitrate
    video_bitrate = target_bitrate_total - audio_bitrate

    # add an adaptive buffer based on duration
    buffer = 0.95 # default buffer
    buffer -= (0.005 * ((duration // 60) + 1)) # reduce buffer by 0.5% for every minute of video
    buffer = max(buffer, 0.7) # clamp to minimum of 70%
    video_bitrate = int(video_bitrate * buffer * size_ratio) # give some buffer for the container overhead
    
    # start ffmpeg compression
    video = ffmpeg.input(absolute_path)

    # we're just going to do the two pass method for all videos
    ffmpeg.output(video, os.devnull,
                    **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}
                  ).overwrite_output().run(quiet=True)
    ffmpeg.output(video, output_path,
                    **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac', 'b:a': int(audio_bitrate), 'movflags': '+faststart', 'maxrate': video_bitrate * 1.5, 'bufsize': video_bitrate * 2}
                  ).overwrite_output().run(quiet=True)
    
    if os.path.getsize(output_path) > target_size_mb * 1024 * 1024:
        print(f"Attempting to compress video: {absolute_path} again. Size is {os.path.getsize(output_path)} bytes, target is {target_size_mb * 1024 * 1024} bytes.")
        # calculate new size ratio
        size_ratio = size_ratio * (target_size_mb * 1024 * 1024) / os.path.getsize(output_path)
        # attempt to compress it again
        return compress_video(absolute_path, output_path, target_size_mb, size_ratio=size_ratio - 0.08, max_attempts=max_attempts - 1)
    elif os.path.getsize(output_path) <= target_size_mb * 1024 * 1024:
        return output_path
    else:
        return None


async def async_compress(absolute_path: str, output_path: str, target_size_mb: int, max_attempts: int = 3) -> str | None:
    return await asyncio.to_thread(compress_video, absolute_path, output_path, target_size_mb, max_attempts)


if __name__ == "__main__":
    def test_compress(filename: str):
        # for testing purposes
        input_path = f"./src/data/videos/{filename}.mp4"
        output_path = f"./src/data/videos/{filename}_compressed.mp4"
        target_size = 10

        try:
            result = compress_video(input_path, output_path, target_size)
            if result:
                print(f"Video compressed successfully: {result}")
            else:
                print("Failed to compress video to the target size.")
        except Exception as e:
            print(f"Error during compression: {e}")

    test_compress("test_standard_video")
    test_compress("test_large_video")