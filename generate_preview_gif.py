import math
import os
from PIL import Image, ImageDraw, ImageFont

WIDTH = 640
HEIGHT = 320
NUM_FRAMES = 36
FRAME_DURATION = 55  # ~18 fps -> 2 second smooth loop

# Content area bounding box (50px top and bottom padding)
TOP_PAD = 50
BOT_PAD = 50
CONTENT_Y_START = TOP_PAD
CONTENT_Y_END = HEIGHT - BOT_PAD  # 270
CONTENT_HEIGHT = CONTENT_Y_END - CONTENT_Y_START  # 220

# Load fonts
try:
    font_title = ImageFont.truetype("segoeuib.ttf", 22)
    font_sub = ImageFont.truetype("segoeui.ttf", 11)
    font_badge = ImageFont.truetype("segoeuib.ttf", 9)
    font_pill = ImageFont.truetype("segoeui.ttf", 10)
    font_mono = ImageFont.truetype("consola.ttf", 10)
    font_mono_bold = ImageFont.truetype("consolab.ttf", 10)
    font_card_title = ImageFont.truetype("segoeuib.ttf", 10)
    font_card_sub = ImageFont.truetype("segoeui.ttf", 9)
except Exception:
    font_title = ImageFont.load_default()
    font_sub = ImageFont.load_default()
    font_badge = ImageFont.load_default()
    font_pill = ImageFont.load_default()
    font_mono = ImageFont.load_default()
    font_mono_bold = ImageFont.load_default()
    font_card_title = ImageFont.load_default()
    font_card_sub = ImageFont.load_default()

def lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

def create_base_bg():
    bg = Image.new("RGB", (WIDTH, HEIGHT), (13, 17, 23))
    draw = ImageDraw.Draw(bg)
    
    # Vertical background gradient
    for y in range(HEIGHT):
        t = y / HEIGHT
        col = lerp_color((9, 13, 22), (22, 27, 34), t)
        draw.line([(0, y), (WIDTH, y)], fill=col)
    
    # Subtle cyber grid
    grid_spacing = 20
    for x in range(0, WIDTH, grid_spacing):
        draw.line([(x, 0), (x, HEIGHT)], fill=(30, 36, 45, 128), width=1)
    for y in range(0, HEIGHT, grid_spacing):
        draw.line([(0, y), (WIDTH, y)], fill=(30, 36, 45, 128), width=1)
    
    # Inner border for the content section (50px top and bottom padding)
    # Draw subtle inner frame boundary
    draw.rounded_rectangle(
        [15, TOP_PAD, WIDTH - 15, CONTENT_Y_END],
        radius=10,
        outline=(48, 54, 61),
        width=1
    )
    
    return bg

base_bg = create_base_bg()

frames = []

for f in range(NUM_FRAMES):
    progress = f / NUM_FRAMES
    rad = progress * 2 * math.pi
    
    img = base_bg.copy()
    draw = ImageDraw.Draw(img)
    
    # 1. Animated scanning sweep line
    scan_x = int((progress * (WIDTH + 200)) - 100)
    for offset in range(-30, 31):
        x = scan_x + offset
        if 0 <= x < WIDTH:
            alpha = max(0, 1.0 - abs(offset) / 30.0)
            glow_col = lerp_color((13, 17, 23), (88, 166, 255), alpha * 0.18)
            # Apply scanning light line inside content area
            draw.line([(x, TOP_PAD + 1), (x, CONTENT_Y_END - 1)], fill=glow_col, width=1)
    
    # 2. Glowing Shield Emblem (Left side)
    # Center of shield:
    shield_cx = 75
    shield_cy = 160
    pulse = (math.sin(rad) + 1) / 2  # 0 to 1
    
    # Animated Radar dashes around shield
    radar_angle = progress * 2 * math.pi
    r_radius = 42 + int(pulse * 3)
    num_dashes = 12
    for i in range(num_dashes):
        a = radar_angle + (i * (2 * math.pi / num_dashes))
        x1 = shield_cx + math.cos(a) * (r_radius - 4)
        y1 = shield_cy + math.sin(a) * (r_radius - 4)
        x2 = shield_cx + math.cos(a) * (r_radius + 2)
        y2 = shield_cy + math.sin(a) * (r_radius + 2)
        c_val = int(120 + 100 * math.sin(a + rad))
        draw.line([(x1, y1), (x2, y2)], fill=(31, 111, 235), width=1)
    
    # Shield Outer Glow
    glow_r = int(32 + pulse * 6)
    glow_col = lerp_color((13, 17, 23), (88, 166, 255), 0.35 + pulse * 0.25)
    draw.ellipse([shield_cx - glow_r, shield_cy - glow_r, shield_cx + glow_r, shield_cy + glow_r], fill=glow_col)
    
    # Shield shape
    # Points for shield:
    s_top = shield_cy - 24
    s_bot = shield_cy + 26
    s_left = shield_cx - 22
    s_right = shield_cx + 22
    shield_pts = [
        (shield_cx, s_top - 4),
        (s_right, s_top + 4),
        (s_right, shield_cy + 6),
        (shield_cx, s_bot),
        (s_left, shield_cy + 6),
        (s_left, s_top + 4)
    ]
    draw.polygon(shield_pts, fill=(16, 24, 38), outline=(88, 166, 255))
    
    # Shield interior lock symbol
    lock_x = shield_cx - 7
    lock_y = shield_cy - 2
    draw.rounded_rectangle([lock_x, lock_y, lock_x + 14, lock_y + 12], radius=2, fill=(88, 166, 255))
    draw.arc([shield_cx - 5, lock_y - 8, shield_cx + 5, lock_y + 2], start=180, end=360, fill=(88, 166, 255), width=2)
    draw.line([(shield_cx, lock_y + 4), (shield_cx, lock_y + 8)], fill=(13, 17, 23), width=2)
    
    # 3. Central Typography & Feature Badges
    text_x = 135
    
    # Header Live Pill
    blink = (math.sin(rad * 2) + 1) / 2
    dot_color = (63, 185, 80) if blink > 0.3 else (27, 85, 38)
    draw.rounded_rectangle([text_x, 62, text_x + 155, 78], radius=8, fill=(22, 27, 34), outline=(48, 54, 61))
    draw.ellipse([text_x + 7, 67, text_x + 13, 73], fill=dot_color)
    draw.text((text_x + 18, 64), "SECURITY AUDIT ENGINE", font=font_badge, fill=(126, 231, 135))
    draw.rounded_rectangle([text_x + 118, 64, text_x + 150, 76], radius=4, fill=(35, 134, 54))
    draw.text((text_x + 122, 65), "ACTIVE", font=font_badge, fill=(255, 255, 255))
    
    # Main Title
    draw.text((text_x, 86), "Find Unprotected Repos", font=font_title, fill=(88, 166, 255))
    
    # Subtitle
    draw.text((text_x, 118), "Automated GitHub Branch Security Auditor", font=font_sub, fill=(139, 148, 158))
    
    # Feature Badges
    pills = ["⚡ 25h Cache", "🍴 Fork Filter", "🔍 Deep Audit", "📟 CLI + UI"]
    px = text_x
    for p in pills:
        pw = int(draw.textlength(p, font=font_pill)) + 12
        draw.rounded_rectangle([px, 142, px + pw, 160], radius=4, fill=(22, 27, 34), outline=(48, 54, 61))
        draw.text((px + 6, 145), p, font=font_pill, fill=(230, 237, 243))
        px += pw + 6
        
    # Command Terminal Snippet
    draw.rounded_rectangle([text_x, 172, text_x + 280, 196], radius=4, fill=(13, 17, 23), outline=(48, 54, 61))
    draw.text((text_x + 8, 178), "$", font=font_mono_bold, fill=(121, 192, 255))
    draw.text((text_x + 20, 178), "python find_unprotected_repos.py", font=font_mono, fill=(230, 237, 243))
    draw.text((text_x + 235, 178), "--fast", font=font_mono, fill=(86, 211, 100))
    
    # 4. Right Side Floating Cards (Animated float)
    card_x = 440
    card_w = 175
    
    # Card 1: Protected (floats with sin wave 1)
    dy1 = int(math.sin(rad) * 3)
    card1_y = 65 + dy1
    draw.rounded_rectangle([card_x, card1_y, card_x + card_w, card1_y + 85], radius=6, fill=(16, 22, 28), outline=(35, 134, 54), width=1)
    # Status dot & repo name
    draw.ellipse([card_x + 8, card1_y + 8, card_x + 16, card1_y + 16], fill=(35, 134, 54))
    draw.text((card_x + 20, card1_y + 7), "repo/production-api", font=font_card_title, fill=(230, 237, 243))
    draw.line([(card_x + 6, card1_y + 24), (card_x + card_w - 6, card1_y + 24)], fill=(48, 54, 61))
    
    draw.text((card_x + 8, card1_y + 30), "branch: main", font=font_mono, fill=(121, 192, 255))
    draw.rounded_rectangle([card_x + 105, card1_y + 28, card_x + card_w - 8, card1_y + 44], radius=3, fill=(35, 134, 54))
    draw.text((card_x + 110, card1_y + 31), "PROTECTED", font=font_badge, fill=(255, 255, 255))
    draw.text((card_x + 8, card1_y + 52), "✓ Reviews & PR Enforced", font=font_card_sub, fill=(126, 231, 135))
    draw.text((card_x + 8, card1_y + 66), "Status: 100% Compliant", font=font_card_sub, fill=(139, 148, 158))
    
    # Card 2: Unprotected (floats with sin wave 2)
    dy2 = int(math.cos(rad) * 3)
    card2_y = 162 + dy2
    card2_outline = (248, 81, 73) if blink > 0.3 else (150, 40, 35)
    draw.rounded_rectangle([card_x, card2_y, card_x + card_w, card2_y + 85], radius=6, fill=(22, 16, 18), outline=card2_outline, width=1)
    # Alert dot
    draw.ellipse([card_x + 8, card2_y + 8, card_x + 16, card2_y + 16], fill=(218, 54, 51))
    draw.text((card_x + 20, card2_y + 7), "repo/internal-tools", font=font_card_title, fill=(230, 237, 243))
    draw.line([(card_x + 6, card2_y + 24), (card_x + card_w - 6, card2_y + 24)], fill=(48, 54, 61))
    
    draw.text((card_x + 8, card2_y + 30), "branch: master", font=font_mono, fill=(240, 136, 62))
    draw.rounded_rectangle([card_x + 95, card2_y + 28, card_x + card_w - 8, card2_y + 44], radius=3, fill=(218, 54, 51))
    draw.text((card_x + 100, card2_y + 31), "UNPROTECTED", font=font_badge, fill=(255, 255, 255))
    draw.text((card_x + 8, card2_y + 52), "⚠ Direct push allowed", font=font_card_sub, fill=(255, 123, 114))
    draw.text((card_x + 8, card2_y + 66), "Action required: Add rules", font=font_card_sub, fill=(139, 148, 158))
    
    # 5. Drifting cyber particles
    for p_idx, (base_px, base_py, col) in enumerate([(410, 80, (88, 166, 255)), (615, 155, (63, 185, 80)), (425, 240, (121, 192, 255))]):
        part_y = base_py + int(math.sin(rad + p_idx) * 4)
        draw.ellipse([base_px - 2, part_y - 2, base_px + 2, part_y + 2], fill=col)
    
    # Convert frame to adaptive palette with dithering for compact GIF size
    p_frame = img.convert("P", palette=Image.ADAPTIVE, colors=96)
    frames.append(p_frame)

script_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(script_dir, "assets")
os.makedirs(assets_dir, exist_ok=True)
out_path = os.path.join(assets_dir, "social-preview.gif")
frames[0].save(
    out_path,
    save_all=True,
    append_images=frames[1:],
    duration=FRAME_DURATION,
    loop=0,
    optimize=True
)

file_size_kb = os.path.getsize(out_path) / 1024
print(f"Generated {out_path}: {file_size_kb:.2f} KB (Target: < 1000 KB, Resolution: 640x320)")

