import os

import cv2
import numpy as np
import pytesseract
from PIL import Image


def process(images, text):
    idx = 0
    for pil_image in images:
        idx += 1
        cv2image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

        height = 5766
        width = 4053

        # Define column coordinates as ratios (x/width, y/height)
        col1_x1_ratio, col1_y1_ratio = 168 / width, 1256 / height
        col1_x2_ratio, col1_y2_ratio = 2228 / width, 4589 / height

        col2_x1_ratio, col2_y1_ratio = 2511 / width, 1256 / height
        col2_x2_ratio, col2_y2_ratio = 3941 / width, 4589 / height

        # To get pixel coordinates for any image, multiply ratios by actual width/height
        x1, y1, x2, y2 = int(col1_x1_ratio * cv2image.shape[1]), int(col1_y1_ratio * cv2image.shape[0]), int(
            col1_x2_ratio * cv2image.shape[1]), int(col1_y2_ratio * cv2image.shape[0])
        cropped_column1 = cv2image[y1:y2, x1:x2]

        x1, y1, x2, y2 = int(col2_x1_ratio * cv2image.shape[1]), int(col2_y1_ratio * cv2image.shape[0]), int(
            col2_x2_ratio * cv2image.shape[1]), int(col2_y2_ratio * cv2image.shape[0])
        cropped_column2 = cv2image[y1:y2, x1:x2]

        # x1, y1, x2, y2 = 168, 1256,     2228, 4589
        # cropped_column1 = cv2image[y1:y2, x1:x2]
        text1 = pytesseract.image_to_string(Image.fromarray(cropped_column1), lang='eng+heb', config='--psm 6')
        text += text1

        # x1, y1, x2, y2 = 2511, 1256,     3941, 4589
        # cropped_column2 = cv2image[y1:y2, x1:x2]
        text2 = pytesseract.image_to_string(Image.fromarray(cropped_column2), lang='eng+heb', config='--psm 6')
        text += text2

        # Ensure the output directory exists
        save_dir = "output_images"

        # Save each image to a file
        # for idx, image in enumerate(images):
        image_path = os.path.join(save_dir, f"cropped_page_1.png")
        Image.fromarray(cropped_column1).save(image_path, "PNG")

        image_path = os.path.join(save_dir, f"cropped_page_2.png")
        Image.fromarray(cropped_column2).save(image_path, "PNG")

        # Save OCR text to corresponding text files
        text1_path = os.path.join(save_dir, f"cropped_page_text_1.txt")
        with open(text1_path, "w", encoding="utf-8") as f:
            f.write(text1)

        text2_path = os.path.join(save_dir, f"cropped_page_text_2.txt")
        with open(text2_path, "w", encoding="utf-8") as f:
            f.write(text2)
    return text
