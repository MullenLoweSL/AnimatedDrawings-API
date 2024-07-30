import datetime

from flask import Flask, request, jsonify, send_from_directory
import os
from examples.image_to_animation import image_to_animation

app = Flask(__name__)

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
    img_file_path = os.path.join('', image_file.filename)

    if background_image_file:
        bg_img_file_path = os.path.join('uploads/bg_images/', background_image_file.filename)
        background_image_file.save(bg_img_file_path)

    image_file.save(img_file_path)

    try:
        if not four_leg_skeleton_flag:
            image_to_animation(img_fn=img_file_path, char_anno_dir=f"uploads/{folder_name}/",
                               motion_cfg_fn='examples/config/motion/dab.yaml',
                               retarget_cfg_fn='examples/config/retarget/fair1_ppf.yaml', bg_image=background_image_file.filename if background_image_file else None)
        else:
            image_to_animation(img_fn=img_file_path, char_anno_dir=f"uploads/{folder_name}/",
                               motion_cfg_fn='examples/config/motion/zombie.yaml',
                               retarget_cfg_fn='examples/config/retarget/four_legs.yaml',
                               bg_image=background_image_file.filename if background_image_file else None)
    except Exception as e:
        print(e)

    finally:
        os.remove(img_file_path)
        if bg_img_file_path:
            os.remove(bg_img_file_path)

    return jsonify({"message": "hello world", "url": request.url_root + f'uploads/{folder_name}/' + "video.mp4"})


@app.route('/uploads/<foldername>/<filename>', methods=['GET'])
def render_file(foldername, filename):
    return send_from_directory(UPLOAD_FOLDER, f"{foldername}/{filename}", as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
