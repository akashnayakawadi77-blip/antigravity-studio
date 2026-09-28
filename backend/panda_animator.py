import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

# ── Panda Sprite Frames (generated cartoon images) ──────────────────────────
ARTIFACT_DIR = r"C:\Users\Admin\.gemini\antigravity\brain\2f2fa8c6-0f72-478a-b69b-57e2a4979c63"

PANDA_FRAMES = {
    "idle":     os.path.join(ARTIFACT_DIR, "panda_idle_1782823252018.png"),
    "talk_open":os.path.join(ARTIFACT_DIR, "panda_talking_open_1782823224053.png"),
    "talk_mid": os.path.join(ARTIFACT_DIR, "panda_talking_mid_1782823234168.png"),
    "wave":     os.path.join(ARTIFACT_DIR, "panda_wave_1782823262832.png"),
    "pointing": os.path.join(ARTIFACT_DIR, "panda_pointing_1782823279017.png"),
}

# Talking animation cycle: idle → talk_mid → talk_open → talk_mid → idle
TALK_CYCLE = ["idle", "talk_mid", "talk_open", "talk_mid", "idle", "talk_mid"]
WAVE_CYCLE = ["wave", "idle", "wave", "idle"]

# ── Destination Cinematic Color Themes ──────────────────────────────────────
DESTINATION_THEMES = {
    "default":   {"sky": [(15,32,39),(32,78,96)],    "ground": (20,50,60),   "accent": (79,195,247)},
    "goa":       {"sky": [(10,40,80),(255,120,40)],  "ground": (180,140,80), "accent": (255,200,50)},
    "kerala":    {"sky": [(10,60,30),(20,100,50)],   "ground": (30,90,40),   "accent": (100,220,100)},
    "leh":       {"sky": [(10,30,80),(50,80,160)],   "ground": (120,100,80), "accent": (150,200,255)},
    "ladakh":    {"sky": [(10,30,80),(50,80,160)],   "ground": (120,100,80), "accent": (150,200,255)},
    "jaipur":    {"sky": [(60,20,10),(180,80,20)],   "ground": (200,150,80), "accent": (255,160,50)},
    "kashmir":   {"sky": [(10,40,80),(70,120,170)],  "ground": (80,130,80),  "accent": (180,230,255)},
    "rajasthan": {"sky": [(60,20,10),(180,80,20)],   "ground": (200,150,80), "accent": (255,160,50)},
    "mumbai":    {"sky": [(10,20,50),(30,50,120)],   "ground": (40,40,60),   "accent": (255,220,100)},
    "delhi":     {"sky": [(20,10,40),(80,30,90)],    "ground": (60,40,80),   "accent": (255,150,200)},
    "varanasi":  {"sky": [(80,40,10),(200,100,20)],  "ground": (160,100,40), "accent": (255,180,50)},
    "shimla":    {"sky": [(10,30,60),(30,60,120)],   "ground": (80,100,80),  "accent": (200,230,255)},
    "andaman":   {"sky": [(10,80,100),(20,140,160)], "ground": (200,180,100),"accent": (100,240,220)},
    "udaipur":   {"sky": [(40,10,30),(120,30,80)],   "ground": (160,120,80), "accent": (255,150,200)},
    "rishikesh": {"sky": [(10,60,40),(20,110,70)],   "ground": (40,100,60),  "accent": (150,255,180)},
    "spiti":     {"sky": [(10,20,50),(40,70,130)],   "ground": (120,100,80), "accent": (150,200,255)},
    "munnar":    {"sky": [(10,50,20),(20,90,40)],    "ground": (30,100,30),  "accent": (100,220,80)},
}

# ── Font Helper ──────────────────────────────────────────────────────────────
def _get_font(size: int, bold: bool = False):
    candidates = [
        "arialbd.ttf" if bold else "arial.ttf",
        "Arial Bold.ttf" if bold else "Arial.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    ]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _get_theme(destination: str) -> dict:
    for key, theme in DESTINATION_THEMES.items():
        if key in destination.lower():
            return theme
    return DESTINATION_THEMES["default"]


# ── Background Scene Generator ───────────────────────────────────────────────
def _make_cartoon_bg(W: int, H: int, theme: dict, frame_idx: int) -> Image.Image:
    """Create a cartoon-style animated background scene."""
    sky_colors = theme["sky"]
    ground_color = theme["ground"]
    accent = theme["accent"]

    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)

    # Sky gradient
    c1, c2 = sky_colors[0], sky_colors[1]
    horizon = int(H * 0.65)
    for y in range(horizon):
        t = y / horizon
        r = int(c1[0] + (c2[0]-c1[0])*t)
        g = int(c1[1] + (c2[1]-c1[1])*t)
        b = int(c1[2] + (c2[2]-c1[2])*t)
        draw.line([(0,y),(W,y)], fill=(r,g,b))

    # Animated cartoon clouds
    for i, (cx, cy, size) in enumerate([(180,80,90),(420,55,70),(680,90,80),(900,65,60),(1100,75,85)]):
        drift = int(15 * math.sin(frame_idx * 0.015 + i * 1.2))
        cx2 = (cx + drift) % W
        cl = (255,255,255,200)
        # Cloud puffs
        for dx, dy, r in [(0,0,size),(size//2,-size//4,size*2//3),(size,0,size*4//5),(-size//2,-size//5,size*3//5)]:
            x0, y0 = cx2+dx-r, cy+dy-r
            draw.ellipse([x0,y0,x0+r*2,y0+r*2], fill=(255,255,255))

    # Ground / terrain
    for y in range(horizon, H):
        t = (y - horizon) / (H - horizon)
        r = int(ground_color[0] * (1-t*0.3))
        g = int(ground_color[1] * (1-t*0.3))
        b = int(ground_color[2] * (1-t*0.3))
        draw.line([(0,y),(W,y)], fill=(r,g,b))

    # Rolling cartoon hills
    for hx in range(-50, W+50, 220):
        offset = int(20 * math.sin(frame_idx * 0.008 + hx * 0.003))
        hill_pts = []
        for x in range(hx-200, hx+200):
            y_hill = horizon + 5 - int(90 * math.exp(-((x-hx)**2)/(2*90**2))) + offset
            hill_pts.append((x, y_hill))
        hill_pts += [(hx+200, H), (hx-200, H)]
        try:
            draw.polygon(hill_pts, fill=(
                min(255,ground_color[0]+20),
                min(255,ground_color[1]+30),
                min(255,ground_color[2]+10)
            ))
        except Exception:
            pass

    # Animated birds flying across sky
    for b_idx in range(3):
        bx = int((frame_idx * 2.5 + b_idx * 370) % (W + 100)) - 50
        by = 60 + b_idx * 30
        wing = int(8 * math.sin(frame_idx * 0.3 + b_idx))
        draw.arc([bx-12, by-wing-4, bx, by+4], 0, 180, fill=(40,40,40), width=2)
        draw.arc([bx, by-wing-4, bx+12, by+4], 0, 180, fill=(40,40,40), width=2)

    # Stars/sparkle accents (destination colour)
    rng = np.random.RandomState(42)
    for _ in range(8):
        sx = rng.randint(50, W-50)
        sy = rng.randint(20, horizon-20)
        pulse = 0.5 + 0.5 * math.sin(frame_idx * 0.1 + sx)
        r2 = int(4 * pulse)
        if r2 > 0:
            draw.ellipse([sx-r2, sy-r2, sx+r2, sy+r2], fill=accent)

    return img


# ── Panda Sprite Loader ───────────────────────────────────────────────────────
_sprite_cache = {}

def _load_panda_sprite(key: str, size: tuple) -> Image.Image:
    cache_key = (key, size)
    if cache_key in _sprite_cache:
        return _sprite_cache[cache_key]
    path = PANDA_FRAMES.get(key, PANDA_FRAMES["idle"])
    try:
        img = Image.open(path).convert("RGBA")
        # Remove near-white background to get transparency
        data = img.getdata()
        new_data = []
        for px in data:
            if px[0] > 230 and px[1] > 230 and px[2] > 230:
                new_data.append((255,255,255,0))
            else:
                new_data.append(px)
        img.putdata(new_data)
        img = img.resize(size, Image.LANCZOS)
    except Exception as e:
        print(f"  Sprite load error ({key}): {e}")
        img = Image.new("RGBA", size, (0,0,0,0))
    _sprite_cache[cache_key] = img
    return img


# ── Caption / Speech Box ──────────────────────────────────────────────────────
def _draw_caption(draw: ImageDraw, W: int, H: int, text: str, accent: tuple):
    if not text:
        return
    words = text.split()
    lines, line = [], []
    for w in words:
        if sum(len(x)+1 for x in line)+len(w) > 58:
            lines.append(' '.join(line)); line = [w]
        else:
            line.append(w)
    if line: lines.append(' '.join(line))
    lines = lines[:3]

    font = _get_font(26, bold=False)
    font_b = _get_font(26, bold=True)
    lh = 34
    box_h = len(lines)*lh + 24
    box_y = H - box_h - 18
    box_x = 20

    # Rounded caption box
    draw.rounded_rectangle([box_x, box_y, W-20, box_y+box_h], radius=14,
                            fill=(0,0,0,200), outline=accent, width=2)
    for i, ln in enumerate(lines):
        draw.text((box_x+16, box_y+12+i*lh), ln, fill=(255,255,255), font=font)


# ── Speech Bubble (for panda) ─────────────────────────────────────────────────
def _draw_speech_bubble(img: Image.Image, text: str, panda_x: int, panda_y: int,
                        W: int, accent: tuple):
    if not text or len(text) < 5:
        return img
    draw = ImageDraw.Draw(img)
    font = _get_font(20)
    words = text.split()[:12]
    short = ' '.join(words) + ('...' if len(text.split()) > 12 else '')

    bw, bh = min(380, len(short)*9+30), 50
    bx = min(panda_x + 50, W - bw - 20)
    by = panda_y - 60

    if by < 70: by = panda_y + 10

    draw.rounded_rectangle([bx, by, bx+bw, by+bh], radius=12,
                            fill=(255,255,255,235), outline=accent, width=2)
    # Tail
    tail_x = bx + 20
    draw.polygon([(tail_x, by+bh), (tail_x+14, by+bh), (panda_x+40, by+bh+18)],
                 fill=(255,255,255,235))
    draw.text((bx+12, by+12), short, fill=(30,30,30), font=font)
    return img


# ── Main Frame Creator ────────────────────────────────────────────────────────
def create_panda_frame(width: int, height: int, caption_text: str,
                       destination: str, frame_index: int, total_frames: int,
                       is_talking: bool = True) -> np.ndarray:
    """
    Create a single fully animated cartoon frame with:
    - Animated cartoon background (sky, clouds, hills, birds)
    - Animated panda character (cycling between talking frames)
    - Floating destination tag
    - Channel branding
    - Caption bar
    - Speech bubble
    """
    theme = _get_theme(destination)
    accent = theme["accent"]

    # ── Background ────────────────────────────────────────────────────────────
    bg = _make_cartoon_bg(width, height, theme, frame_index)
    draw = ImageDraw.Draw(bg)

    # ── Top Branding Bar ──────────────────────────────────────────────────────
    bar_h = 62
    bar = Image.new("RGBA", (width, bar_h), (0,0,0,180))
    bg.paste(bar.convert("RGB"), (0,0), bar)
    draw = ImageDraw.Draw(bg)
    font_brand = _get_font(28, bold=True)
    font_dest  = _get_font(22, bold=True)
    draw.text((18, 14), "TRAVELING PANDA", fill=accent, font=font_brand)
    draw.text((18+len("TRAVELING PANDA")*17+8, 18), "| India Travel", fill=(200,200,200), font=_get_font(20))

    # Destination pill (top right)
    dest_text = destination.upper()
    pill_w = len(dest_text)*14 + 30
    pill_x = width - pill_w - 16
    draw.rounded_rectangle([pill_x, 12, pill_x+pill_w, 50], radius=18, fill=accent)
    draw.text((pill_x+15, 17), dest_text, fill=(20,20,20), font=font_dest)

    # ── Animated Panda Character ──────────────────────────────────────────────
    # Choose sprite based on frame
    if is_talking:
        cycle_pos = (frame_index // 6) % len(TALK_CYCLE)
        sprite_key = TALK_CYCLE[cycle_pos]
    else:
        cycle_pos = (frame_index // 15) % len(WAVE_CYCLE)
        sprite_key = WAVE_CYCLE[cycle_pos]

    panda_size = (360, 420)
    panda_sprite = _load_panda_sprite(sprite_key, panda_size)

    # Breathing/bobbing animation
    bob = int(8 * math.sin(frame_index * 0.06))
    panda_x = width // 2 - panda_size[0] // 2
    panda_y = height - panda_size[1] - 80 + bob

    # Drop shadow under panda
    shadow = Image.new("RGBA", (panda_size[0], 30), (0,0,0,0))
    sh_draw = ImageDraw.Draw(shadow)
    sh_draw.ellipse([20,0,panda_size[0]-20,28], fill=(0,0,0,70))
    bg.paste(shadow.convert("RGB"), (panda_x, panda_y+panda_size[1]-10), shadow)

    # Paste panda
    bg.paste(panda_sprite.convert("RGB"), (panda_x, panda_y), panda_sprite)

    # ── Speech Bubble ─────────────────────────────────────────────────────────
    if is_talking and caption_text and frame_index % 90 < 75:
        bg = _draw_speech_bubble(bg, caption_text, panda_x+panda_size[0]//2,
                                  panda_y, width, accent)

    draw = ImageDraw.Draw(bg)

    # ── Floating Travel Icons (animated) ─────────────────────────────────────
    icons = ["✈", "🗺", "🎒", "📍", "⭐"]
    for i, icon in enumerate(icons):
        ix = int(60 + i * (width/len(icons)))
        iy = int(90 + 20 * math.sin(frame_index * 0.04 + i * 1.3))
        try:
            draw.text((ix, iy), icon, fill=(255,255,255,180), font=_get_font(22))
        except Exception:
            pass

    # ── Subscribe CTA (pulsing red button, flashes every 5s) ─────────────────
    cta_pulse = 0.85 + 0.15 * math.sin(frame_index * 0.15)
    if (frame_index // 120) % 2 == 0:
        cta_w = int(220 * cta_pulse)
        cta_x = width - cta_w - 18
        cta_y = height - 58
        draw.rounded_rectangle([cta_x, cta_y, cta_x+cta_w, cta_y+40],
                                radius=20, fill=(220, 40, 40))
        draw.text((cta_x+22, cta_y+8), "SUBSCRIBE  +  BELL",
                  fill=(255,255,255), font=_get_font(16, bold=True))

    # ── Caption Bar at bottom ─────────────────────────────────────────────────
    _draw_caption(draw, width, height, caption_text, accent)

    return np.array(bg)


# ── B-Roll Overlay Frame ──────────────────────────────────────────────────────
def create_broll_frame(width: int, height: int, label_text: str,
                       destination: str, frame_index: int) -> np.ndarray:
    """
    Create a cinematic B-roll style frame with location title overlay
    (used when no real video clip is available).
    """
    theme = _get_theme(destination)
    accent = theme["accent"]

    bg = _make_cartoon_bg(width, height, theme, frame_index)
    draw = ImageDraw.Draw(bg)

    # Cinematic letterbox bars
    bar_h = 55
    draw.rectangle([0,0,width,bar_h], fill=(0,0,0,200))
    draw.rectangle([0,height-bar_h,width,height], fill=(0,0,0,200))

    # Channel name top
    draw.text((18, 14), "TRAVELING PANDA", fill=accent, font=_get_font(26, bold=True))

    # Destination title (large, centered)
    font_big = _get_font(64, bold=True)
    dest_name = destination.upper()
    # Shadow
    draw.text((width//2 - len(dest_name)*18 + 3, height//2 - 46),
              dest_name, fill=(0,0,0,140), font=font_big)
    draw.text((width//2 - len(dest_name)*18, height//2 - 48),
              dest_name, fill=(255,255,255), font=font_big)

    # Subtitle label
    if label_text:
        sub = label_text[:70]
        draw.text((width//2 - len(sub)*7, height//2 + 28),
                  sub, fill=accent, font=_get_font(24))

    # Location pin + animated pulse
    pin_x, pin_y = width//2, height//2 - 110
    pulse_r = int(20 + 8 * math.sin(frame_index * 0.1))
    draw.ellipse([pin_x-pulse_r, pin_y-pulse_r, pin_x+pulse_r, pin_y+pulse_r],
                 outline=accent, width=3)
    draw.ellipse([pin_x-8, pin_y-8, pin_x+8, pin_y+8], fill=accent)

    return np.array(bg)
