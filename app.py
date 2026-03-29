import os
import re
from flask import Flask, render_template, send_from_directory, abort

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_ROOT = os.path.join(BASE_DIR, "data", "images")
COORD_ROOT = os.path.join(BASE_DIR, "data", "coords")

DATASETS = ["shanghaitech", "UBnormal"]


def list_dirs(path):
    if not os.path.exists(path):
        return []
    return sorted([name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))])


def list_images(path):
    if not os.path.exists(path):
        return []
    return sorted([
        name for name in os.listdir(path)
        if name.lower().endswith((".jpg", ".jpeg", ".png"))
    ])


def frame_to_txt(frame_name):
    # img_00001.jpg -> point0.txt
    base = os.path.splitext(frame_name)[0]
    m = re.search(r"(\d+)$", base)
    if not m:
        return None
    idx = int(m.group(1)) - 1
    return f"point{idx}.txt"


def read_points(txt_path):
    points = []
    if not os.path.exists(txt_path):
        return points

    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # 支持 (747.87, 1010.03)
            line2 = line.replace("(", "").replace(")", "").replace(",", " ")
            parts = line2.split()
            if len(parts) >= 2:
                try:
                    x = float(parts[0])
                    y = float(parts[1])
                    points.append({"x": x, "y": y})
                    continue
                except ValueError:
                    pass
    return points


def prev_next(frames, current):
    if current not in frames:
        return None, None
    i = frames.index(current)
    prev_f = frames[i - 1] if i > 0 else None
    next_f = frames[i + 1] if i < len(frames) - 1 else None
    return prev_f, next_f


@app.route("/")
def index():
    return render_template("index.html", datasets=DATASETS)


@app.route("/dataset/<dataset_name>")
def dataset_detail(dataset_name):
    if dataset_name not in DATASETS:
        abort(404)

    dataset_path = os.path.join(IMAGE_ROOT, dataset_name)
    videos = list_dirs(dataset_path)

    print("========== DATASET DETAIL ==========")
    print("dataset_name =", dataset_name)
    print("dataset_path =", dataset_path)
    print("exists =", os.path.exists(dataset_path))
    print("videos_count =", len(videos))
    print("videos_sample =", videos[:10])
    print("====================================")

    return render_template(
        "dataset.html",
        dataset_name=dataset_name,
        videos=videos
    )


@app.route("/video/<dataset_name>/<video_name>")
def video_detail(dataset_name, video_name):
    if dataset_name not in DATASETS:
        abort(404)

    video_path = os.path.join(IMAGE_ROOT, dataset_name, video_name)
    frames = list_images(video_path)

    print("=========== VIDEO DETAIL ===========")
    print("dataset_name =", dataset_name)
    print("video_name =", video_name)
    print("video_path =", video_path)
    print("exists =", os.path.exists(video_path))
    print("frame_count =", len(frames))
    print("frames_sample =", frames[:10])
    print("====================================")

    return render_template(
        "video.html",
        dataset_name=dataset_name,
        video_name=video_name,
        frames=frames
    )


@app.route("/frame/<dataset_name>/<video_name>/<frame_name>")
def frame_detail(dataset_name, video_name, frame_name):
    if dataset_name not in DATASETS:
        abort(404)

    image_path = os.path.join(IMAGE_ROOT, dataset_name, video_name, frame_name)
    if not os.path.exists(image_path):
        abort(404)

    txt_name = frame_to_txt(frame_name)
    txt_content = "未找到对应的坐标文件"
    points = []

    if txt_name:
        txt_path = os.path.join(COORD_ROOT, dataset_name, video_name, txt_name)
        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                txt_content = f.read()
            points = read_points(txt_path)

    frames = list_images(os.path.join(IMAGE_ROOT, dataset_name, video_name))
    prev_frame, next_frame = prev_next(frames, frame_name)

    return render_template(
        "frame.html",
        dataset_name=dataset_name,
        video_name=video_name,
        frame_name=frame_name,
        image_url=f"/data/images/{dataset_name}/{video_name}/{frame_name}",
        txt_content=txt_content,
        points=points,
        prev_frame=prev_frame,
        next_frame=next_frame
    )


@app.route("/data/images/<dataset_name>/<video_name>/<filename>")
def serve_image(dataset_name, video_name, filename):
    folder = os.path.join(IMAGE_ROOT, dataset_name, video_name)
    if not os.path.exists(folder):
        abort(404)
    return send_from_directory(folder, filename)


# if __name__ == "__main__":
#     print("BASE_DIR =", BASE_DIR)
#     print("IMAGE_ROOT =", IMAGE_ROOT)
#     print("COORD_ROOT =", COORD_ROOT)
#     print("images datasets =", list_dirs(IMAGE_ROOT))
#     print("coords datasets =", list_dirs(COORD_ROOT))
#     app.run(debug=True)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)