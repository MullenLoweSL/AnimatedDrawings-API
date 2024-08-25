import base64
import datetime
from flask import Flask, request, jsonify, send_from_directory
import os
from examples.image_to_animation import image_to_animation
from moviepy.editor import VideoFileClip, AudioFileClip

app = Flask(__name__)

# Configure the upload folder and allowed extensions
UPLOAD_FOLDER = "uploads"
BG_IMAGES_FOLDER = "uploads/bg_images"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
AUDIO_FOLDER = "uploads/audio_files"
# Ensure the upload folder exists
os.makedirs(BG_IMAGES_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

audio_mapper = {
    0: "advertising.mp3",
    1: "funk.mp3"
}

background_mapper = {
    0: "forest-1.jpg",
    1: "forest-2.png"
}

# Function to check if a file is allowed
def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/image_to_animation", methods=["POST"])
def upload_file():
    try:
        url = ""
        data = request.json
        image_base64 = data.get("img_base64")
        audio_id = data.get("audio_id")
        bg_image_id = data.get("bg_image_id")
        four_leg_skeleton_flag = data.get("four_leg_skeleton")
        bg_img_file_path = ""

        # Decode the base64 string to an image file
        image_data = base64.b64decode(image_base64)
        now = datetime.datetime.now()
        current_timestamp = str(int(datetime.datetime.timestamp(now)))
        folder_name = f"image_{current_timestamp}"
        img_file_path = os.path.join("", f"{folder_name}.png")
        audio_clip = None

        with open(img_file_path, "wb") as f:
            f.write(image_data)

        if bg_image_id:
            bg_img_file = background_mapper.get(int(bg_image_id))
            bg_img_file_path = os.path.join(BG_IMAGES_FOLDER, bg_img_file)

        if not four_leg_skeleton_flag:
            image_to_animation(
                img_fn=img_file_path,
                char_anno_dir=f"uploads/{folder_name}/",
                motion_cfg_fn="examples/config/motion/dab.yaml",
                retarget_cfg_fn="examples/config/retarget/fair1_ppf.yaml",
                bg_image=(bg_img_file_path if bg_image_id else None),
            )


        else:
            image_to_animation(
                img_fn=img_file_path,
                char_anno_dir=f"uploads/{folder_name}/",
                motion_cfg_fn="examples/config/motion/zombie.yaml",
                retarget_cfg_fn="examples/config/retarget/four_legs.yaml",
                bg_image=(bg_img_file_path if bg_image_id else None),
            )

            url = request.url_root + f"uploads/{folder_name}/" + "video.mp4"
        # Audio adding part start
        if audio_id:
            audio_file = audio_mapper.get(int(audio_id))
            audio_path = os.path.join(AUDIO_FOLDER, audio_file)
            # Load video and audio files
            audio_clip = AudioFileClip(audio_path)


        video_path = f"uploads/{folder_name}/" + "video.mp4"
        output_path = f"uploads/{folder_name}/" + "video_web.mp4"
        video_clip = VideoFileClip(video_path)
        new_video_clip = video_clip.set_audio(audio_clip)
        new_video_clip.write_videofile(output_path)
        url = request.url_root + output_path
        os.remove(img_file_path)
        return jsonify({"message": "hello world", "url": url})

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/uploads/<foldername>/<filename>", methods=["GET"])
def render_file(foldername, filename):
    return send_from_directory(
        UPLOAD_FOLDER, f"{foldername}/{filename}", as_attachment=True
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
