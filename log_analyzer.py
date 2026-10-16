LEVELS = ("INFO", "WARNING", "ERROR")
counts = {level: 0 for level in LEVELS}

with open("sample.log", encoding="utf-8") as log_file:
    for line in log_file:
        timestamp, level, message = line.strip().split(maxsplit=2)
        counts[level] += 1

for level in LEVELS:
    print(f"{level}: {counts[level]}")
