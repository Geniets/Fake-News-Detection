import whois
from datetime import datetime

domains = ['youtube.com', 'www.youtube.com', 'google.com', 'facebook.com']

for domain in domains:
    print(f"\n{'='*60}")
    print(f"Testing: {domain}")
    print('='*60)
    
    try:
        info = whois.whois(domain)
        print(f"Success!")
        print(f"Creation Date: {info.creation_date}")
        print(f"Registrar: {info.registrar}")
        print(f"Emails: {info.emails}")
        
        if info.creation_date:
            creation = info.creation_date
            if isinstance(creation, list):
                creation = creation[0]
            
            if creation:
                age_days = (datetime.now() - creation).days
                age_years = round(age_days / 365.25, 1)
                print(f"Domain Age: {age_years} years")
            else:
                print("Creation date is None")
        else:
            print("No creation_date attribute")
            
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {str(e)[:200]}")
