#!/usr/bin/env python3

from openai import OpenAI
import base64
import itertools
import argparse
import os

system_content = """
Your task is to transcribe Polish exercises from images and create interactive blanks for the users to fill in.
Don't fill interactive blanks by yourself let the students do it.
At the end include a dictionary section where each interesting or complicated Polish word with pronunciation in Russian and Russian translation.
Aimed specifically for Ukrainian students learning Polish.
For dictionary use template:
Słownik
1. polish_word - [pronunciation] - russian_translation
2. another_polish_word - [pronunciation] - russian_translation
Example: grać - [граць] - играть
For exercises use template:
Student: (Ja) __________ na imię Piotr, a ty jak __________ na imię?
Output in Markdown format.
"""


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def main():
    client = OpenAI()

    parser = argparse.ArgumentParser(description="Process image path.")
    parser.add_argument("image_path", type=str, help="Path to the image")

    args = parser.parse_args()
    base64_image = encode_image(args.image_path)

    completion = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": system_content
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Write exercises on the image to the output."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high"
                        }
                    }],
            }
        ],
        temperature=0.3,
        max_tokens=4096,
        stream=True,
    )

    spinner = itertools.cycle(['-', '/', '|', '\\'])

    buffer = []
    chunk_number = 1
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            buffer.append(chunk.choices[0].delta.content)
            print(f"Processing chunk #{chunk_number}", f"id:{chunk.id}", f"{next(spinner)}", end="\r")
            chunk_number += 1

    print()

    image_dir = os.path.dirname(args.image_path)
    md_file_name, _ = os.path.splitext(os.path.basename(args.image_path))
    md_file_path = os.path.join(image_dir, f"{md_file_name}.md")

    response = ''.join(buffer)
    with open(md_file_path, "w") as f:
        f.write(response)

    print(response)


if __name__ == "__main__":
    main()
