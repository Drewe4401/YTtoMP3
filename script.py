import os
import re
import subprocess
import sys
import yt_dlp

def set_ffmpeg_path():
    """
    Set the FFmpeg executable path explicitly by adding it to the system PATH.
    Update the path below to point to your FFmpeg 'bin' directory.
    """
    ffmpeg_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg", "bin")
    if ffmpeg_dir not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + ffmpeg_dir
    print("FFmpeg path set to:", ffmpeg_dir)

set_ffmpeg_path()

def sanitize_folder_name(name):
    """
    Sanitizes the folder name by removing or replacing invalid characters.
    """
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def get_playlist_name(playlist_url):
    """
    Extracts the playlist name (album name) using yt-dlp's metadata extraction.
    """
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
            return info.get('title', 'Unknown Playlist')
    except Exception as e:
        print(f"Error fetching playlist info: {e}")
        return 'Unknown Playlist'

def download_youtube_playlist_audio(playlist_url, output_folder):
    """
    Downloads only the audio from a YouTube playlist or video.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'ignoreerrors': True,
        'quiet': False,
        'noplaylist': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([playlist_url])
    except Exception as e:
        print(f"An error occurred while downloading the playlist: {e}")

def copy_folder_to_network_share(source_folder, network_path):
    """
    Copies a folder to a specified network location using xcopy (Windows).
    """
    if not os.path.exists(source_folder):
        print(f"Error: Source folder {source_folder} does not exist.")
        return

    try:
        # Use xcopy command for Windows
        command = f'xcopy "{source_folder}" "{network_path}" /E /I /Y'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Folder successfully copied to {network_path}")
        else:
            print(f"Error copying folder: {result.stderr}")
    except Exception as e:
        print(f"An error occurred while copying the folder: {e}")

def process_playlist(playlist_url):
    """
    Process the download and copy operations for a YouTube playlist or video.
    """
    album_name = get_playlist_name(playlist_url)
    sanitized_album_name = sanitize_folder_name(album_name)
    # Save the downloaded audio to a folder named after the album in the current working directory.
    output_folder = os.path.join(os.getcwd(), sanitized_album_name)
    
    print(f"\n🎵 Downloading: {album_name}")
    print(f"📁 Saving to: {output_folder}\n")
    
    download_youtube_playlist_audio(playlist_url, output_folder)
    

if __name__ == "__main__":
    print("🔊 YouTube Audio Downloader")
    print("---------------------------")
    url = input("Enter the YouTube video/playlist URL: ").strip()

    if url:
        process_playlist(url)
        print("\n✅ Done! Exiting...")
        sys.exit(0)
    else:
        print("❌ No URL provided. Exiting.")
        sys.exit(1)

