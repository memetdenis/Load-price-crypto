from decimal import Decimal


old = round(float('0.00000000000017'),14)
new = round(float(''),14)
changes = round(((new - old) / old) * 100, 2)
print(changes)