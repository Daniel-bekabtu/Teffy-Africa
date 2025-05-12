import json
from datetime import datetime
import time
import threading

DATA_FILES = {
    'users': 'users.json',
    'crops': 'crops.json',
    'land': 'land_data.json',
    'harvests': 'harvests.json',
    'alerts': 'alerts.json',
    'investments': 'investments.json',
    'listings': 'farm_listings.json'
}

CROP_SENSITIVITY = {
    "maize": {"min_temp": 10, "max_temp": 35, "max_wind": 30, "min_rain": 20, "max_rain": 150},
    "wheat": {"min_temp": 0, "max_temp": 30, "max_wind": 25, "min_rain": 15, "max_rain": 100},
    "tea": {"min_temp": 15, "max_temp": 30, "max_wind": 20, "min_rain": 50, "max_rain": 200},
    "coffee": {"min_temp": 15, "max_temp": 28, "max_wind": 25, "min_rain": 60, "max_rain": 250},
}

def load_data(file_key):
    """Load data from JSON file"""
    try:
        with open(DATA_FILES[file_key], 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(file_key, data):
    """Save data to JSON file"""
    with open(DATA_FILES[file_key], 'w') as file:
        json.dump(data, file, indent=4)

class USSDUser:
    def __init__(self, phone_number):
        self.phone_number = phone_number
        self.users = load_data('users')
        self.land_data = load_data('land')
        self.harvests = load_data('harvests')
        self.alerts = load_data('alerts')
        self.investments = load_data('investments')
        
        if phone_number not in self.users:
            self.register_user()
        else:
            self.current_state = self.users[phone_number].get('state', 'main_menu')
            self.role = self.users[phone_number]['role']
    
    def register_user(self):
        print("\nWelcome to FarmConnect!")
        print("1. Farmer")
        print("2. Investor")
        choice = input("Select your role (1-2): ")
        
        if choice == '1':
            self.users[self.phone_number] = {
                'role': 'farmer',
                'state': 'main_menu',
                'registration_date': datetime.now().strftime("%Y-%m-%d")
            }
            self.role = 'farmer'
        elif choice == '2':
            self.users[self.phone_number] = {
                'role': 'investor',
                'state': 'investor_menu',
                'registration_date': datetime.now().strftime("%Y-%m-%d"),
                'risk_profile': 'Moderate'
            }
            self.role = 'investor'
        else:
            print("Invalid choice. Please try again.")
            return self.register_user()
        
        save_data('users', self.users)
        self.current_state = self.users[self.phone_number]['state']
        print("\nRegistration successful!")
        self.show_menu()
    
    def show_menu(self):
        while True:
            if self.role == 'farmer':
                self.handle_farmer_states()
            elif self.role == 'investor':
                self.handle_investor_states()
            
            self.users[self.phone_number]['state'] = self.current_state
            save_data('users', self.users)
    
    def handle_farmer_states(self):
        if self.current_state == 'main_menu':
            unread_alerts = 0
            if self.phone_number in self.alerts:
                unread_alerts = len([a for a in self.alerts[self.phone_number] if not a.get('read', False)])
            
            print("\nFarmer Menu:")
            print("1. My Lands")
            print("2. Profile")
            print("3. Register New Land")
            print("4. Harvest Tracking")
            print(f"5. Weather Alerts ({unread_alerts} new)")
            
            choice = input("Select option (1-5): ")
            
            if choice == '1':
                if self.phone_number in self.land_data:
                    land = self.land_data[self.phone_number]
                    print("\nMy Land Info:")
                    print(f"Name: {land.get('farm_name', 'N/A')}")
                    print(f"Type: {land.get('farm_type', 'N/A')}")
                    print(f"Practice: {land.get('farming_practice', 'N/A')}")
                    print(f"Address: {land.get('farm_address', 'N/A')}")
                    print(f"Elevation: {land.get('elevation', 'N/A')}")
                    print(f"Revenue: {land.get('current_revenue', 'N/A')}")
                    print(f"Funding: {land.get('fund_amount', 'N/A')}")
                else:
                    print("\nYou don't have any registered land yet.")
                input("Press Enter to continue...")
            elif choice == '2':
                self.current_state = 'profile_menu'
            elif choice == '3':
                self.current_state = 'register_land'
            elif choice == '4':
                self.current_state = 'harvest_menu'
            elif choice == '5':
                self.current_state = 'weather_alerts'
            else:
                print("Invalid choice. Please try again.")
        
        elif self.current_state == 'weather_alerts':
            print("\nWeather Alerts:")
            print("1. View Alerts")
            print("2. Weather Forecast")
            print("3. Crop Advice")
            print("0. Back to main menu")
            
            choice = input("Select option (0-3): ")
            
            if choice == '0':
                self.current_state = 'main_menu'
            elif choice == '1':
                if self.phone_number in self.alerts and self.alerts[self.phone_number]:
                    for alert in self.alerts[self.phone_number]:
                        alert['read'] = True
                    save_data('alerts', self.alerts)
                    
                    print("\nLatest Alerts:")
                    for i, alert in enumerate(self.alerts[self.phone_number][-3:], 1):
                        crop = alert.get('crop', 'unknown')
                        first_msg = alert['alerts'][0] if alert['alerts'] else "No details"
                        print(f"{i}. {crop}: {first_msg[:30]}...")
                    
                    sub_choice = input("Select alert for details (1-3) or 0 to go back: ")
                    if sub_choice == '0':
                        pass
                    elif sub_choice.isdigit() and 1 <= int(sub_choice) <= 3:
                        alert_index = int(sub_choice) - 1
                        alert = self.alerts[self.phone_number][-3:][alert_index]
                        print("\nAlert Details:")
                        print(f"Crop: {alert.get('crop', 'unknown')}")
                        print(f"Time: {alert.get('timestamp', 'unknown')}")
                        print("Issues:")
                        for issue in alert.get('alerts', []):
                            print(f"- {issue}")
                        input("Press Enter to continue...")
                    else:
                        print("Invalid selection.")
                else:
                    print("\nNo weather alerts at this time.")
                    input("Press Enter to continue...")
            elif choice == '2':
                if self.phone_number in self.land_data and 'farm_address' in self.land_data[self.phone_number]:
                    print("\nWeather Forecast:")
                    print("Mon 09:00: 22°C, partly cloudy")
                    print("Mon 12:00: 26°C, sunny")
                    print("Mon 15:00: 24°C, light rain")
                    print("(Simulated forecast data)")
                else:
                    print("\nPlease register your farm address first.")
                input("Press Enter to continue...")
            elif choice == '3':
                self.current_state = 'crop_advice'
            else:
                print("Invalid choice. Please try again.")
        
        elif self.current_state == 'crop_advice':
            print("\nSelect crop for advice:")
            if self.phone_number in self.harvests:
                unique_crops = list(set(h['crop_type'] for h in self.harvests[self.phone_number]))
                for i, crop in enumerate(unique_crops[:5], 1):
                    print(f"{i}. {crop}")
                print("0. Back to weather menu")
                
                choice = input("Select crop (1-5) or 0 to go back: ")
                
                if choice == '0':
                    self.current_state = 'weather_alerts'
                elif choice.isdigit() and 1 <= int(choice) <= len(unique_crops):
                    selected_crop = unique_crops[int(choice)-1].lower()
                    print(f"\nCrop Advice for {selected_crop}:")
                    
                    if selected_crop in CROP_SENSITIVITY:
                        thresholds = CROP_SENSITIVITY[selected_crop]
                        print(f"- Ideal temperature range: {thresholds['min_temp']}°C to {thresholds['max_temp']}°C")
                        print(f"- Recommended rainfall: {thresholds['min_rain']}mm to {thresholds['max_rain']}mm")
                    
                    print("\nBest practices:")
                    print("- Ensure proper drainage")
                    print("- Monitor for pests regularly")
                    print("- Water in early morning")
                    input("Press Enter to continue...")
                else:
                    print("Invalid selection.")
            else:
                print("\nNo crops registered yet.")
                input("Press Enter to continue...")
                self.current_state = 'weather_alerts'
        
        elif self.current_state == 'register_land':
            print("\nLand Registration Process:")
            if 'farm_name' not in self.land_data.get(self.phone_number, {}):
                self.land_data[self.phone_number] = {}
                self.land_data[self.phone_number]['farm_name'] = input("Enter your farm's name: ")
                save_data('land', self.land_data)
            
            if 'farm_type' not in self.land_data.get(self.phone_number, {}):
                self.land_data[self.phone_number]['farm_type'] = input("What type of farm is this? (e.g., mixed, organic): ")
                save_data('land', self.land_data)
            
            if 'farming_practice' not in self.land_data.get(self.phone_number, {}):
                self.land_data[self.phone_number]['farming_practice'] = input("What farming practices do you use? (e.g., organic, conventional): ")
                save_data('land', self.land_data)
            
            if 'farm_address' not in self.land_data.get(self.phone_number, {}):
                self.land_data[self.phone_number]['farm_address'] = input("Please provide the farm's address: ")
                save_data('land', self.land_data)
            
            if 'elevation' not in self.land_data.get(self.phone_number, {}):
                self.land_data[self.phone_number]['elevation'] = input("What is the elevation of your farm? ")
                save_data('land', self.land_data)
            
            if 'access_roads' not in self.land_data.get(self.phone_number, {}):
                self.land_data[self.phone_number]['access_roads'] = input("Please describe the access roads to your farm: ")
                save_data('land', self.land_data)
            
            if 'collateral' not in self.land_data.get(self.phone_number, {}):
                self.land_data[self.phone_number]['collateral'] = input("What assets are pledged as collateral for your farm? ")
                save_data('land', self.land_data)
            
            if 'certifications' not in self.land_data.get(self.phone_number, {}):
                self.land_data[self.phone_number]['certifications'] = input("Provide links to any relevant certifications: ")
                save_data('land', self.land_data)
            
            if 'farm_images' not in self.land_data.get(self.phone_number, {}):
                self.land_data[self.phone_number]['farm_images'] = input("Provide links to images of your farm (e.g., aerial photos): ")
                save_data('land', self.land_data)
            
            if 'contact_email' not in self.land_data.get(self.phone_number, {}):
                self.land_data[self.phone_number]['contact_email'] = input("Please provide your contact email: ")
                save_data('land', self.land_data)
            
            if 'contact_phone' not in self.land_data.get(self.phone_number, {}):
                self.land_data[self.phone_number]['contact_phone'] = input("Please provide your contact phone number: ")
                save_data('land', self.land_data)
            
            if 'current_revenue' not in self.land_data.get(self.phone_number, {}):
                self.land_data[self.phone_number]['current_revenue'] = input("What is your farm's current revenue? ")
                save_data('land', self.land_data)
            
            if 'fund_amount' not in self.land_data.get(self.phone_number, {}):
                self.land_data[self.phone_number]['fund_amount'] = input("How much funding do you need for this farm? ")
                save_data('land', self.land_data)
                print("\nYour farm has been successfully registered!")
                self.current_state = 'main_menu'
    
    def handle_investor_states(self):
        if self.current_state == 'investor_menu':
            print("\nInvestor Dashboard:")
            print("1. Browse Farms")
            print("2. My Investments")
            print("3. Market Trends")
            print("4. Due Diligence Tools")
            print("5. Investor Profile")
            
            choice = input("Select option (1-5): ")
            
            if choice == '1':
                self.current_state = 'browse_farms'
            elif choice == '2':
                if self.phone_number in self.investments and self.investments[self.phone_number]:
                    self.current_state = 'view_investments'
                else:
                    print("\nYou have no active investments.")
                    input("Press Enter to continue...")
            elif choice == '3':
                self.current_state = 'market_trends'
            elif choice == '4':
                self.current_state = 'due_diligence'
            elif choice == '5':
                self.current_state = 'investor_profile'
            else:
                print("Invalid selection.")
        
        elif self.current_state == 'browse_farms':
            print("\nBrowse Farms:")
            print("1. By Location")
            print("2. By Crop Type")
            print("3. By ROI")
            print("0. Back to main menu")
            
            choice = input("Select option (0-3): ")
            
            if choice == '0':
                self.current_state = 'investor_menu'
            elif choice == '1':
                print("\nBrowse by Location:")
                print("1. Eastern")
                print("2. Western")
                print("3. Northern")
                print("4. Southern")
                loc_choice = input("Select region (1-4): ")
                regions = {1: "Eastern", 2: "Western", 3: "Northern", 4: "Southern"}
                if loc_choice in ['1', '2', '3', '4']:
                    print(f"\nShowing farms in {regions[int(loc_choice)]} region:")
                    print("1. Green Valley Farm - Coffee - 15% ROI")
                    print("2. Sunrise Fields - Tea - 12% ROI")
                    input("Press Enter to continue...")
                else:
                    print("Invalid selection.")
            elif choice == '2':
                print("\nBrowse by Crop Type:")
                print("1. Coffee")
                print("2. Tea")
                print("3. Maize")
                print("4. Wheat")
                crop_choice = input("Select crop (1-4): ")
                crops = {1: "Coffee", 2: "Tea", 3: "Maize", 4: "Wheat"}
                if crop_choice in ['1', '2', '3', '4']:
                    print(f"\nShowing farms growing {crops[int(crop_choice)]}:")
                    print("1. Mountain View Farm - 18% ROI")
                    print("2. Highland Estate - 14% ROI")
                    input("Press Enter to continue...")
                else:
                    print("Invalid selection.")
            elif choice == '3':
                print("\nTop ROI Farms:")
                print("1. Blue Sky Plantation - Coffee - 22% ROI")
                print("2. Golden Harvest - Tea - 19% ROI")
                print("3. Green Acres - Maize - 17% ROI")
                
                farm_choice = input("Select farm to view details (1-3) or 0 to go back: ")
                if farm_choice == '0':
                  pass
                elif farm_choice in ['1', '2', '3']:
                    farms = [
                        {
                            'farm_name': "Blue Sky Plantation",
                            'farm_type': "Coffee plantation",
                            'farm_address': "Western Highlands",
                            'projected_roi': "22",
                            'fund_amount': "50000"
                        },
                        {
                            'farm_name': "Golden Harvest",
                            'farm_type': "Tea estate",
                            'farm_address': "Eastern Plateau",
                            'projected_roi': "19",
                            'fund_amount': "35000"
                        },
                        {
                            'farm_name': "Green Acres",
                            'farm_type': "Mixed farm",
                            'farm_address': "Central Valley",
                            'projected_roi': "17",
                            'fund_amount': "40000"
                        }
                    ]
                    selected_farm = farms[int(farm_choice)-1]
                    
                    print("\nFarm Details:")
                    print(f"Name: {selected_farm['farm_name']}")
                    print(f"Type: {selected_farm['farm_type']}")
                    print(f"Location: {selected_farm['farm_address']}")
                    print(f"Projected ROI: {selected_farm['projected_roi']}%")
                    print(f"Seeking: ${selected_farm['fund_amount']}")
                    
                    invest_choice = input("Would you like to invest in this farm? (y/n): ")
                    if invest_choice.lower() == 'y':
                        amount = input("Enter amount to invest: $")
                        if amount.isdigit():
                            if self.phone_number not in self.investments:
                                self.investments[self.phone_number] = []
                            
                            self.investments[self.phone_number].append({
                                "farm_id": "simulated_"+farm_choice,
                                "farm_name": selected_farm['farm_name'],
                                "amount": float(amount),
                                "date": datetime.now().strftime("%Y-%m-%d"),
                                "status": "active",
                                "expected_roi": selected_farm['projected_roi']
                            })
                            save_data('investments', self.investments)
                            
                            print(f"\nSuccessfully invested ${amount} in {selected_farm['farm_name']}!")
                            input("Press Enter to continue...")
                        else:
                            print("Invalid amount. Please enter numbers only.")
                    else:
                        print("Investment cancelled.")
                else:
                    print("Invalid selection.")
        
        elif self.current_state == 'market_trends':
            print("\nMarket Trends:")
            print("1. Crop Prices")
            print("2. Weather Impact")
            print("3. Demand Forecast")
            print("0. Back to main menu")
            
            choice = input("Select option (0-3): ")
            
            if choice == '0':
                self.current_state = 'investor_menu'
            elif choice == '1':
                print("\nCurrent Crop Prices:")
                print("Coffee: $2.50/kg")
                print("Tea: $1.80/kg")
                print("Maize: $0.30/kg")
                print("Wheat: $0.35/kg")
                input("Press Enter to continue...")
            elif choice == '2':
                print("\nWeather Impact:")
                print("Heavy rains expected in Western regions")
                print("may affect tea harvests next quarter")
                input("Press Enter to continue...")
            elif choice == '3':
                print("\nDemand Forecast:")
                print("Coffee: ↑12%")
                print("Tea: ↑5%")
                print("Maize: ↓3%")
                print("Wheat: ↔")
                input("Press Enter to continue...")
            else:
                print("Invalid selection.")
        
        elif self.current_state == 'investor_profile':
            profile = self.users.get(self.phone_number, {})
            print("\nInvestor Profile:")
            print(f"Name: {profile.get('name', 'N/A')}")
            print(f"Risk Appetite: {profile.get('risk_profile', 'Medium')}")
            
            total_invested = sum(inv.get('amount', 0) for inv in self.investments.get(self.phone_number, []))
            print(f"Total Invested: ${total_invested}")
            
            print("\n1. Update Risk Profile")
            print("2. View Investment History")
            print("0. Back to main menu")
            
            choice = input("Select option (0-2): ")
            
            if choice == '0':
                self.current_state = 'investor_menu'
            elif choice == '1':
                print("\nUpdate Risk Profile:")
                print("1. Conservative")
                print("2. Moderate")
                print("3. Aggressive")
                risk_choice = input("Select your risk profile (1-3): ")
                
                risk_levels = {"1": "Conservative", "2": "Moderate", "3": "Aggressive"}
                if risk_choice in risk_levels:
                    self.users[self.phone_number]["risk_profile"] = risk_levels[risk_choice]
                    save_data('users', self.users)
                    print(f"\nRisk profile updated to {risk_levels[risk_choice]}")
                    input("Press Enter to continue...")
                else:
                    print("Invalid selection.")
            elif choice == '2':
                if self.phone_number in self.investments:
                    print("\nInvestment History:")
                    for inv in self.investments[self.phone_number][-3:]:
                        print(f"{inv.get('date')}: ${inv.get('amount')} in {inv.get('farm_name')}")
                    input("Press Enter to continue...")
                else:
                    print("\nNo investment history.")
                    input("Press Enter to continue...")
            else:
                print("Invalid selection.")

def simulate_weather_alerts():
    """Background thread to simulate weather alerts"""
    while True:
        time.sleep(30)
        
        land_data = load_data('land')
        alerts = load_data('alerts')
        
        for phone, land in land_data.items():
            if phone not in alerts:
                alerts[phone] = []
            
            if 'farm_address' in land and 'Western' in land['farm_address']:
                alerts[phone].append({
                    'crop': 'coffee',
                    'alerts': ["Heavy rain warning: 120mm expected in next 24 hours"],
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'read': False
                })
            elif 'farm_address' in land and 'Eastern' in land['farm_address']:
                alerts[phone].append({
                    'crop': 'tea',
                    'alerts': ["Drought warning: Only 10mm rain in last month"],
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'read': False
                })
        
        save_data('alerts', alerts)

if __name__ == '__main__':
    weather_thread = threading.Thread(target=simulate_weather_alerts, daemon=True)
    weather_thread.start()
    
    print("FarmConnect USSD Simulator")
    print("-------------------------")
    
    phone_number = input("Enter your phone number (for testing): ")
    
    user = USSDUser(phone_number)
    user.show_menu()