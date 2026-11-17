"""Scores System Usability Scale questionnaires (Brooke, 1996; interpretation after Bangor et al., 2009).
Input CSV: one row per participant, columns q1..q10 holding answers 1-5.   Usage: python sus_score.py responses.csv"""
import csv, statistics, sys
scores = []
for row in csv.DictReader(open(sys.argv[1])):
    a = [int(row["q%d" % i]) for i in range(1, 11)]
    scores.append(2.5 * (sum(x - 1 for x in a[0::2]) + sum(5 - x for x in a[1::2])))
print("participants:", len(scores))
print("mean SUS: %.1f   median: %.1f   min: %.1f   max: %.1f   sd: %.1f" % (
    statistics.mean(scores), statistics.median(scores), min(scores), max(scores), statistics.pstdev(scores)))
m = statistics.mean(scores)
print("adjective rating:", "Best imaginable" if m >= 90 else "Excellent" if m >= 80.3 else "Good" if m >= 68 else "OK/Marginal" if m >= 51 else "Poor")
