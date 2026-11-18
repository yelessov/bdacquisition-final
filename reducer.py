import sys
current_symbol = None
total_qty = 0.0

for line in sys.stdin:
    try:
        symbol, qty = line.strip().split('\t')
        qty = float(qty)
    except ValueError:
        continue
        
    if current_symbol == symbol:
        total_qty += qty
    else:
        if current_symbol:
            print("{}\t{}".format(current_symbol, round(total_qty, 2)))
        current_symbol = symbol
        total_qty = qty
        
if current_symbol:
    print("{}\t{}".format(current_symbol, round(total_qty, 2)))
