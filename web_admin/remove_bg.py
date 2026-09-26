from PIL import Image

def is_background(r, g, b):
    # Checkered pattern is usually white or gray. 
    # Let's say if it's strictly grayscale and light (R=G=B > 150)
    # But wait, the colors in the logo are Magenta, Orange, Cyan, Black.
    # Magenta: ~ (200, 40, 100)
    # Orange: ~ (240, 140, 30)
    # Cyan: ~ (0, 180, 230)
    # Black: ~ (0, 0, 0)
    # So if R, G, B are all > 180 and absolute diffs are small, it's gray/white.
    if r > 150 and g > 150 and b > 150:
        if abs(r - g) < 20 and abs(g - b) < 20 and abs(r - b) < 20:
            return True
    return False

img = Image.open('/Users/andreatlas/.gemini/antigravity/brain/ae607236-2a49-487b-9962-29f90f0d4f78/.user_uploaded/media_1790394674712.jpg').convert("RGBA")
data = img.getdata()

new_data = []
for item in data:
    if is_background(item[0], item[1], item[2]):
        new_data.append((255, 255, 255, 0))
    else:
        new_data.append(item)

img.putdata(new_data)
img.save('public/logo-lablivre.png', 'PNG')
print("Saved to public/logo-lablivre.png")
