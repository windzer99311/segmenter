import subprocess,os
INPUT_FILE = "segmented_file/song.mp3"
OUTPUT_DIR = "segmented_file"
def create_segmented_file():
    cmd = [
        "ffmpeg",
        "-y",
        "-i", INPUT_FILE,
        "-map", "0:a",
        "-c:a", "aac",
        "-b:a", "128k",
        "-f", "dash",
        "-seg_duration", "2",
        "-use_template", "1",
        "-use_timeline", "1",
        "-init_seg_name", f"{OUTPUT_DIR}/init.mp4",
        "-media_seg_name", f"{OUTPUT_DIR}/chunk-stream0-$Number%05d$.m4s",
        os.path.join(f"{OUTPUT_DIR}", "manifest.mpd"),
    ]
    subprocess.run(cmd, check=True)
