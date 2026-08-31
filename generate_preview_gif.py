import math
import os
from PIL import Image, ImageDraw, ImageFont

WIDTH = 640
HEIGHT = 320
NUM_FRAMES = 36
FRAME_DURATION = 55  # ~18 fps -> 2 second smooth loop

TOP_PAD = 50
BOT_PAD = 50
CONTENT_Y_START = TOP_PAD
CONTENT_Y_END = HEIGHT - BOT_PAD  # 270

# Load fonts
try:
    font_title = ImageFont.truetype("segoeuib.ttf", 20)
    font_sub = ImageFont.truetype("segoeui.ttf", 10)
    font_badge = ImageFont.truetype("segoeuib.ttf", 9)
    font_pill = ImageFont.truetype("segoeui.ttf", 9)
    font_mono = ImageFont.truetype("consola.ttf", 10)
    font_mono_bold = ImageFont.truetype("consolab.ttf", 10)
except Exception:
    font_title = ImageFont.load_default()
    font_sub = ImageFont.load_default()
    font_badge = ImageFont.load_default()
    font_pill = ImageFont.load_default()
    font_mono = ImageFont.load_default()
    font_mono_bold = ImageFont.load_default()

def lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

def create_base_bg():
    bg = Image.new("RGB", (WIDTH, HEIGHT), (13, 17, 23))
    draw = ImageDraw.Draw(bg)
    
    # Background gradient
    for y in range(HEIGHT):
        t = y / HEIGHT
        col = lerp_color((8, 12, 20), (20, 26, 35), t)
        draw.line([(0, y), (WIDTH, y)], fill=col)
    
    # Subtle cyber grid
    grid_spacing = 20
    for x in range(0, WIDTH, grid_spacing):
        draw.line([(x, 0), (x, HEIGHT)], fill=(30, 36, 45, 128), width=1)
    for y in range(0, HEIGHT, grid_spacing):
        draw.line([(0, y), (WIDTH, y)], fill=(30, 36, 45, 128), width=1)
    
    # Inner border for the content section (50px top and bottom padding)
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
    for offset in range(-25, 26):
        x = scan_x + offset
        if 16 <= x <= WIDTH - 16:
            alpha = max(0, 1.0 - abs(offset) / 25.0)
            glow_col = lerp_color((13, 17, 23), (88, 166, 255), alpha * 0.16)
            draw.line([(x, TOP_PAD + 1), (x, CONTENT_Y_END - 1)], fill=glow_col, width=1)
    
    # 2. Glowing Shield Emblem (Centered top: cx=320, cy=82)
    shield_cx = 320
    shield_cy = 76
    pulse = (math.sin(rad) + 1) / 2
    
    # Rotating Radar Ring
    radar_angle = progress * 2 * math.pi
    r_radius = 28 + int(pulse * 3)
    num_dashes = 10
    for i in range(num_dashes):
        a = radar_angle + (i * (2 * math.pi / num_dashes))
        x1 = shield_cx + math.cos(a) * (r_radius - 3)
        y1 = shield_cy + math.sin(a) * (r_radius - 3)
        x2 = shield_cx + math.cos(a) * (r_radius + 2)
        y2 = shield_cy + math.sin(a) * (r_radius + 2)
        draw.line([(x1, y1), (x2, y2)], fill=(31, 111, 235), width=1)
        
    # Shield Outer Glow
    glow_r = int(22 + pulse * 4)
    glow_col = lerp_color((13, 17, 23), (88, 166, 255), 0.35 + pulse * 0.25)
    draw.ellipse([shield_cx - glow_r, shield_cy - glow_r, shield_cx + glow_r, shield_cy + glow_r], fill=glow_col)
    
    # Shield shape
    s_top = shield_cy - 16
    s_bot = shield_cy + 18
    s_left = shield_cx - 15
    s_right = shield_cx + 15
    shield_pts = [
        (shield_cx, s_top - 3),
        (s_right, s_top + 3),
        (s_right, shield_cy + 4),
        (shield_cx, s_bot),
        (s_left, shield_cy + 4),
        (s_left, s_top + 3)
    ]
    draw.polygon(shield_pts, fill=(13, 17, 23), outline=(88, 166, 255))
    
    # Shield lock symbol
    draw.rounded_rectangle([shield_cx - 5, shield_cy - 1, shield_cx + 5, shield_cy + 8], radius=1, fill=(88, 166, 255))
    draw.arc([shield_cx - 4, shield_cy - 6, shield_cx + 4, shield_cy + 1], start=180, end=360, fill=(88, 166, 255), width=1)
    
    # Status checkmark badge on shield
    draw.ellipse([shield_cx + 10, s_top + 2, shield_cx + 18, s_top + 10], fill=(35, 134, 54))
    
    # 3. Top Status Pill (Centered)
    blink = (math.sin(rad * 2) + 1) / 2
    dot_color = (63, 185, 80) if blink > 0.3 else (27, 85, 38)
    pill_w = 170
    pill_x = shield_cx - (pill_w // 2)
    pill_y = 106
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + 18], radius=9, fill=(22, 27, 34), outline=(48, 54, 61))
    draw.ellipse([pill_x + 6, pill_y + 5, pill_x + 12, pill_y + 11], fill=dot_color)
    draw.text((pill_x + 16, pill_y + 3), "SECURITY AUDIT ENGINE", font=font_badge, fill=(126, 231, 135))
    draw.rounded_rectangle([pill_x + 128, pill_y + 2, pill_x + 164, pill_y + 15], radius=4, fill=(35, 134, 54))
    draw.text((pill_x + 132, pill_y + 3), "ACTIVE", font=font_badge, fill=(255, 255, 255))
    
    # 4. Centered Title
    title_str = "Find Unprotected Repos"
    tw = int(draw.textlength(title_str, font=font_title))
    draw.text((shield_cx - (tw // 2), 132), title_str, font=font_title, fill=(88, 166, 255))
    
    # 5. Centered Subtitle
    sub_str = "Automate GitHub branch protection & security posture audits in seconds."
    sw = int(draw.textlength(sub_str, font=font_sub))
    draw.text((shield_cx - (sw // 2), 160), sub_str, font=font_sub, fill=(139, 148, 158))
    
    # 6. Centered Feature Badges
    pills = ["⚡ 25h Cache", "🍴 Fork Filter", "🔍 Deep Audit", "📟 CLI + Web UI"]
    pill_widths = [int(draw.textlength(p, font=font_pill)) + 12 for p in pills]
    total_pills_w = sum(pill_widths) + (len(pills) - 1) * 6
    px = shield_cx - (total_pills_w // 2)
    py = 184
    for i, p in enumerate(pills):
        pw = pill_widths[i]
        draw.rounded_rectangle([px, py, px + pw, py + 18], radius=4, fill=(22, 27, 34), outline=(48, 54, 61))
        draw.text((px + 6, py + 3), p, font=font_pill, fill=(230, 237, 243))
        px += pw + 6
        
    # 7. Centered Terminal Prompt Box
    term_w = 340
    term_x = shield_cx - (term_w // 2)
    term_y = 214
    draw.rounded_rectangle([term_x, term_y, term_x + term_w, term_y + 26], radius=5, fill=(13, 17, 23), outline=(48, 54, 61))
    draw.text((term_x + 10, term_y + 6), "$", font=font_mono_bold, fill=(121, 192, 255))
    draw.text((term_x + 24, term_y + 6), "python find_unprotected_repos.py", font=font_mono, fill=(230, 237, 243))
    draw.text((term_x + 280, term_y + 6), "--audit", font=font_mono, fill=(86, 211, 100))
    
    # 8. Floating ambient particles
    for p_idx, (bx, by, col) in enumerate([(60, 110, (88, 166, 255)), (80, 210, (63, 185, 80)), (570, 110, (88, 166, 255)), (550, 210, (63, 185, 80))]):
        dy = int(math.sin(rad + p_idx) * 4)
        draw.ellipse([bx - 2, by + dy - 2, bx + 2, by + dy + 2], fill=col)
    
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
