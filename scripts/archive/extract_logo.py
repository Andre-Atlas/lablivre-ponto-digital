from PIL import Image
import cv2
import numpy as np

img = cv2.imread('/Users/andreatlas/.gemini/antigravity/brain/ae607236-2a49-487b-9962-29f90f0d4f78/.user_uploaded/media_1790392600558.jpg')

# Find the magenta part
# Convert to HSV
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
# Magenta is around hue 150-170
lower_mag = np.array([140, 100, 100])
upper_mag = np.array([170, 255, 255])
mask_mag = cv2.inRange(hsv, lower_mag, upper_mag)

# Find orange
lower_or = np.array([10, 100, 100])
upper_or = np.array([25, 255, 255])
mask_or = cv2.inRange(hsv, lower_or, upper_or)

# Find cyan
lower_cy = np.array([80, 100, 100])
upper_cy = np.array([100, 255, 255])
mask_cy = cv2.inRange(hsv, lower_cy, upper_cy)

def get_poly(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        c = max(contours, key=cv2.contourArea)
        epsilon = 0.02 * cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, epsilon, True)
        return approx
    return None

mag_poly = get_poly(mask_mag)
or_poly = get_poly(mask_or)
cy_poly = get_poly(mask_cy)

print("Magenta:", mag_poly.tolist() if mag_poly is not None else None)
print("Orange:", or_poly.tolist() if or_poly is not None else None)
print("Cyan:", cy_poly.tolist() if cy_poly is not None else None)
