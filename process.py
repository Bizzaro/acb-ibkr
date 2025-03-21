import pandas as pd
import sys
import requests
from datetime import timedelta

def get_bank_of_canada_fx_rate(date, currency):
    """
    Fetch the Bank of Canada FX rate for a given date and currency.
    Args:
        date (datetime.date): The date for which to fetch the FX rate.
        currency (str): The currency code (e.g., "USD").
    Returns:
        float: The FX rate for the given date and currency, or None if not available.
    """
    # Format the date to YYYY-MM-DD
    formatted_date = date.strftime("%Y-%m-%d")
    
    # Example API endpoint for Bank of Canada FX rates
    api_url = f"https://www.bankofcanada.ca/valet/observations/FX{currency}CAD/json?start_date={formatted_date}&end_date={formatted_date}"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        # Extract the FX rate from the response
        observations = data.get("observations", [])
        if observations:
            fx_rate = float(observations[0][f"FX{currency}CAD"]["v"])
            return fx_rate
        else:
            return None
    except Exception as e:
        print(f"Error fetching FX rate for {currency} on {formatted_date}: {e}")
        return None

# Load the CSV file
file_path = "master.csv"  # Update with the path to your CSV file
df = pd.read_csv(file_path, names=["Date", "Type", "Symbol", "Action", "Quantity", "Price", "Fee", "Currency"], header=None, parse_dates=["Date"])

# Check if the user provided a year argument
if len(sys.argv) < 2:
    print("Usage: python capital_gains_acb.py <year>")
    sys.exit(1)

year = int(sys.argv[1])  # Convert year argument to integer

# Filter the DataFrame to include only transactions up to the specified year
df = df[df["Date"].dt.year <= year]

# Sort data by date for correct FIFO processing
df = df.sort_values(by="Date")

# Initialize data structures
capital_gains = []
cost_basis = {}
buy_transactions = []  # Track all BUY transactions for superficial loss rules

for index, row in df.iterrows():
    symbol = row["Symbol"]
    action = row["Action"]
    date = row["Date"]
    quantity = abs(row["Quantity"])  # Ensure quantity is positive
    total_cost = abs(row["Price"] * quantity)  # Exclude fee from purchase cost
    fee = abs(row["Fee"])  # Selling expenses (explicit cost to sell)

    if action == "BUY":
        if symbol not in cost_basis:
            cost_basis[symbol] = {"total_shares": 0, "total_cost": 0, "currency": "CAD"}  # Default to CAD

        # If the currency is not CAD, convert it to CAD
        if row["Currency"] != "CAD":
            fx_rate = get_bank_of_canada_fx_rate(date, row["Currency"])
            if fx_rate is None:
                raise ValueError(f"FX rate not available for {row['Currency']} on {date}")
            total_cost_cad = total_cost * fx_rate
        else:
            total_cost_cad = total_cost

        # Update cost basis
        cost_basis[symbol]["total_shares"] += quantity
        cost_basis[symbol]["total_cost"] += total_cost_cad

        # Track the BUY transaction
        buy_transactions.append({"symbol": symbol, "date": date, "quantity": quantity, "total_cost": total_cost_cad})

    elif action == "SELL" and date.year == year:
        if symbol in cost_basis and cost_basis[symbol]["total_shares"] > 0:
            acb_per_share = cost_basis[symbol]["total_cost"] / cost_basis[symbol]["total_shares"]

            # Calculate proceeds
            if row["Currency"] != "CAD":
                fx_rate = get_bank_of_canada_fx_rate(date, row["Currency"])
                if fx_rate is None:
                    raise ValueError(f"FX rate not available for {row['Currency']} on {date}")
                proceeds = total_cost * fx_rate
            else:
                proceeds = total_cost

            adjusted_cost = acb_per_share * quantity
            gain_or_loss = proceeds - adjusted_cost - fee

            # Check for superficial loss
            if gain_or_loss < 0:  # Loss occurred
                # Check for BUY transactions within 30 days before or after the SELL date
                superficial_loss = False
                for buy in buy_transactions:
                    if (
                        buy["symbol"] == symbol and
                        abs((buy["date"] - date).days) <= 30
                    ):
                        # Ensure repurchased shares exist after the sale
                        remaining_shares = cost_basis[symbol]["total_shares"] - quantity
                        if remaining_shares > 0:
                            superficial_loss = True
                            disallowed_loss = abs(gain_or_loss)
                            # Add the disallowed loss to the ACB of the repurchased shares
                            cost_basis[symbol]["total_cost"] += disallowed_loss

                            # Log the details of the superficial loss calculation
                            print(
                                f"Superficial loss detected for {symbol} on {date}.\n"
                                f"  - Quantity Sold: {quantity}\n"
                                f"  - Sale Proceeds: {round(proceeds, 2)}\n"
                                f"  - Adjusted Cost: {round(adjusted_cost, 2)}\n"
                                f"  - Loss: {round(gain_or_loss, 2)}\n"
                                f"  - Repurchase Date: {buy['date']}\n"
                                f"  - Repurchase Quantity: {buy['quantity']}\n"
                                f"  - Disallowed Loss: {round(disallowed_loss, 2)}\n"
                                f"  - New ACB: {round(cost_basis[symbol]['total_cost'], 2)}"
                            )
                            break

                if superficial_loss:
                    gain_or_loss = 0  # Disallowed loss

            # Append the transaction to capital gains
            capital_gains.append([
                round(quantity, 2),
                symbol,
                round(proceeds, 2),
                round(adjusted_cost, 2),
                round(fee, 2),
                round(gain_or_loss, 2),
                "CAD"
            ])

            # Update remaining shares and cost basis
            cost_basis[symbol]["total_shares"] -= quantity
            cost_basis[symbol]["total_cost"] -= adjusted_cost

# Convert to DataFrame without column names
capital_gains_df = pd.DataFrame(capital_gains)

# Save as CSV with no headers
output_file = f"formatted_capital_gains_{year}.csv"
capital_gains_df.to_csv(output_file, index=False, header=False)

print(f"Capital gains report for {year} saved as {output_file} (no headers).")
