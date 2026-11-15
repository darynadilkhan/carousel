"""Render an Instagram carousel (1080x1350 PNGs) from a JSON spec.

Usage: python3 gen.py spec.json out_dir
spec = {"brand": "...", "slides": [{"type": "cover"|"point"|"cta", "kicker": "...", "title": "...", "body": "..."}]}
"""
import json, sys, os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
BG = (14, 14, 20)
CARD = (26, 26, 36)
ACCENT = (254, 44, 85)
ACCENT2 = (37, 244, 238)
WHITE = (245, 245, 247)
GREY = (160, 160, 175)
F = "/usr/share/fonts/opentype/inter/"


def font(name, size):
    return ImageFont.truetype(F + name, size)


def wrap(draw, text, fnt, maxw):
    lines = []
    for para in text.split("\n"):
        words, cur = para.split(), ""
        for w in words:
            t = (cur + " " + w).strip()
            if draw.textlength(t, font=fnt) <= maxw:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def block(draw, x, y, text, fnt, fill, maxw, gap=1.25):
    for ln in wrap(draw, text, fnt, maxw):
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += int(fnt.size * gap)
    return y


def fit(draw, text, name, start, minsize, maxw, maxlines):
    s = start
    while s > minsize:
        f = font(name, s)
        if len(wrap(draw, text, f, maxw)) <= maxlines:
            return f
        s -= 4
    return font(name, minsize)


def render(spec, out):
    os.makedirs(out, exist_ok=True)
    slides = spec["slides"]
    n = len(slides)
    paths = []
    for i, s in enumerate(slides, 1):
        im = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(im)
        # accent glow corners
        d.ellipse((-260, -260, 360, 360), fill=(40, 14, 26))
        d.ellipse((W - 300, H - 300, W + 260, H + 260), fill=(10, 40, 44))
        m = 90
        maxw = W - 2 * m
        # top bar
        d.text((m, 70), spec.get("brand", ""), font=font("Inter-SemiBold.otf", 30), fill=GREY)
        cnt = f"{i}/{n}"
        cf = font("Inter-SemiBold.otf", 30)
        d.text((W - m - d.textlength(cnt, font=cf), 70), cnt, font=cf, fill=GREY)
        t = s.get("type", "point")
        if t == "cover":
            y = 300
            if s.get("kicker"):
                kf = font("Inter-Bold.otf", 36)
                kw = d.textlength(s["kicker"], font=kf)
                d.rounded_rectangle((m, y, m + kw + 48, y + 66), 33, fill=ACCENT)
                d.text((m + 24, y + 12), s["kicker"], font=kf, fill=WHITE)
                y += 120
            tf = fit(d, s["title"], "Inter-ExtraBold.otf", 104, 64, maxw, 6)
            y = block(d, m, y, s["title"], tf, WHITE, maxw, 1.12)
            y += 40
            d.rectangle((m, y, m + 140, y + 10), fill=ACCENT2)
            y += 60
            if s.get("body"):
                block(d, m, y, s["body"], font("Inter-Medium.otf", 44), GREY, maxw, 1.35)
            sw = "Солға сырғытыңыз  →"
            sf = font("Inter-SemiBold.otf", 36)
            d.text((W - m - d.textlength(sw, font=sf), H - 130), sw, font=sf, fill=ACCENT2)
        elif t == "cta":
            y = 330
            tf = fit(d, s["title"], "Inter-ExtraBold.otf", 92, 60, maxw, 5)
            y = block(d, m, y, s["title"], tf, WHITE, maxw, 1.12)
            y += 70
            kw = s.get("keyword", "ТАРГЕТ")
            kf = font("Inter-Black.otf", 96)
            bw = d.textlength(kw, font=kf) + 120
            d.rounded_rectangle((m, y, m + bw, y + 170), 40, fill=ACCENT)
            d.text((m + 60, y + 28), kw, font=kf, fill=WHITE)
            y += 240
            if s.get("body"):
                block(d, m, y, s["body"], font("Inter-Medium.otf", 44), GREY, maxw, 1.35)
        else:
            y = 250
            if s.get("kicker"):
                d.text((m, y), s["kicker"], font=font("Inter-Bold.otf", 40), fill=ACCENT)
                y += 80
            tf = fit(d, s["title"], "Inter-ExtraBold.otf", 80, 54, maxw, 4)
            y = block(d, m, y, s["title"], tf, WHITE, maxw, 1.15)
            y += 50
            # body card
            bf = font("Inter-Medium.otf", 42)
            lines = wrap(d, s.get("body", ""), bf, maxw - 100)
            ch = len(lines) * int(42 * 1.4) + 100
            d.rounded_rectangle((m, y, W - m, y + ch), 36, fill=CARD)
            d.rectangle((m, y + 40, m + 8, y + ch - 40), fill=ACCENT2)
            yy = y + 50
            for ln in lines:
                d.text((m + 50, yy), ln, font=bf, fill=WHITE)
                yy += int(42 * 1.4)
            # big faint index number in the lower area
            num = f"{i - 1:02d}"
            nf = font("Inter-Black.otf", 360)
            d.text((m - 10, H - 470), num, font=nf, fill=(34, 34, 46))
        p = os.path.join(out, f"slide_{i:02d}.png")
        im.save(p, optimize=True)
        paths.append(p)
    return paths


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    for p in render(spec, sys.argv[2]):
        print(p)
