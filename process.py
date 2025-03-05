import pandas as pd
import sys


# Load the CSV file
file_path = "master.csv"  # Update with the path to your CSV file
df = pd.read_csv(file_path, names=["Date", "Type", "Symbol", "Action", "Quantity", "Price", "Fee", "Currency"], header=None, parse_dates=["Date"])

# Check if the user provided a year argument
if len(sys.argv) < 2:
    print("Usage: python capital_gains_acb.py <year>")
    sys.exit(1)

year = int(sys.argv[1])  # Convert year argument to integer

# Sort data by date for correct FIFO processing
df = df.sort_values(by="Date")

# Initialize data structures
capital_gains = []
cost_basis = {}

for index, row in df.iterrows():
    symbol = row["Symbol"]
    action = row["Action"]
    date = row["Date"]
    quantity = abs(row["Quantity"])  # Ensure quantity is positive
    total_cost = abs(row["Price"] * quantity)  # Exclude fee from purchase cost
    fee = abs(row["Fee"])  # Selling expenses (explicit cost to sell)

    if action == "BUY":
        if symbol not in cost_basis:
            cost_basis[symbol] = {"total_shares": 0, "total_cost": 0}
        
        # Update ACB (Adjusted Cost Base)
        cost_basis[symbol]["total_shares"] += quantity
        cost_basis[symbol]["total_cost"] += total_cost

    elif action == "SELL" and date.year == year:  # Filter by year
        if symbol in cost_basis and cost_basis[symbol]["total_shares"] > 0:
            # Calculate ACB per share
            acb_per_share = cost_basis[symbol]["total_cost"] / cost_basis[symbol]["total_shares"]

            # Calculate values
            proceeds = total_cost  # Total sale amount
            adjusted_cost = acb_per_share * quantity  # Cost basis for sold shares

            capital_gains.append([
                quantity,  # 1. Number of Shares
                symbol,    # 2. Name of Shares
                proceeds,  # 3. Proceeds
                adjusted_cost,  # 4. ACB
                fee  # 5. Expenses (actual cost to sell)
            ])

            # Update remaining shares and cost
            cost_basis[symbol]["total_shares"] -= quantity
            cost_basis[symbol]["total_cost"] -= adjusted_cost

# Convert to DataFrame without column names
capital_gains_df = pd.DataFrame(capital_gains)

# Save as CSV with no headers
output_file = f"formatted_capital_gains_{year}.csv"
capital_gains_df.to_csv(output_file, index=False, header=False)

print(f"Capital gains report for {year} saved as {output_file} (no headers).")
