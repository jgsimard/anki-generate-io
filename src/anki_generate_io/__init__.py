from PIL import Image
import pytesseract
import requests


def hello() -> str:
    return "Hello from anki-generate-io!"


# Function to perform OCR and generate occlusion data
def generate_occlusions(image_path):
    image = Image.open(image_path)
    text_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

    occlusions = []
    for i in range(len(text_data["text"])):
        if text_data["text"][i].strip():
            (x, y, w, h) = (
                text_data["left"][i],
                text_data["top"][i],
                text_data["width"][i],
                text_data["height"][i],
            )
            occlusions.append(
                {
                    "ordinal": i + 1,
                    "shape": "rect",
                    "left": x / image.width,
                    "top": y / image.height,
                    "width": w / image.width,
                    "height": h / image.height,
                    "occludeInactive": 1,
                }
            )

    return occlusions


# Function to create an Image Occlusion card in Anki
def create_image_occlusion_card(image_path, occlusions, deck_name="Default"):
    # Construct the cloze deletion format
    occlusion_strings = [
        f'{{{{c{occl["ordinal"]}::image-occlusion:{occl["shape"]}:left={occl["left"]:.4f}:top={occl["top"]:.4f}:width={occl["width"]:.4f}:height={occl["height"]:.4f}:oi=1}}}}<br>'
        for occl in occlusions
    ]
    occlusion_text = "".join(occlusion_strings)

    # Prepare the HTML for the image
    image_html = f'<img src="{image_path}">'

    # Prepare the payload for AnkiConnect
    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": deck_name,
                "modelName": "Basic",
                "fields": {"Front": occlusion_text, "Back": image_html},
                "options": {"allowDuplicate": False},
                "tags": [],
            }
        },
    }

    # Send the request to AnkiConnect
    response = requests.post("http://localhost:8765", json=payload)
    return response.json()


# Paths and deck name
image_path = "path_to_image.png"
deck_name = "Default"

# Generate occlusions and create card
occlusions = generate_occlusions(image_path)
response = create_image_occlusion_card(image_path, occlusions, deck_name)
print(response)
