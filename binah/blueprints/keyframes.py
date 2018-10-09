import cv2
import PIL
from pathlib import Path
from binah.util import get_data_home, log
from binah.model import Video, Image, Type, Lifecycle, Example
import piexif
import ujson as json

THRESHOLD = 0.1

VIDEO_DIR = get_data_home() / 'videos'
IMAGES_DIR = get_data_home() / 'images'

def _preprocess_frame(frame):
    """
    Preprocess frame to be more invariant to noise and other irrelevant differences.
    """
    frame = cv2.resize(frame, None, fx=0.2, fy=0.2, interpolation=cv2.INTER_AREA)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.GaussianBlur(frame, (9,9), 0.0)
    return frame

def _emit_keyframes(path):
    last_frame = []
    frame_idx = 0
    video = cv2.VideoCapture(path)
    while (video.isOpened()):
        _, frame = video.read()
        frame = _preprocess_frame(frame)
        if len(last_frame) == 0:
            last_frame = frame
        diff = cv2.absdiff(frame, last_frame)
        diff = cv2.countNonZero(diff)
        if diff > THRESHOLD:
            yield frame, frame_idx
        last_frame = frame
        frame_idx += 1

def Keyframes(session):
    videos = session.query(Example).filter(Example.type == Type.MP4)
    for video in videos:
        videopath = str(VIDEO_DIR / str(video.id))
        for frame, idx in _emit_keyframes(videopath + '.mp4'):
            example = Example(dataset_id=video.dataset_id,
                        type=Type.JPEG,
                        lifecycle=Lifecycle.FLEXIBLE,
                        license_id=video.license_id
                        )
            session.add(example)
            session.flush()
            frame = PIL.Image.fromarray(frame)
            
            exif = piexif.load(frame.info["exif"])
            metadata = json.dumps({'video_id': video.id, 'frame': idx})
            exif["0th"][piexif.ImageIFD.ImageDescription] = metadata
  
            img = Image(id=example.id, url=str(f"file:///data/video/{video.id}?frame={idx}"))
            session.add(img)
            imgpath = IMAGES_DIR / str(example.id)
            frame.save(imgpath, exif=piexif.dump(exif))
    session.commit()

