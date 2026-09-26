# -*- coding: utf-8 -*-
"""캡처 프레임 위에 한글 자막/카드를 얹는다. 오디오는 없으므로 자막이 해설을 대신한다."""
import os, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = os.environ.get("PROMO_WORK", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_work"))
sys.path.insert(0, S)
from bp_story import SHOTS, FPS, TOTAL

RAW = os.path.join(S, 'bp_raw'); OUT = os.path.join(S, 'bp_out')
os.makedirs(OUT, exist_ok=True)
W, H = 1920, 1080
BD = 'C:/Windows/Fonts/malgunbd.ttf'; RG = 'C:/Windows/Fonts/malgun.ttf'
F = lambda p, s: ImageFont.truetype(p, s)
f_title = F(BD, 76); f_sub = F(BD, 34); f_note = F(RG, 26)
f_cchap = F(BD, 40); f_ctitle = F(BD, 92)
f_ktag = F(BD, 30); f_khead = F(BD, 46); f_kbody = F(RG, 29)

ACC = (255, 193, 68)      # 앱 헤더의 주황
INK = (232, 237, 247)
DIM = (150, 165, 195)

def ease(u):            # 부드러운 진입/퇴장
    return u*u*(3-2*u)

def fade(u, inn=0.14, out=0.14):
    a = 1.0
    if u < inn:      a = ease(u/inn)
    if u > 1-out:    a = ease((1-u)/out)
    return max(0.0, min(1.0, a))

def band(im, box, alpha, radius=18, fill=(8, 12, 22)):
    """반투명 라운드 박스 — 배경이 밝아도 글씨가 읽히게."""
    ov = Image.new('RGBA', im.size, (0,0,0,0))
    ImageDraw.Draw(ov).rounded_rectangle(box, radius, fill=fill + (int(216*alpha),))
    return Image.alpha_composite(im, ov)

def text(d, xy, s, font, col, a, anchor='la'):
    d.text(xy, s, font=font, fill=col + (int(255*a),), anchor=anchor)

def draw_lower_third(im, cap, a):
    """3D 화면 위 좌하단 자막 — 앱 하단 툴바(y≈1035)를 피해 배치."""
    tag, head, body = cap
    d0 = ImageDraw.Draw(im)
    wmax = max(d0.textlength(head, f_khead), d0.textlength(body, f_kbody),
               d0.textlength(tag, f_ktag)) + 76
    x0, y0 = 250, 790
    im = band(im, (x0, y0, x0 + wmax, y0 + 186), a)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x0+34, y0+30, x0+40, y0+150), 3, fill=ACC+(int(255*a),))
    text(d, (x0+58, y0+28), tag,  f_ktag,  ACC, a)
    text(d, (x0+58, y0+72), head, f_khead, INK, a)
    text(d, (x0+58, y0+132), body, f_kbody, DIM, a)
    return im

def draw_card(im, shot, a):
    """큰 카테고리 전환 카드 — 화면을 어둡게 덮고 챕터를 크게."""
    sc = Image.new('RGBA', im.size, (6, 9, 18, int(232*a)))
    im = Image.alpha_composite(im.filter(ImageFilter.GaussianBlur(9)), sc)
    d = ImageDraw.Draw(im)
    cy = H//2
    text(d, (W//2, cy-126), shot['chapter'], f_ctitle, ACC, a, 'mm')
    text(d, (W//2, cy-18),  shot['title'],   f_ctitle, INK, a, 'mm')
    d.line((W//2-150, cy+58, W//2+150, cy+58), fill=ACC+(int(200*a),), width=3)
    text(d, (W//2, cy+104), shot['sub'],  f_sub,  INK, a, 'mm')
    text(d, (W//2, cy+156), shot['note'], f_note, DIM, a, 'mm')
    return im

def draw_title(im, shot, a, u, outro=False):
    sc = Image.new('RGBA', im.size, (6, 9, 18, int((214 if outro else 188)*a)))
    im = Image.alpha_composite(im.filter(ImageFilter.GaussianBlur(5 if not outro else 8)), sc)
    d = ImageDraw.Draw(im)
    cy = H//2 - (20 if not outro else 0)
    text(d, (W//2, cy-56), shot['title'], f_title, INK, a, 'mm')
    d.line((W//2-190, cy+2, W//2+190, cy+2), fill=ACC+(int(210*a),), width=3)
    text(d, (W//2, cy+50),  shot['sub'],  f_sub,  ACC, a, 'mm')
    text(d, (W//2, cy+108), shot['note'], f_note, DIM, a, 'mm')
    return im

def main():
    bounds, t = [], 0
    for s in SHOTS: bounds.append((t, t+s['n'], s)); t += s['n']
    made = 0
    for i in range(TOTAL):
        src = os.path.join(RAW, 'f%05d.png' % i)
        dst = os.path.join(OUT, 'f%05d.png' % i)
        if not os.path.exists(src):
            print('누락:', src); return 1
        if os.path.exists(dst): continue
        lo, hi, shot = next(b for b in bounds if b[0] <= i < b[1])
        u = (i - lo) / max(hi - lo - 1, 1)
        im = Image.open(src).convert('RGBA')
        k = shot['kind']
        if k == 'card':    im = draw_card(im, shot, fade(u, .18, .18))
        elif k == 'title': im = draw_title(im, shot, fade(u, .16, .12), u)
        elif k == 'outro': im = draw_title(im, shot, fade(u, .14, .10), u, True)
        else:              im = draw_lower_third(im, shot['cap'], fade(u, .16, .16))
        im.convert('RGB').save(dst)
        made += 1
        if made % 120 == 0: print('  합성 %d' % made, flush=True)
    print('합성 완료 (신규 %d)' % made)
    return 0

if __name__ == '__main__':
    sys.exit(main())
