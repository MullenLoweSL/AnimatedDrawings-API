import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from examples.image_to_animation import image_to_animation

app = Flask(__name__)

# Allow CORS globally for all routes
CORS(app, origins=[
    "https://portal.azure.com",
    "http://localhost:3000",
    "http://localhost:5173",
    "https://atlas-paint-mixer-mobile-webapp.vercel.app"
])

media_base_url = "https://mullenlowedemo.blob.core.windows.net/paint-mixer-public/"
audio_mapper = {
    0: {
        "url": media_base_url + "beat.mp3",
        "image": "https://mullenlowedemo.blob.core.windows.net/public/3-sri-lanka.png",
        "title": "Beaty music",
        "subtitle": "Beaty music subtitle",
    },
    1: {
        "url": media_base_url + "loop.mp3",
        "image": "https://mullenlowedemo.blob.core.windows.net/public/3-sri-lanka.png",
        "title": "Loop music",
        "subtitle": "Loop music subtitle",
    },
    2: {
        "url": media_base_url + "synth.mp3",
        "image": "https://mullenlowedemo.blob.core.windows.net/public/3-sri-lanka.png",
        "title": "Synth music",
        "subtitle": "Synth music subtitle",
    }
}

background_mapper = {
    0: {
        "url": media_base_url + "jungle.png",
        "description": "Jungle background"
    },
    1: {
        "url": media_base_url + "lake.png",
        "description": "Lake background"
    },
    2: {
        "url": media_base_url + "desert.png",
        "description": "Desert background"
    }
}

# Add Content Security Policy (CSP) headers to all responses
@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "img-src 'self' data:; "
        "media-src 'self'; "  # Assuming videos are served from the same domain
        "script-src 'self'; "
        "style-src 'self' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "frame-ancestors 'self';"
    )
    return response

# Configure the upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
BG_IMAGES_FOLDER = 'uploads/bg_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload folder exists
os.makedirs(BG_IMAGES_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Function to check if a file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/get_backgrounds', methods=['GET'])
def return_backgrounds():
    backgrounds = {key: background_mapper[key] for key in background_mapper}
    return jsonify(backgrounds)

@app.route('/get_audios', methods=['GET'])
def return_audios():
    audios = {key: audio_mapper[key] for key in audio_mapper}
    return jsonify(audios)

@app.route('/image_to_animation', methods=['POST'])
def upload_file():
    image_file = request.files.get('img')
    background_image_file = request.files.get('bg_img')
    four_leg_skeleton_flag = request.args.get('four_leg_skeleton')

    bg_img_file_path = ""
    # Construct the file path to save the image

    # current date and time
    now = datetime.datetime.now()
    current_timestamp = datetime.datetime.timestamp(now)
    folder_name = f"{image_file.filename.split('.')[0]}_{current_timestamp}"
    file_name, file_ext = image_file.filename.split(".")
    img_file_path = os.path.join('', f"{file_name}_{current_timestamp}.{file_ext}")

    if background_image_file:
        bg_file_name, bg_file_ext = background_image_file.filename.split(".")
        bg_img_file_path = os.path.join('uploads/bg_images/', f"{bg_file_name}_{current_timestamp}.{bg_file_ext}")
        bg_img_name = f"{bg_file_name}_{current_timestamp}.{bg_file_ext}"
        background_image_file.save(bg_img_file_path)

    image_file.save(img_file_path)

    try:
        if not four_leg_skeleton_flag:
            image_to_animation(img_fn=img_file_path, char_anno_dir=f"uploads/{folder_name}/",
                               motion_cfg_fn='examples/config/motion/dab.yaml',
                               retarget_cfg_fn='examples/config/retarget/fair1_ppf.yaml', bg_image=bg_img_name if background_image_file else None)
        else:
            image_to_animation(img_fn=img_file_path, char_anno_dir=f"uploads/{folder_name}/",
                               motion_cfg_fn='examples/config/motion/zombie.yaml',
                               retarget_cfg_fn='examples/config/retarget/four_legs.yaml',
                               bg_image=bg_img_name if background_image_file else None)
    except Exception as e:
        print(e)

    finally:
        os.remove(img_file_path)
        if bg_img_file_path:
            os.remove(bg_img_file_path)

    # add cache busting parameter
    return jsonify({
        "message": "hello world", 
        "url": request.url_root + f'uploads/{folder_name}/video.mp4?t={int(datetime.datetime.now().timestamp())}'
    })


@app.route('/uploads/<foldername>/<filename>', methods=['GET'])
def render_file(foldername, filename):
    return send_from_directory(UPLOAD_FOLDER, f"{foldername}/{filename}", as_attachment=True)

# Your route to serve video files
@app.route('/uploads/<path:subfolder>/<filename>')
def serve_video(subfolder, filename):
    return send_from_directory(f'uploads/{subfolder}', filename, mimetype='video/mp4')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)