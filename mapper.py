import sys
for line in sys.stdin:
    parts = line.strip().split(',')
    if len(parts) == 2:
        print("{}\t{}".format(parts[0], parts[1]))
