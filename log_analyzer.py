LEVELS = ("INFO", "WARNING", "ERROR")


def parse_log_line(line):
    parts = line.strip().split(maxsplit=2)

    if len(parts) != 3:
        return None

    timestamp, level, message = parts

    if level not in LEVELS:
        return None

    return {
        "timestamp": timestamp,
        "level": level,
        "message": message,
    }


def analyze_log(log_file):
    counts = {level: 0 for level in LEVELS}
    malformed_lines = 0

    with open(log_file, encoding="utf-8") as file:
        for line in file:
            entry = parse_log_line(line)

            if entry is None:
                malformed_lines += 1
                continue

            counts[entry["level"]] += 1

    return {
        "source": log_file,
        "counts": counts,
        "malformed_lines": malformed_lines,
    }


def print_summary(report):
    print("Log summary")

    for level in LEVELS:
        print(f"{level}: {report['counts'][level]}")

    print(f"Malformed lines: {report['malformed_lines']}")


report = analyze_log("sample.log")
print_summary(report)
