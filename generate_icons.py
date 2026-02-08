from PIL import Image, ImageDraw, ImageFont
import os

# Створюємо папку для іконок
os.makedirs('static/images', exist_ok=True)

# Розміри іконок
sizes = [72, 96, 128, 144, 152, 192, 384, 512]

# Кольори
bg_color = (102, 126, 234)  # #667eea
text_color = (255, 255, 255)

for size in sizes:
    # Створюємо зображення
    img = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(img)

    # Малюємо літаки ✈
    try:
        # Спроба використати системний шрифт
        font_size = int(size * 0.6)
        font = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", font_size)
    except:
        try:
            # Для інших систем
            font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", font_size)
        except:
            # Використовуємо дефолтний
            font = ImageFont.load_default()

    # Текст по центру
    text = "✈"

    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((size - text_width) // 2, (size - text_height) // 2 - size // 10)
    except:
        # Fallback для старіших версій PIL
        text_width, text_height = draw.textsize(text, font=font)
        position = ((size - text_width) // 2, (size - text_height) // 2)

    draw.text(position, text, fill=text_color, font=font)

    # Зберігаємо
    img.save(f'static/images/icon-{size}x{size}.png')
    print(f'✅ Створено icon-{size}x{size}.png')

print('\n🎉 Всі іконки створено!')