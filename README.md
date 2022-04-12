# IBKR

Parses annual activity statement in `.csv` from IBKR, automatically calculates correct ACB for Schedule 3.

## Why?
T5008 is inaccurate even using a single broker. Fractional shares are not included in calculations, exchange rates are also not BoC rates. This is common knowledge amongst CPAs and also the CRA itself.

## How to use
Sign in to client portal, then go 
`Reports > Statements > Activity > Period: Annual > Format: CSV > Run`

For use with https://github.com/Bizzaro/cad-capital-gains.
![](2022-04-11-22-28-54.png)

1. Create virtual env 
```
python3 -m venv virtual-env 
source virtual-env/bin/activate
```

2. Install deps 
```
pip3 install -r requirements.txt
```

3. Generate a compatible `cad-capital-gains` compatible `.csv.`
```
python3 ibkr.py <CSV NAME>
```

4. Run the `capgains` (cad-capital-gains) tool
```
capgains calc eggs.csv 2021`
```

### DISCLAIMER
YOU (THE USER OF THIS SCRIPT) ARE RESPONSIBLE FOR THE NUMBERS PRODUCED BY THIS TOOL. IT HAS NOT BEEN AUDITED OR VERIFIED BY A THIRD PARTY. THIS IS NOT TAX ADVICE OR CERTIFIED TAX SOFTWARE. DOING RANDOM SPOT CHECKS OF CALCULATIONS IS RECOMMENDED. CONSULT A CPA FOR ALL YOUR TAX INQUIRIES.
