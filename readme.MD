# YouTube Video Downloader

This Python script allows you to download YouTube videos or playlists with options for selecting video quality or extracting audio only.

## Prerequisites

Before running the script, ensure you have the following installed on your Windows system:

1. **Python**: Make sure Python is installed. You can download it from the [official Python website](https://www.python.org/downloads/).

2. **Required Python Packages**:
   - `yt-dlp`: A feature-rich YouTube downloader.
   - `inquirer`: A collection of common interactive command-line user interfaces.

   Install these packages using `pip`:

   ```bash
   pip install yt_dlp
   pip install inquirer
   ```

3. **FFmpeg**: A complete solution to record, convert, and stream audio and video. It's required for processing media files.

   Install FFmpeg using `winget`:

   ```bash
   winget install ffmpeg
   ```

   Alternatively, you can download the installer from the [official FFmpeg website](https://getffmpeg.org/) and follow the installation instructions.

## Usage

1. **Clone the Repository**:

   Download or clone this repository to your local machine.

2. **Run the Script**:

   Open a command prompt, navigate to the directory containing the script, and execute:

   ```bash
   python your_script_name.py
   ```

   Follow the on-screen prompts to enter the YouTube URL and select your download preferences.

## Notes

- Ensure that the `ffmpeg` executable is in your system's PATH. If you installed FFmpeg using `winget`, this should be configured automatically.

- For detailed information on `yt-dlp` and its capabilities, refer to the [yt-dlp GitHub repository](https://github.com/yt-dlp/yt-dlp).

- If you encounter issues with `inquirer`, consult its [GitHub page](https://github.com/magmax/python-inquirer) for troubleshooting and support.

By following these steps, you should be able to download YouTube videos or audio seamlessly using the provided Python script. 