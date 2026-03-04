<<<<<<< HEAD
from deepface import DeepFace
import numpy as np
import cv2
from PIL import Image
import config


def load_image_file(file_stream):
    """
    Load main image from stream. DeepFace accepts paths or numpy arrays (BGR).
    """
    image = Image.open(file_stream)
    image = np.array(image)
    # Convert RGB to BGR for OpenCV/DeepFace if needed, but DeepFace internals handle it.
    # DeepFace usually expects RGB if using PIL, or BGR if using cv2.imread.
    # Let's keep it as numpy array.
    return image


def get_face_encodings(image):
    """
    Return a list of face encodings found in the image.
    DeepFace represents multiple faces if detector_backend finds them.
    However, DeepFace.represent returns a list of result objects.
    """
    try:
        # enforce_detection=True throws error if no face.
        # We handle exception.
        embedding_objs = DeepFace.represent(
            img_path=image,
            model_name=config.MODEL_NAME,
            enforce_detection=True,
            detector_backend="opencv",  # fast, no external dlib dep needed hopefully
        )
        # embedding_objs is a list of dicts: {'embedding': [...], 'facial_area': ...}
        encodings = [np.array(obj["embedding"]) for obj in embedding_objs]
        return encodings
    except Exception as e:
        # No face found or other error
        print(f"DeepFace detect error: {e}")
        return []


def match_face(unknown_encoding, known_encodings, tolerance=0.5):
    """
    Compare embedding against knowns.
    DeepFace uses Cosine Similarity or Euclidean L2.
    """
    if not known_encodings:
        return None

    # Find the closest match using Euclidean or Cosine distance
    # DeepFace verification default threshold for Facenet512 is around 0.3 (cosine) or 23.56 (euclidean_l2)
    # We will implement a simple distance check here since we have embeddings.

    # Let's use Cosine Similarity: A . B / ||A|| ||B||
    # 1 - Cosine Sim = Cosine Distance. Lower is better.

    best_score = float("inf")
    best_index = -1

    unknown_norm = np.linalg.norm(unknown_encoding)

    for i, known in enumerate(known_encodings):
        known_norm = np.linalg.norm(known)
        # Cosine distance
        sim = np.dot(unknown_encoding, known) / (unknown_norm * known_norm)
        dist = 1 - sim

        if dist < best_score:
            best_score = dist
            best_index = i

    # Threshold for Facenet512 cosine distance is usually around 0.4
    if best_score < 0.4:
        return best_index

    return None
=======
from deepface import DeepFace
import numpy as np
import cv2
from PIL import Image
import config


def load_image_file(file_stream):
    """
    Load main image from stream. DeepFace accepts paths or numpy arrays (BGR).
    """
    image = Image.open(file_stream)
    image = np.array(image)
    # Convert RGB to BGR for OpenCV/DeepFace if needed, but DeepFace internals handle it.
    # DeepFace usually expects RGB if using PIL, or BGR if using cv2.imread.
    # Let's keep it as numpy array.
    return image


def get_face_encodings(image):
    """
    Return a list of face encodings found in the image.
    DeepFace represents multiple faces if detector_backend finds them.
    However, DeepFace.represent returns a list of result objects.
    """
    try:
        # enforce_detection=True throws error if no face.
        # We handle exception.
        embedding_objs = DeepFace.represent(
            img_path=image,
            model_name=config.MODEL_NAME,
            enforce_detection=True,
            detector_backend="opencv",  # fast, no external dlib dep needed hopefully
        )
        # embedding_objs is a list of dicts: {'embedding': [...], 'facial_area': ...}
        encodings = [np.array(obj["embedding"]) for obj in embedding_objs]
        return encodings
    except Exception as e:
        # No face found or other error
        print(f"DeepFace detect error: {e}")
        return []


def match_face(unknown_encoding, known_encodings, tolerance=0.5):
    """
    Compare embedding against knowns.
    DeepFace uses Cosine Similarity or Euclidean L2.
    """
    if not known_encodings:
        return None

    # Find the closest match using Euclidean or Cosine distance
    # DeepFace verification default threshold for Facenet512 is around 0.3 (cosine) or 23.56 (euclidean_l2)
    # We will implement a simple distance check here since we have embeddings.

    # Let's use Cosine Similarity: A . B / ||A|| ||B||
    # 1 - Cosine Sim = Cosine Distance. Lower is better.

    best_score = float("inf")
    best_index = -1

    unknown_norm = np.linalg.norm(unknown_encoding)

    for i, known in enumerate(known_encodings):
        known_norm = np.linalg.norm(known)
        # Cosine distance
        sim = np.dot(unknown_encoding, known) / (unknown_norm * known_norm)
        dist = 1 - sim

        if dist < best_score:
            best_score = dist
            best_index = i

    # Threshold for Facenet512 cosine distance is usually around 0.4
    if best_score < 0.4:
        return best_index

    return None
>>>>>>> f56354bff23c57e9dbb309990488effecb6c4ad5
