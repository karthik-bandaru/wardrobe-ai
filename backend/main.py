import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.concurrency import run_in_threadpool

from pydantic import BaseModel

from ai.recommendations.colour_matching import (
    get_outfit_recommendations,
    COLOUR_FAMILIES,
)

import re

import cv2
import numpy as np

from ai.detection.colour_detection import analyze_clothing

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "Wardrobe AI Backend is running"
    }


@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    # Accept only image uploads
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Please upload an image file."
        )

    # Read the uploaded image bytes
    contents = await file.read()

    # Convert bytes into an OpenCV image
    image_array = np.frombuffer(contents, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if image is None:
        raise HTTPException(
            status_code=400,
            detail="The uploaded image could not be read."
        )

    try:
        # Run AI analysis without blocking the async event loop
        result = await run_in_threadpool(analyze_clothing, image)
        return result

    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))





class RecommendationRequest(BaseModel):
    clothing_type: str
    colour: str


@app.post("/recommend")
def recommend_outfit(request: RecommendationRequest):
    result = get_outfit_recommendations(
        request.clothing_type,
        request.colour
    )

    return result



import re


class ChatRequest(BaseModel):
    message: str


def find_colour_in_message(message):
    """Find a recognized colour or shade in a chat message."""

    colour_names = [
        shade
        for shades in COLOUR_FAMILIES.values()
        for shade in shades
    ]

    # Check longer names first, such as Sky Blue.
    colour_names.sort(key=len, reverse=True)

    for colour in colour_names:
        pattern = rf"(?<!\w){re.escape(colour)}(?!\w)"

        if re.search(pattern, message, re.IGNORECASE):
            return colour

    return None


def find_clothing_type(message):
    """Identify a clothing type mentioned in the message."""

    text = message.lower().replace("_", " ")

    clothing_types = [
        ("t-shirt", ["t-shirt", "t shirt", "tshirt"]),
        ("trousers", ["trousers", "pants"]),
        ("jeans", ["jeans", "denim"]),
        ("kurta", ["kurta"]),
        ("dress", ["dress", "gown"]),
        ("shirt", ["shirt"]),
    ]

    for clothing_type, keywords in clothing_types:
        for keyword in keywords:
            pattern = rf"(?<!\w){re.escape(keyword)}(?!\w)"

            if re.search(pattern, text):
                return clothing_type

    return None


def get_python_matching_context(message):
    colour = find_colour_in_message(message)
    clothing_type = find_clothing_type(message)

    if not colour or not clothing_type:
        return ""

    result = get_outfit_recommendations(
        clothing_type,
        colour
    )

    if result.get("message"):
        return ""

    recommendations = result.get("recommendations", [])

    if not recommendations:
        return ""

    lines = [
        f"Recognized clothing item: {colour} {clothing_type}",
        "Existing Python colour-matching results:"
    ]

    for item in recommendations[:5]:
        lines.append(
            f"- {item['colour']}: "
            f"Score {item['score']}/100. "
            f"Reason: {item['reason']}"
        )

    suggested_items = result.get("recommended_items", [])

    if suggested_items:
        lines.append(
            "Suggested clothing items: "
            + ", ".join(suggested_items)
        )

    return "\n".join(lines)


@app.post("/chat")
def chat_with_assistant(request: ChatRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Please enter a message."
        )

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Gemini API key is not configured."
        )

    try:
        client = genai.Client(api_key=api_key)

        matching_context = get_python_matching_context(message)

        prompt = message

        if matching_context:
            prompt = (
                f"User's fashion question:\n{message}\n\n"
                f"Verified results from the project's Python "
                f"colour-matching engine:\n{matching_context}\n\n"
                "Use these Python scores and reasons accurately. "
                "You may suggest additional outfit ideas, but clearly "
                "distinguish extra styling suggestions from the "
                "Python engine's scored recommendations. "
                "If no Python results are supplied, answer using "
                "your general fashion knowledge."
            )

        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are Wardrobe AI, a friendly and practical "
                    "fashion assistant. Help users choose clothing, "
                    "match colours, coordinate outfits, and dress "
                    "appropriately for occasions such as interviews, "
                    "weddings, college, parties, and casual outings. "
                    "Give clear, specific suggestions with examples. "
                    "Consider the user's stated clothing, colours, "
                    "occasion, weather, and preferences when provided. "
                    "If important information is missing, ask a short "
                    "follow-up question. Be respectful of different "
                    "budgets, cultures, and personal styles. "
                    "Do not claim to see an uploaded image unless "
                    "image information is actually provided. "
                    "Stay focused on fashion and styling."
                ),
                temperature=0.7,
                max_output_tokens=1000,
            ),
        )

        reply = response.text

        if not reply:
            raise HTTPException(
                status_code=502,
                detail="Gemini returned an empty response. Please try again."
            )

        return {"reply": reply}

    except HTTPException:
        raise

    except Exception as exc:
        print(f"Gemini API error: {exc}")
        raise HTTPException(
            status_code=502,
            detail=(
                "Sorry, the fashion assistant is temporarily unavailable. "
                "Check the backend terminal for details."
            )
        )
