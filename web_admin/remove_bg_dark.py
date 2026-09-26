from PIL import Image

def is_dark_background(r, g, b):
    # The checkered pattern in the dark image is made of dark grays.
    # The logo colors are bright (White, Magenta, Orange, Cyan).
    # Magenta is ~ (200, 40, 100) -> R is high.
    # Cyan is ~ (0, 180, 230) -> G and B are high.
    # Orange is ~ (240, 140, 30) -> R and G are high.
    # White is ~ (255, 255, 255) -> all high.
    # So the background is basically anything where R, G, B are all < 100
    # Let's be safe: if all R, G, B are < 120 and they are somewhat neutral (difference < 30)
    if r < 120 and g < 120 and b < 120:
        if abs(r - g) < 30 and abs(g - b) < 30 and abs(r - b) < 30:
            return True
    return False

img = Image.open('/Users/andreatlas/.gemini/antigravity/brain/ae607236-2a49-487b-9962-29f90f0d4f78/.user_uploaded/media_1790395326592.jpg').convert("RGBA")
data = img.getdata()

new_data = []
for item in data:
    if is_dark_background(item[0], item[1], item[2]):
        new_data.append((255, 255, 255, 0))
    else:
        new_data.append(item)

img.putdata(new_data)
img.save('public/logo-lablivre-dark.png', 'PNG')
print("Saved to public/logo-lablivre-dark.png")
