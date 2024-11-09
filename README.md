# PyMediaPlayer
**PyMediaPlayer** is a simple Python-based media player GUI for playing video files with customizable playback options. This application uses pygame for video playback.

## Features
- Play video files of various formats including MP4, AVI, MOV, MKV, and others.
- Adjust playback settings like volume and frames per second (FPS).
- Loop videos and cache videos for faster reloading.
- Control visibility of playback status.

## Prerequisites

- Python 3.10 or higher.
- Required modules: pygame, tkinter pygvideo, lib-pygame-ui.

## Installation
Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
Launch the GUI by running the following command in your terminal:
```bash
python PyMediaPlayer.py
```

## GUI Controls
1. Open Video File: A file dialog will appear for selecting a video file if a path isn't provided via command-line.
2. Playback Options:
    - **Play/Pause**: Controls to start and pause video playback.
    - **Volume Control**: Slider to adjust the audio volume (range: 0.0 to 1.0, in-UI: 0 to 100).
    - **Loop Playback**: Toggle to repeat the video once it finishes.
    - **Hide Status**: Option to hide the video status information.
    - Command-Line Options

## Command-Line Options
The GUI can also be customized using the following command-line arguments:

- `video_path`: Path to the video file.
- `-l` or `--loop`: Enable looping.
- `-c` or `--cache`: Cache the video on load.
- `-hs` or `--hide-status`: Hide the video status.
- `-vol` or `--volume`: Set volume level (default: 1).
- `-fps`: Set frames per second (default: 24).

## Example
```bash
python PyMediaPlayer.py apt.mp4 -l -vol 0.8 -fps 30
```