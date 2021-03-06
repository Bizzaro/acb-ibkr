import csv, sys
from datetime import datetime

DEBUG = False
IBKR_FILENAME = sys.argv[1]
TX_ARRAY = []

with open(IBKR_FILENAME, newline='') as ibkr_csv_file:
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
                print(f"{converted_date} {ticker} {action} {quantity} {proceeds/quantity} {fee} {currency}")
            price = proceeds/quantity
            TX_ARRAY.append([converted_date, "", ticker, action, quantity, price, fee, currency])
    ibkr_csv_file.close()

def takeFirst(elem):
    return elem[0]

TX_ARRAY.sort(key=takeFirst)
with open(f'TX_LOG_CLEANED.csv', 'w', newline='') as tx_output_file:
    tx_log_for_capgains = csv.writer(tx_output_file, delimiter=',')
    for x in range(len(TX_ARRAY)):
        tx_log_for_capgains.writerow(TX_ARRAY[x])
    tx_output_file.close()
