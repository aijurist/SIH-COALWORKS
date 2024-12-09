# config.py

# Reverse Scale for Consequence
CONSEQUENCE_SCALE = {
    "Several dead": 5,
    "One dead": 1,
    "Significant chance of fatality": 0.3,
    "One permanent disability or less chance of fatality": 0.1,
    "Many lost time injuries": 0.01,
    "One lost time injury": 0.001,
    "Small injury": 0.0001
}

# Reverse Scale for Exposure
EXPOSURE_SCALE = {
    "Continuous": 10,
    "Frequent (daily)": 5,
    "Seldom (weekly)": 3,
    "Unusual (monthly)": 2.5,
    "Occasional (yearly)": 2,
    "Once in 5 years": 1.5,
    "Once in 10 years": 0.5,
    "Once in 100 years": 0.02
}

# Reverse Scale for Probability
PROBABILITY_SCALE = {
    "May well be expected": 10,
    "Quite possible": 7,
    "Unusual but possible": 3,
    "Only remotely possible": 2,
    "Conceivable but unlikely": 1,
    "Practically impossible": 0.5,
    "Virtually impossible": 0.1
}
