"""Builds the benchmark corpus used in Chapter 4 (deterministic: fixed seeds; text taken from the
Python standard library so the same material exists on every machine that has Python).
Usage:  python benchmark/make_corpus.py [output_dir]"""
import glob, os, random, sys, sysconfig, zipfile
from PIL import Image, ImageDraw, ImageFilter

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "corpus")
for sub in ("text", "images", "binary", "scaling"):
    os.makedirs(os.path.join(out, sub), exist_ok=True)
rnd = random.Random(2026)


def w(sub, name, data):
    p = os.path.join(out, sub, name)
    with open(p, "wb") as f:
        f.write(data)
    return p


# ---- text -------------------------------------------------------------------
from pydoc_data.topics import topics
prose = "\n\n".join(topics[k] for k in sorted(topics)).encode("utf-8")
w("text", "english_5KB.txt", prose[:5 * 1024])
w("text", "english_100KB.txt", prose[:100 * 1024])
w("text", "english_548KB.txt", prose)      # whole text, no repetition
stdlib = sysconfig.get_paths()["stdlib"]
code = b""
for f in sorted(glob.glob(os.path.join(stdlib, "*.py"))):
    with open(f, "rb") as fh:
        code += fh.read()
w("text", "source_code_500KB.py", code[:500 * 1024])

names = ["Yusuf", "Ene", "Ovey", "David", "Okwe", "Ajayi", "Suleiman", "Musa", "Ibrahim", "Aisha"]
rows = ["id,name,department,level,score,cgpa,email"]
for i in range(1, 30001):
    n = rnd.choice(names)
    rows.append("%d,%s,%s,%d,%d,%.2f,%s%d@nsuk.edu.ng" % (i, n, rnd.choice(["CSC", "SEN", "CYB", "IFT"]),
                rnd.choice([100, 200, 300, 400]), rnd.randrange(30, 100), rnd.uniform(1.5, 5.0), n.lower(), i))
w("text", "student_records_1MB.csv", "\n".join(rows).encode()[:1048576])
levels = ["INFO", "INFO", "INFO", "WARN", "ERROR", "DEBUG"]
msgs = ["User login successful", "File uploaded", "Connection timed out", "Cache miss", "Request completed in %dms"]
lines = []
for i in range(40000):
    m = rnd.choice(msgs)
    if "%d" in m:
        m = m % rnd.randrange(5, 900)
    lines.append("2026-03-%02d %02d:%02d:%02d [%s] server-%d: %s" % (1 + i // 2000 % 28, i // 100 % 24, i % 60, i * 7 % 60,
                 rnd.choice(levels), rnd.randrange(1, 5), m))
w("text", "server_log_1MB.log", "\n".join(lines).encode()[:1048576])

# ---- images -----------------------------------------------------------------
W = H = 512
g = Image.new("RGB", (W, H))
px = g.load()
for y in range(H):
    for x in range(W):
        px[x, y] = (x * 255 // W, y * 255 // H, (x + y) * 255 // (W + H))
d = ImageDraw.Draw(g)
for _ in range(25):
    x, y = rnd.randrange(W), rnd.randrange(H)
    d.ellipse((x, y, x + rnd.randrange(20, 120), y + rnd.randrange(20, 120)), fill=tuple(rnd.randrange(256) for _ in range(3)))
g.save(os.path.join(out, "images", "synthetic_gradient_512.bmp"))

doc = Image.new("RGB", (800, 600), "white")
d = ImageDraw.Draw(doc)
for row in range(25):
    d.text((40, 20 + row * 22), "Scanned document line %d - compression test text " % row * 2, fill="black")
doc.save(os.path.join(out, "images", "scanned_document_800x600.bmp"))

noise = Image.effect_noise((W, H), 90).convert("RGB")
photo = Image.blend(g, noise.filter(ImageFilter.GaussianBlur(1.2)), 0.35)
photo.save(os.path.join(out, "images", "photo_like_512.bmp"))
photo.save(os.path.join(out, "images", "photo_like_512.jpg"), quality=85)

# ---- binary -----------------------------------------------------------------
import sys as _s
cands = [_s.executable] + glob.glob(os.path.join(stdlib, "lib-dynload", "*.so")) + glob.glob(os.path.join(os.path.dirname(_s.executable), "*"))
cands = [c for c in cands if os.path.isfile(c)]
exe = max(cands, key=lambda c: min(os.path.getsize(c), 2 << 20))
with open(exe, "rb") as f:
    w("binary", "executable_2MB.bin", f.read(2 << 20))
w("binary", "random_1MB.bin", rnd.randbytes(1 << 20))
sp = bytearray(2 << 20)
for _ in range(3000):
    p = rnd.randrange(len(sp) - 40)
    sp[p:p + rnd.randrange(1, 40)] = rnd.randbytes(rnd.randrange(1, 40))[:len(sp) - p]
w("binary", "sparse_2MB.bin", bytes(sp)[:2 << 20])
zp = os.path.join(out, "binary", "archive_deflated.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(out, "text", "english_548KB.txt"), "english.txt")

# ---- scaling series (source code of increasing size) ---------------------------
big = b""
for f in sorted(glob.glob(os.path.join(stdlib, "**", "*.py"), recursive=True)):
    try:
        with open(f, "rb") as fh:
            big += fh.read()
    except OSError:
        pass
    if len(big) >= 50 * 1048576:
        break
while len(big) < 50 * 1048576:         # tiny stdlib? repeat to reach 50 MB
    big += big
for label, size in (("100KB", 100 << 10), ("1MB", 1 << 20), ("5MB", 5 << 20), ("10MB", 10 << 20), ("50MB", 50 << 20)):
    w("scaling", "source_%s.txt" % label, big[:size])
print("corpus written to", out)
