from deepface import DeepFace


def detect_emotion(face_image):
    """
    Detect the dominant emotion from a cropped face image.

    Args:
        face_image: OpenCV image (NumPy array)

    Returns:
        str: Detected emotion or "Unknown"
    """

    if face_image is None:
        return "Unknown"

    try:
        result = DeepFace.analyze(
            img_path=face_image,
            actions=["emotion"],
            detector_backend="skip",
            enforce_detection=False,
            silent=True
        )

        # DeepFace may return a list or a dictionary
        if isinstance(result, list):
            if not result:
                return "Unknown"
            result = result[0]

        emotion = result.get("dominant_emotion", "Unknown")

        return emotion

    except Exception as e:
        print(f"Emotion detection error: {e}")
        return "Unknown"