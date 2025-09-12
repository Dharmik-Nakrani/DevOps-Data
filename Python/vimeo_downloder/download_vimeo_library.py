import requests
import os

ACCESS_TOKEN = '8d6e1be9c11fda74e2c3eba0211ea478'  # Replace with your Vimeo personal access token
DOWNLOAD_FOLDER = 'vimeo_downloads'
PER_PAGE = 10  # Number of videos per page to fetch

def ensure_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)

def get_videos(page=1):
    url = f'https://api.vimeo.com/me/videos?page={page}&per_page={PER_PAGE}'
    headers = {
        'Authorization': f'bearer {ACCESS_TOKEN}',
        'Accept': 'application/vnd.vimeo.*+json;version=3.4',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def download_video(video):
    title = video['name']
    downloads = video.get('download', [])
    if not downloads:
        print(f"⚠️ No downloadable files for: {title}")
        return

    # Get the best resolution
    best = sorted(downloads, key=lambda x: int(x.get('height', 0)), reverse=True)[0]
    video_url = best['link']
    file_ext = video_url.split('?')[0].split('.')[-1]
    safe_title = ''.join(c if c.isalnum() else '_' for c in title)
    filepath = os.path.join(DOWNLOAD_FOLDER, f"{safe_title}.{file_ext}")

    if os.path.exists(filepath):
        print(f"⏭️ Skipping '{title}' - file already exists at: {filepath}")
        return
    
    print(f"⬇️ Downloading '{title}' at {best['quality']} resolution...")

    with requests.get(video_url, stream=True) as r:
        r.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    print(f"✅ Saved to: {filepath}")

def main():
    ensure_folder(DOWNLOAD_FOLDER)
    page = 1
    while True:
        data = get_videos(page)
        videos = data.get('data', [])
        if not videos:
            break
        for video in videos:
            download_video(video)
        if data['paging']['next'] is None:
            break
        page += 1

if __name__ == '__main__':
    main()