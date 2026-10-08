import cv2
import numpy as np

# Load the image
img = cv2.imread('/Users/andreatlas/.gemini/antigravity/brain/ae607236-2a49-487b-9962-29f90f0d4f78/.user_uploaded/media_1790875925152.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)

# Find contours
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

svg_paths = []
for cnt in contours:
    # Approximate contour
    epsilon = 0.001 * cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, epsilon, True)
    
    if len(approx) > 10:
        path = "M " + " L ".join([f"{p[0][0]},{p[0][1]}" for p in approx]) + " Z"
        svg_paths.append(path)

print(f"Found {len(svg_paths)} paths")
with open("logo.svg", "w") as f:
    f.write(f'<svg viewBox="0 0 {img.shape[1]} {img.shape[0]}" xmlns="http://www.w3.org/2000/svg">\n')
    for p in svg_paths:
        f.write(f'  <path d="{p}" fill="currentColor" />\n')
    f.write('</svg>')
