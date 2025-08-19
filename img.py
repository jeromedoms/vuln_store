from PIL import Image, ImageDraw, ImageFont

# Create red square image (800x800)
img = Image.new('RGB', (800, 800), color='red')
draw = ImageDraw.Draw(img)

# Use default font (no external file needed)
try:
    font = ImageFont.truetype("arialbd.ttf", 60)  # Try Arial Bold if available
except:
    font = ImageFont.load_default(size=60)  # Fallback to default font

# Get text bounding box (new method for Pillow 10+)
text = "COMMAND EXECUTED"
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

# Center the text
x = (800 - text_width) / 2
y = (800 - text_height) / 2

# Draw white text
draw.text((x, y), text, fill="white", font=font)

# Save image
img.save("hacked.jpg")
print("Image saved as command_executed.png")
