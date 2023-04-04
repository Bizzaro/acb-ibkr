import csv, sys
import os
from datetime import datetime

DEBUG = False
TX_ARRAY = []

IBKR_CSV_FILES_IN_SOURCE = os.listdir("./source")

for filename in IBKR_CSV_FILES_IN_SOURCE:
    with open(f"source/{filename}", newline='') as ibkr_csv_file:
        ibkr_csv_data = csv.reader(ibkr_csv_file, delimiter=',', quotechar='\"')
        for row in ibkr_csv_data:
            if (row[0] == 'Trades' and row[1] == 'Header' and DEBUG):
                print(row)

            if (row[0] == 'Trades' and row[1] == 'Data' and row[3] != 'Forex'):
                instrument = row[3]
                currency = row[4]
                ticker = row[5]
                date = row[6]
                quantity = float(row[7])
                proceeds = float(row[10])
                fee = float(row[11])
                basis_includes_fee = float(row[12])
                converted_date = datetime.strptime(date, '%Y-%m-%d, %H:%M:%S').date()
            
                if (quantity > 0):
                    action = "BUY"
                elif (quantity < 0):
                    action = "SELL"
                
                if (DEBUG):
                    print(f"{converted_date} {instrument} {ticker} {action} {quantity} {proceeds/quantity} {fee} {currency}")
                price = proceeds/quantity
                TX_ARRAY.append([converted_date, instrument, ticker, action, quantity, price, fee, currency])

def takeFirst(elem):
    return elem[0]

TX_ARRAY.sort(key=takeFirst)

with open(f'master.csv', 'w', newline='') as tx_output_file:
    tx_log_for_capgains = csv.writer(tx_output_file, delimiter=',')
    tx_log_for_capgains.writerows(TX_ARRAY)
