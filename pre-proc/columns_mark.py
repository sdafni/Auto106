import cv2
import numpy as np
from pdf2image import convert_from_path

# Convert PDF to image(s)
pages = convert_from_path("../forms/dagshub_ocr_old/non_pass_031168701_T106.pdf", dpi=500)
image = np.array(pages[0])
clone = image.copy()


# List to store column coordinates
columns = []

def mark_columns(event, x, y, flags, param):
    print(f"Mouse at: ({x}, {y})")
    if event == cv2.EVENT_LBUTTONDOWN:
        columns.append((x, y))
    elif event == cv2.EVENT_LBUTTONUP:
        columns.append((x, y))
        cv2.rectangle(clone, columns[-2], columns[-1], (0, 255, 0), 2)
        cv2.imshow("Mark Columns", clone)

cv2.namedWindow("Mark Columns")
cv2.setMouseCallback("Mark Columns", mark_columns)

while True:
    cv2.imshow("Mark Columns", clone)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):  # Press 'q' to quit
        break

cv2.destroyAllWindows()

# Now use these coordinates to crop columns
print(columns)
# [(2374, 757), (1512, 2741), (1352, 759), (143, 2750)]
# cv2image[y1:y2, x1:x2]
# column1 = image[columns[0][1]:columns[1][1], columns[0][0]:columns[1][0]]
# column2 = image[columns[2][1]:columns[3][1], columns[2][0]:columns[3][0]]
