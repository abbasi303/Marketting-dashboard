import csv
import random
import datetime
from pathlib import Path

# Configuration
NUM_USERS = 1000
START_DATE = datetime.datetime(2025, 1, 1)
END_DATE = datetime.datetime(2025, 3, 31)
CAMPAIGNS = ["SpringSale", "BrandPush", "Retarget", "SummerPromo", "BlackFriday"]
CHANNELS = ["Email", "Social", "Ads", "Organic", "Partner"]

# Conversion rates (adjust as needed)
SIGNUP_RATE = 0.7  # 70% of views convert to signups
PURCHASE_RATE = 0.3  # 30% of signups convert to purchases

# Campaign costs
COSTS = {
    "SpringSale": {"Email": {"cpc": 0.50, "cpm": 10.00}, 
                  "Social": {"cpc": 0.75, "cpm": 15.00},
                  "Ads": {"cpc": 1.20, "cpm": 25.00},
                  "Organic": {"cpc": 0.00, "cpm": 0.00},
                  "Partner": {"cpc": 0.90, "cpm": 18.00}},
    "BrandPush": {"Email": {"cpc": 0.45, "cpm": 8.00},
                 "Social": {"cpc": 0.65, "cpm": 12.00},
                 "Ads": {"cpc": 1.00, "cpm": 20.00},
                 "Organic": {"cpc": 0.00, "cpm": 0.00},
                 "Partner": {"cpc": 0.80, "cpm": 16.00}},
    "Retarget": {"Email": {"cpc": 0.30, "cpm": 5.00},
                "Social": {"cpc": 0.40, "cpm": 7.00},
                "Ads": {"cpc": 0.80, "cpm": 15.00},
                "Organic": {"cpc": 0.00, "cpm": 0.00},
                "Partner": {"cpc": 0.60, "cpm": 12.00}},
    "SummerPromo": {"Email": {"cpc": 0.55, "cpm": 11.00},
                   "Social": {"cpc": 0.80, "cpm": 16.00},
                   "Ads": {"cpc": 1.30, "cpm": 26.00},
                   "Organic": {"cpc": 0.00, "cpm": 0.00},
                   "Partner": {"cpc": 0.95, "cpm": 19.00}},
    "BlackFriday": {"Email": {"cpc": 0.60, "cpm": 12.00},
                   "Social": {"cpc": 0.90, "cpm": 18.00},
                   "Ads": {"cpc": 1.50, "cpm": 30.00},
                   "Organic": {"cpc": 0.00, "cpm": 0.00},
                   "Partner": {"cpc": 1.00, "cpm": 20.00}}
}


def random_date(start, end):
    """Generate a random datetime between start and end"""
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + datetime.timedelta(seconds=random_second)


def generate_events():
    """Generate marketing event data"""
    events = []
    
    for user_id in range(1, NUM_USERS + 1):
        # Randomly select campaign and channel
        campaign = random.choice(CAMPAIGNS)
        channel = random.choice(CHANNELS)
        
        # Generate view event
        view_date = random_date(START_DATE, END_DATE)
        events.append({
            "user_id": user_id,
            "event_type": "page_view",
            "campaign": campaign,
            "channel": channel,
            "timestamp": view_date.isoformat()
        })
        
        # Generate signup event (with probability)
        if random.random() < SIGNUP_RATE:
            # Signup happens within minutes of view
            signup_date = view_date + datetime.timedelta(minutes=random.randint(1, 15))
            events.append({
                "user_id": user_id,
                "event_type": "signup",
                "campaign": campaign,
                "channel": channel,
                "timestamp": signup_date.isoformat()
            })
            
            # Generate purchase event (with probability)
            if random.random() < PURCHASE_RATE:
                # Purchase happens within hours of signup
                purchase_date = signup_date + datetime.timedelta(hours=random.randint(1, 48))
                events.append({
                    "user_id": user_id,
                    "event_type": "purchase",
                    "campaign": campaign,
                    "channel": channel,
                    "timestamp": purchase_date.isoformat()
                })
    
    return events


def generate_costs():
    """Generate campaign cost data"""
    costs = []
    
    for campaign in CAMPAIGNS:
        for channel in CHANNELS:
            costs.append({
                "campaign": campaign,
                "channel": channel,
                "cpc": COSTS[campaign][channel]["cpc"],
                "cpm": COSTS[campaign][channel]["cpm"]
            })
    
    return costs


def write_csv(data, filename):
    """Write data to CSV file"""
    if not data:
        return
    
    file_path = Path("../data") / filename
    
    with open(file_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Generated {len(data)} rows in {file_path}")


def main():
    """Main function"""
    print("Generating marketing event data...")
    events = generate_events()
    write_csv(events, "generated_events.csv")
    
    print("Generating campaign cost data...")
    costs = generate_costs()
    write_csv(costs, "generated_costs.csv")
    
    print("Done!")


if __name__ == "__main__":
    main()
