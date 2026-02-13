import os
import urllib.request
import json

def get_latest_app():
    token = os.environ.get('DO_TOKEN')
    if not token:
        print("Error: DO_TOKEN not set")
        return

    url = "https://api.digitalocean.com/v2/apps"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Content-Type', 'application/json')

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            apps = data.get('apps', [])
            
            if not apps:
                print("No apps found.")
                return

            # Sort by updated_at desc to get the one we just touched
            # Assuming ISO 8601 format strings sort lexically correctly for recent dates
            apps.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            
            latest = apps[0]
            live_url = latest.get('live_url')
            # If live_url is None, try constructing it from default domain
            if not live_url:
                domains = latest.get('domains', [])
                if domains:
                 live_url = f"https://{domains[0]}"
            
            print(f"App: {latest.get('spec', {}).get('name')}")
            print(f"ID: {latest.get('id')}")
            print(f"Status: {latest.get('phase')}")
            print(f"Live URL: {live_url}")
            
    except Exception as e:
        print(f"Error fetching apps: {e}")

if __name__ == "__main__":
    get_latest_app()
