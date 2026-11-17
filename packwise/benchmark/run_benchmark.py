"""Runs every algorithm on every corpus file and writes CSV results (Chapter 4 data).
Usage: python benchmark/run_benchmark.py <corpus_dir> <results_dir> [--scaling]
Each time is the median of 3 runs for files <= 2 MiB, a single run for larger files."""
import csv, json, os, platform, statistics, sys, time, zlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from packwise import container
from packwise.controller import ALGORITHM_NAMES, encode, entropy_bits_per_byte
from packwise.engine import STORED_ID, ALGORITHMS

corpus, results = sys.argv[1], sys.argv[2]
scaling = "--scaling" in sys.argv
os.makedirs(results, exist_ok=True)


def timeit(fn, reps):
    ts, val = [], None
    for _ in range(reps):
        t = time.perf_counter(); val = fn(); ts.append(time.perf_counter() - t)
    return statistics.median(ts), val


rows = []
folders = ["scaling"] if scaling else ["text", "images", "binary"]
for folder in folders:
    d = os.path.join(corpus, folder)
    for name in sorted(os.listdir(d), key=lambda n: (os.path.getsize(os.path.join(d, n)), n)):
        path = os.path.join(d, name)
        data = open(path, "rb").read()
        reps = 3 if len(data) <= 2 << 20 else 1
        h = entropy_bits_per_byte(data)
        for algo in ALGORITHM_NAMES:
            ct, (aid, payload) = timeit(lambda: encode(data, algo), reps)
            blob = container.pack(aid, data, payload, name)
            dt, (back, _, _) = timeit(lambda: container.unpack(blob), reps)
            ok = back == data
            rows.append(dict(category=folder, file=name, original=len(data), algorithm=algo,
                             used=("Stored" if aid == STORED_ID else algo), compressed=len(blob),
                             ratio=len(data) / len(blob), saving_pct=100 - 100 * len(blob) / len(data),
                             comp_s=ct, decomp_s=dt, verified=ok, entropy_bits=h))
            print(folder, name, algo, len(data), len(blob), "%.2f" % rows[-1]["ratio"], "%.3f" % ct, "%.3f" % dt, ok, flush=True)
        ct, z = timeit(lambda: zlib.compress(data, 6), reps)
        dt, _ = timeit(lambda: zlib.decompress(z), reps)
        rows.append(dict(category=folder, file=name, original=len(data), algorithm="zlib-6 (reference)", used="zlib",
                         compressed=len(z), ratio=len(data) / len(z), saving_pct=100 - 100 * len(z) / len(data),
                         comp_s=ct, decomp_s=dt, verified=True, entropy_bits=h))
out = os.path.join(results, "scaling_results.csv" if scaling else "benchmark_results.csv")
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
env = dict(platform=platform.platform(), python=platform.python_version(), machine=platform.machine(),
           processor=platform.processor(), cpu_count=os.cpu_count(), date=time.strftime("%Y-%m-%d"))
json.dump(env, open(os.path.join(results, "environment.json"), "w"), indent=2)
print("wrote", out)
