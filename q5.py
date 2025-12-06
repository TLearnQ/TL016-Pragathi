def filter_logs(lines, out_file):
    with open(out_file, "a") as f:
        for line in lines:
            if "ERROR" in line or "WARN" in line:
                f.write(line.strip() + "\n")


