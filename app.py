import base64
import datetime
from flask import Flask, request, jsonify, send_from_directory
import os
from examples.image_to_animation import image_to_animation
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip

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
    1: "classical.mp3",
    2: "emotional.mp3",
    3: "funk.mp3",
    4: "sport.mp3"
}

background_mapper = {
    0: "beach.png",
    1: "castle.png",
    2: "desert.png",
    3: "forest.png",
    4: "house.png",
    5: "snow.png",
    6: "space.png"
}

motion_mapper = {
    0: "examples/config/motion/dab.yaml",
    1: "examples/config/motion/jesse_dance.yaml",
    2: "examples/config/motion/jumping_jacks.yaml",
    3: "examples/config/motion/jumping.yaml",
    4: "examples/config/motion/wave_hello.yaml",
    5: "examples/config/motion/zombie.yaml"
}

# Function to check if a file is allowed
def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def overlay_images_on_video(video_path, img1_path, img2_path, output_path):
    # Load the video
    video_clip = VideoFileClip(video_path)
    video_width = video_clip.w
    video_height = video_clip.h

    # Load and scale the first image
    img1_clip = ImageClip(img1_path).resize(width=video_width)
    img1_clip = img1_clip.set_position(("center", "bottom")).set_duration(video_clip.duration)

    # Load and scale the second image
    img2_clip = ImageClip(img2_path).resize(width=video_width)
    img2_clip = img2_clip.set_position(("center", "top")).set_duration(video_clip.duration)

    # Overlay the images on the video using CompositeVideoClip
    final_clip = CompositeVideoClip([video_clip, img1_clip, img2_clip])

    # Write the result to a file
    final_clip.write_videofile(output_path, codec="libx264")

    return output_path

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

        motion_id = data.get("motion_id")
        motion_cfg_fn = motion_mapper.get(int(motion_id))

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
                motion_cfg_fn=motion_cfg_fn,
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

        # Edits for BMICH launch event
        # Overlay images on the video
        img1_path = "watermark/bottom.png"  # Replace with actual path
        img2_path = "watermark/top.png"  # Replace with actual path
        final_output_path = f"uploads/{folder_name}/" + "final_video.mp4"
        overlay_images_on_video(output_path, img1_path, img2_path, final_output_path)

        url = request.url_root + final_output_path
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
