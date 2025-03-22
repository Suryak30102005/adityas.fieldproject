from flask import Flask, request, render_template, jsonify, send_from_directory
import instaloader
import re
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for flash messages in audio routes

# Global counters for each brand
brand_counters = {
    "krishv.things": 0,
    "krishv.dev": 0
}

# Configure Instaloader to download posts into "downloads/{target}"
L = instaloader.Instaloader(dirname_pattern='downloads/{target}', download_videos=True)

def extract_shortcode(url):
    """
    Extract the Instagram shortcode from URLs with /p/, /reel/ or /tv/ paths.
    """
    match = re.search(r"instagram\.com/(?:p|reel|tv)/([^/?]+)", url)
    return match.group(1) if match else None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_media():
    global brand_counters
    url = request.form.get('url')
    brand = request.form.get('brand')
    if brand not in brand_counters:
        return jsonify({'status': 'error', 'message': 'Invalid brand selected'}), 400

    shortcode = extract_shortcode(url)
    if not shortcode:
        return jsonify({'status': 'error', 'message': 'Invalid Instagram URL'}), 400

    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target=shortcode)
        
        # Folder for this post
        folder_path = os.path.join('downloads', shortcode)
        if not os.path.isdir(folder_path):
            return jsonify({'status': 'error', 'message': 'Download folder not found'}), 500

        files = os.listdir(folder_path)
        download_file = None
        # Prefer video files if available
        for f in files:
            if f.endswith('.mp4'):
                download_file = f
                break
        if not download_file:
            for f in files:
                if f.endswith('.jpg'):
                    download_file = f
                    break
        if not download_file:
            return jsonify({'status': 'error', 'message': 'No downloadable media found'}), 500

        # Increment the counter for the selected brand and rename file
        brand_counters[brand] += 1
        current_serial = brand_counters[brand]
        ext = os.path.splitext(download_file)[1]
        new_filename = f"{current_serial}_{brand}{ext}"
        old_path = os.path.join(folder_path, download_file)
        new_path = os.path.join(folder_path, new_filename)
        os.rename(old_path, new_path)

        file_url = f"/download_file/{shortcode}/{new_filename}"
        is_video = post.is_video if hasattr(post, 'is_video') else False

        return jsonify({
            'status': 'success',
            'message': 'Download complete!',
            'download_url': file_url,
            'is_video': is_video,
            'new_filename': new_filename,
            'serial': current_serial,
            'brand': brand
        })
    except Exception as e:
        # Note: The error below may include network-related issues (NameResolutionError)
        # which indicate that your machine failed to connect to Instagram. Check your DNS or network settings.
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/download_file/<folder>/<filename>')
def download_file(folder, filename):
    directory = os.path.join('downloads', folder)
    return send_from_directory(directory, filename, as_attachment=True)


