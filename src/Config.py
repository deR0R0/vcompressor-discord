# config vars for video compression
GIBIBYTE_TO_GIGABYTE_CONSTANT = (1024 ** 3) / (1000 ** 3)
MIN_AUDIO_BITRATE = 64_000  # in bps (bare minimum)
MAX_AUDIO_BITRATE = 96_000  # in bps (bare minimum)
MIN_VID_BITRATE = {
    "720": 250_000,
    "1080": 500_000,
    "1440": 1_000_000,
    "2160": 2_000_000,
    "above": 4_000_000
}

# video stuff
VIDEO_FOLDER = "./src/data/videos/"
SUPPORTED_TYPES = ["mp4", "avi", "mov", "mkv", "flv", "asf", "ogg"]

# job handling

JOB_DATA_FILE = "./src/data/jobs.json"

# link config
UPLOAD_LINK = "http://localhost:1234/upload"