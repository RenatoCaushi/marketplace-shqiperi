import requests
import pandas as pd

def fetch_jobs():
    url = "https://remoteok.com/api"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            
            jobs_list = []
            for job in data[1:]:
                title = job.get('position')
                company = job.get('company')
                location = job.get('location', 'Remote')
                tags = job.get('tags', [])
                url_link = job.get('url')
                date = job.get('date')
                
                if title and company:
                    jobs_list.append({
                        "Title": title,
                        "Company": company,
                        "Location": location,
                        "Tags": ", ".join(tags) if isinstance(tags, list) else tags,
                        "URL": url_link,
                        "Date": date
                    })
            
            df = pd.DataFrame(jobs_list)
            return df
        else:
            print("Gabim gjatë marrjes së të dhënave.")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Ndodhi një gabim: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    df_jobs = fetch_jobs()
    print(f"U mblodhën {len(df_jobs)} oferta pune me sukses!")
    print(df_jobs.head())