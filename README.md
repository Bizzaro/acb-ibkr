# IBKR
Parses annual activity statement in `.csv` from IBKR, manually calculates ACB for Schedule 3. T5008 is inaccurate even using a single broker. Fractional shares are not included in calculations, exchange rates are also not BoC rates.

Sign in to client portal, then go 
`Reports > Statements > Activity > Period: Annual > Format: CSV > Run`

For use with https://github.com/Bizzaro/cad-capital-gains.

1. Create virtual env 
```
python3 -m venv virtual-env 
source virtual-env/bin/activate
```

2. Clone the cad-capital-gains repo or install from git repo into pip 
```
pip3 install <PATH TO cad-capital-gains>

or 

pip3 install git+https://github.com/Bizzaro/cad-capital-gains.git
```
3. `python3 ibkr.py <CSV NAME>`

4. `capgains calc eggs.csv 2021`
