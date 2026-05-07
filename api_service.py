import requests
from datetime import datetime, timedelta

def get_currency_rates():
    
    url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
    try:
        response = requests.get(url)
        data = response.json()
        
        
        rates = {'UAH': 1.0} 
        for item in data:
            rates[item['cc']] = float(item['rate'])
        return rates
    except Exception as e:
        print(f"Помилка NBU API: {e}")
        return None

def get_history_7_days(currency_code):
    
    base_url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode={}&date={}&json"
    history = []
    
    for i in range(1, 8):
        
        date_obj = datetime.now() - timedelta(days=i)
        date_request = date_obj.strftime("%Y%m%d")
        date_display = date_obj.strftime("%d.%m.%Y")
        
        try:
            response = requests.get(base_url.format(currency_code, date_request))
            data = response.json()
            if data:
                rate = data[0]['rate']
                history.append(f"📅 {date_display}: {rate:.2f} UAH")
        except Exception as e:
            print(f"Помилка історії: {e}")
            
    return history