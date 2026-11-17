"""Draws the Chapter 4 figures from the CSV results. Usage: python make_charts.py <results_dir> <out_dir>"""
import csv, sys, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

res, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
rows = list(csv.DictReader(open(os.path.join(res, "benchmark_results.csv"))))
scal = list(csv.DictReader(open(os.path.join(res, "scaling_results.csv"))))
ALG = ["RLE", "Huffman", "LZ77", "LZW"]
COL = {"RLE": "#2a78d6", "Huffman": "#eb6834", "LZ77": "#1baf7a", "LZW": "#e87ba4"}
HATCH = {"RLE": "", "Huffman": "//", "LZ77": "..", "LZW": "xx"}
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e3e2de"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK, "text.color": INK})


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID, linewidth=0.8); ax.set_axisbelow(True)


files = []
for r in rows:
    if r["file"] not in files:
        files.append(r["file"])
# Fig 4.x space saving per file
fig, ax = plt.subplots(figsize=(9.2, 4.4), dpi=200)
w = 0.2
for k, a in enumerate(ALG):
    vals = [max(float(r["saving_pct"]), 0) for f in files for r in rows if r["file"] == f and r["algorithm"] == a]
    ax.bar([i + (k - 1.5) * w for i in range(len(files))], vals, w * 0.88, label=a, color=COL[a],
           hatch=HATCH[a], edgecolor="white", linewidth=0.4)
ax.set_xticks(range(len(files)))
ax.set_xticklabels(files, rotation=55, ha="right", fontsize=7.5)
ax.set_ylabel("Space saved (%)"); ax.set_ylim(0, 100); clean(ax)
ax.legend(ncol=4, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.12))
fig.tight_layout(); fig.savefig(os.path.join(out, "fig_saving.png")); plt.close(fig)

# Fig throughput (MB/s) averaged over all corpus files that are >= 500 KB
def avg(alg, key):
    xs = [float(r["original"]) / 1048576 / float(r[key]) for r in rows
          if r["algorithm"] == alg and int(r["original"]) >= 500_000 and float(r[key]) > 0
          and r["used"] != "Stored"]      # 'stored' files skip decoding, so they would inflate speed
    return sum(xs) / len(xs)
fig, ax = plt.subplots(figsize=(6.2, 3.6), dpi=200)
for k, a in enumerate(ALG):
    ax.bar(k - 0.19, avg(a, "comp_s"), 0.36, color=COL[a], hatch=HATCH[a], edgecolor="white", label=None)
    ax.bar(k + 0.19, avg(a, "decomp_s"), 0.36, color=COL[a], alpha=0.45, hatch=HATCH[a], edgecolor="white")
    ax.text(k - 0.19, avg(a, "comp_s") + 0.4, "%.1f" % avg(a, "comp_s"), ha="center", fontsize=8)
    ax.text(k + 0.19, avg(a, "decomp_s") + 0.4, "%.1f" % avg(a, "decomp_s"), ha="center", fontsize=8)
ax.set_xticks(range(4)); ax.set_xticklabels(ALG)
ax.set_ylabel("Throughput (MB/s of original data)"); clean(ax)
ax.text(0.99, 0.97, "solid = compression, light = decompression", transform=ax.transAxes, ha="right", va="top", fontsize=8, color=MUTED)
fig.tight_layout(); fig.savefig(os.path.join(out, "fig_throughput.png")); plt.close(fig)

# Fig scaling
sizes = []
for r in scal:
    if int(r["original"]) not in sizes:
        sizes.append(int(r["original"]))
fig, axs = plt.subplots(1, 2, figsize=(9, 3.6), dpi=200)
for ax, key, ttl in ((axs[0], "comp_s", "Compression time"), (axs[1], "decomp_s", "Decompression time")):
    for a in ALG:
        ys = [float(r[key]) for s in sizes for r in scal if int(r["original"]) == s and r["algorithm"] == a]
        ax.plot([s / 1048576 for s in sizes], ys, marker="o", ms=5, lw=2, color=COL[a], label=a)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xticks([0.1, 1, 5, 10, 50]); ax.set_xticklabels(["0.1", "1", "5", "10", "50"]); ax.set_xlabel("File size (MB)"); ax.set_ylabel("Seconds"); ax.set_title(ttl, fontsize=10, loc="left")
    ax.grid(color=GRID, linewidth=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
axs[0].legend(frameon=False)
fig.tight_layout(); fig.savefig(os.path.join(out, "fig_scaling.png")); plt.close(fig)

# Fig Huffman vs entropy
fig, ax = plt.subplots(figsize=(6.2, 3.8), dpi=200)
pts = [(float(r["entropy_bits"]), 8 * float(r["compressed"]) / float(r["original"])) for r in rows if r["algorithm"] == "Huffman"]
ax.plot([0, 8.3], [0, 8.3], color=MUTED, lw=1, ls="--")
ax.scatter([p[0] for p in pts], [min(p[1], 8.0) for p in pts], s=40, color=COL["Huffman"], edgecolor="white", zorder=3)
ax.set_xlabel("Order-0 Shannon entropy H (bits/byte)"); ax.set_ylabel("Huffman output (bits/byte)")
ax.set_xlim(0, 8.3); ax.set_ylim(0, 8.3); clean(ax)
ax.text(5.0, 4.4, "entropy limit (y = x)", color=MUTED, fontsize=8, rotation=38)
fig.tight_layout(); fig.savefig(os.path.join(out, "fig_entropy.png")); plt.close(fig)
print("charts ok")
