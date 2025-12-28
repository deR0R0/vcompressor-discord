# PRODUCTION?
IS_PRODUCTION = False

# config vars for video compression
MIN_AUDIO_BITRATE = 32_000

# video stuff
VIDEO_FOLDER = "./src/data/videos/"
SUPPORTED_TYPES = ["mp4", "avi", "mov", "mkv", "flv", "asf", "ogg"]

# job handling

JOB_DATA_FILE = "./src/data/jobs.json"

# link config
UPLOAD_LINK = "http://localhost:1234/upload"

# commands

# COMMAND: video
VIDEO_TARGET_SIZE_MB = 10  # target size in MB for discord uploads
UPLOAD_TIMEOUT_SECONDS = 180  # time to wait for user to upload video