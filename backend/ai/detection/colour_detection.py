
from pathlib import Path

from ultralytics import YOLO
import cv2
import numpy as np


def classify_colour(h, s, v):
    """Convert HSV values into a human-readable colour name."""

    if s < 40:
        if v < 60:
            return "Black"
        elif v > 180:
            return "White"
        else:
            return "Grey"

    if 5 <= h <= 25 and 50 <= s <= 255 and 40 <= v <= 180:
        return "Brown"

    if h < 5 or h >= 170:
        return "Red"

    if 10 <= h < 20:
        return "Orange"

    if 20 <= h < 35:
        return "Yellow"

    if 35 <= h < 85:
        return "Green"

    if 85 <= h < 130:
        return "Blue"

    if 130 <= h < 160:
        return "Purple"

    if 160 <= h < 170:
        return "Pink"

    return "Unknown"


def find_dominant_colours(clothing_pixels, k=3):
    """
    Find the most prominent colours in the detected clothing.

    clothing_pixels contains BGR pixel values from OpenCV.
    Returns a list of colour names, ordered by prominence.
    """

    if clothing_pixels.size == 0:
        return ["Unknown"]

    # Reshape the pixels into a list of BGR colours
    pixels = clothing_pixels.reshape(-1, 3)

    # Sample pixels to keep processing reasonably fast
    if len(pixels) > 10000:
        rng = np.random.default_rng(42)
        indices = rng.choice( len(pixels), size=10000, replace=False)
        pixels = pixels[indices]

    # K-means requires floating-point input
    pixels = np.float32(pixels)

    # Don't request more clusters than available pixels
    number_of_clusters = min(k, len(pixels))

    criteria = (
        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
        100,
        0.2
    )

    _, labels, centers = cv2.kmeans(
        pixels,
        number_of_clusters,
        None,
        criteria,
        10,
        cv2.KMEANS_PP_CENTERS
    )

    # Count how many pixels belong to each cluster
    counts = np.bincount(labels.flatten())

    # Sort clusters from largest to smallest
    sorted_indices = np.argsort(counts)[::-1]

    dominant_colours = []

    for index in sorted_indices:
        # Convert the cluster's representative BGR colour to HSV
        center = np.uint8([[centers[index]]])

        hsv = cv2.cvtColor(
            center,
            cv2.COLOR_BGR2HSV
        )[0][0]

        h, s, v = map(float, hsv)

        # Reuse our existing colour-classification function
        colour_name = classify_colour(h, s, v)

        # Avoid returning the same colour name multiple times
        if colour_name not in dominant_colours:
            dominant_colours.append(colour_name)

    return dominant_colours


# Locate the model file relative to the backend folder
MODEL_PATH = Path(__file__).resolve().parents[2] / "clothing_model.pt"

# Load the model once, not every time an image is analyzed
model = YOLO(str(MODEL_PATH))


def analyze_clothing(image):
    """
    Analyze an image represented as an OpenCV BGR array.
    Return clothing type, confidence and colour.
    """

    if image is None:
        raise ValueError("The image could not be read.")

    # Detect clothing
    results = model.predict(
        source=image,
        conf=0.80,
        verbose=False
    )

    result = results[0]

    # Check that clothing and its segmentation mask were detected
    if result.boxes is None or len(result.boxes) == 0:
        raise ValueError("No clothing detected.")

    if result.masks is None:
        raise ValueError("No clothing segmentation mask detected.")

    # Select the detection with the highest confidence
    confidences = result.boxes.conf.cpu().numpy()
    best_index = int(np.argmax(confidences))

    class_id = int(result.boxes.cls[best_index].item())
    clothing_type = result.names[class_id]
    confidence = float(confidences[best_index])

    # Get the mask belonging to that detection
    mask = result.masks.data[best_index].cpu().numpy()

    mask = cv2.resize(
        mask,
        (image.shape[1], image.shape[0])
    )

    mask = mask > 0.5

    # Extract only the detected clothing pixels
    clothing_pixels = image[mask]

    if clothing_pixels.size == 0:
        raise ValueError("Could not extract clothing pixels.")

    # Convert the clothing pixels from BGR to HSV
    hsv_pixels = cv2.cvtColor(
        clothing_pixels.reshape(-1, 1, 3),
        cv2.COLOR_BGR2HSV
    ).reshape(-1, 3)

    # Calculate the average HSV values
    average_hsv = np.mean(hsv_pixels, axis=0)

    h, s, v = average_hsv

    # Classify the dominant colour

    # Classify the overall average colour
    colour_name = classify_colour(h, s, v)

    # Find the prominent colours separately
    dominant_colours = find_dominant_colours(clothing_pixels, k=3)

    return {
        "clothing_type": clothing_type,
        "confidence": round(confidence, 4),
        "colour": colour_name,
        "dominant_colours": dominant_colours
    }

