from yt_dlp import YoutubeDL
import sys
from pathlib import Path
import logging
import inquirer
from urllib.parse import urlparse, parse_qs

def setup_logger():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def validate_url(url):
    """Validate if the URL is a proper YouTube URL"""
    try:
        parsed = urlparse(url)
        return 'youtube.com' in parsed.netloc or 'youtu.be' in parsed.netloc
    except:
        return False

def is_playlist(url):
    """Check if the URL is a playlist"""
    return 'playlist' in url or '&list=' in url

def get_user_input(is_playlist_url=False):
    """Get download preferences from user through interactive prompts"""
    questions = [
        inquirer.Text('url',
                     message="Enter the YouTube URL (video or playlist)",
                     validate=lambda _, x: validate_url(x)),
        inquirer.Text('output_path',
                     message="Enter output directory path",
                     default="downloads"),
    ]

    if is_playlist_url:
        questions.extend([
            inquirer.List('playlist_options',
                         message="Playlist download options",
                         choices=['Full playlist', 'Select range', 'Specific videos']),
            inquirer.Text('start_index',
                         message="Enter start index (e.g., 1)",
                         validate=lambda _, x: x.isdigit(),
                         ignore=lambda x: x['playlist_options'] not in ['Select range']),
            inquirer.Text('end_index',
                         message="Enter end index (e.g., 5)",
                         validate=lambda _, x: x.isdigit(),
                         ignore=lambda x: x['playlist_options'] not in ['Select range']),
            inquirer.Text('video_indices',
                         message="Enter video numbers separated by commas (e.g., 1,3,5)",
                         ignore=lambda x: x['playlist_options'] not in ['Specific videos'])
        ])

    questions.extend([
        inquirer.List('download_type',
                     message="What would you like to download?",
                     choices=['Video with Audio', 'Audio Only']),
        inquirer.List('quality',
                     message="Select quality",
                     choices=['best', '1080p', '720p', '480p', '360p'],
                     ignore=lambda x: x['download_type'] == 'Audio Only'),
        inquirer.List('audio_format',
                     message="Select audio format",
                     choices=['mp3', 'wav', 'm4a'],
                     ignore=lambda x: x['download_type'] == 'Video with Audio'),
    ])
    
    return inquirer.prompt(questions)

def get_playlist_config(preferences):
    """Configure playlist download options based on user preferences"""
    if preferences.get('playlist_options') == 'Select range':
        start = int(preferences['start_index'])
        end = int(preferences['end_index'])
        playlist_items = f"{start}-{end}"
    elif preferences.get('playlist_options') == 'Specific videos':
        playlist_items = preferences['video_indices'].replace(' ', '')
    else:
        playlist_items = None
    return playlist_items

def get_format_string(quality):
    """Generate the appropriate format string based on quality settings"""
    if quality == "best":
        return "bestvideo*+bestaudio/best"  # Best video + best audio available
    else:
        height = quality[:-1]  # Remove 'p' from quality string
        return f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"

def download_videos(url, output_path="downloads", quality="best", 
                   audio_only=False, audio_format='mp3', playlist_items=None):
    """
    Download video(s) from YouTube with specified options
    """
    logger = setup_logger()
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    ydl_opts = {
        'format': 'bestaudio/best' if audio_only else 'bestvideo+bestaudio/best',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'progress_hooks': [lambda d: logger.info(f'Downloading: {d["_percent_str"]} of {d["_total_bytes_str"]}')],
        'ignoreerrors': True,
        'no_warnings': False,
        'quiet': False,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': audio_format,
            'preferredquality': '192',
        }] if audio_only else []
    }

    if playlist_items:
        if '-' in playlist_items:
            start, end = map(int, playlist_items.split('-'))
            ydl_opts['playliststart'] = start
            ydl_opts['playlistend'] = end
        else:
            ydl_opts['playlist_items'] = playlist_items

    try:
        logger.info(f"Starting download from: {url}")
        with YoutubeDL(ydl_opts) as ydl:
            # Get video/playlist information
            info = ydl.extract_info(url, download=False)
            
            if 'entries' in info:  # It's a playlist
                logger.info(f"Playlist: {info.get('title', 'Unknown Playlist')}")
                logger.info(f"Number of videos: {len(info['entries'])}")
                if playlist_items:
                    logger.info(f"Downloading videos: {playlist_items}")
            else:  # Single video
                logger.info(f"Title: {info.get('title', 'Unknown Title')}")
                logger.info(f"Duration: {info.get('duration', 0)//60}:{info.get('duration', 0)%60:02d}")
            
            if input("\nProceed with download? (y/n): ").lower() != 'y':
                logger.info("Download cancelled by user")
                return False
            
            ydl.download([url])
            
        logger.info("Download completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return False

def main():
    """Main function to run the interactive downloader"""
    print("\n=== YouTube Downloader ===\n")
    
    while True:
        # Get initial URL to check if it's a playlist
        url = input("Enter YouTube URL (video or playlist): ")
        is_playlist_url = is_playlist(url)
        
        # Get all preferences
        preferences = get_user_input(is_playlist_url)
        
        # Process the preferences
        audio_only = preferences['download_type'] == 'Audio Only'
        quality = preferences['quality'] if not audio_only else 'best'
        audio_format = preferences['audio_format'] if audio_only else 'mp3'
        
        # Handle playlist configuration
        playlist_items = None
        if is_playlist_url and preferences.get('playlist_options'):
            playlist_items = get_playlist_config(preferences)
        
        # Perform the download
        success = download_videos(
            preferences['url'],
            preferences['output_path'],
            quality=quality,
            audio_only=audio_only,
            audio_format=audio_format,
            playlist_items=playlist_items
        )
        
        if input("\nWould you like to download another video/playlist? (y/n): ").lower() != 'y':
            print("\nThank you for using YouTube Downloader!")
            break

if __name__ == "__main__":
    main()
