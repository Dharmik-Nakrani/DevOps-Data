import yt_dlp

def download_playlist(playlist_url, output_path='downloads/%(title)s.%(ext)s'):
    options = {
        'format': 'bestvideo+bestaudio/best',  # Highest quality video and audio
        'outtmpl': output_path,  # Output file format
        'merge_output_format': 'mp4',  # Ensure output is MP4
        'noplaylist': False,  # Download the full playlist
        'quiet': False,  # Show progress
    }
    
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([playlist_url])

if __name__ == "__main__":
    playlist_url = input("Enter YouTube playlist URL: ")
    download_playlist(playlist_url)
