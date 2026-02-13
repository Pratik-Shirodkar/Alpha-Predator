import os
import urllib.request
import json

def update_env():
    token = os.environ.get('DO_TOKEN')
    if not token:
        print("Error: DO_TOKEN not set")
        return

    # 1. Get App ID
    url = "https://api.digitalocean.com/v2/apps"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Content-Type', 'application/json')
    
    app_id = None
    spec = None
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            for app in data.get('apps', []):
                # Look for our app name
                if app.get('spec', {}).get('name') == 'zk-alpha-predator':
                    app_id = app.get('id')
                    spec = app.get('spec')
                    break
    except Exception as e:
        print(f"Error fetching apps: {e}")
        return

    if not app_id:
        print("Error: App 'zk-alpha-predator' not found")
        return

    print(f"Found App ID: {app_id}")

    # 2. Prepare new env var
    # We want to add/update VIRTUALS_API_KEY
    # We'll read it from .env
    new_key = None
    try:
        with open('backend/.env', 'r') as f:
            for line in f:
                if line.startswith('VIRTUALS_API_KEY='):
                    new_key = line.strip().split('=', 1)[1]
                    break
    except Exception as e:
        print(f"Error reading .env: {e}")
        return

    if not new_key:
        print("Error: VIRTUALS_API_KEY not found in backend/.env")
        return

    # 3. Update spec
    # Locate the service (should be 'backend')
    services = spec.get('services', [])
    updated = False
    for service in services:
        if service.get('name') == 'backend':
            envs = service.get('envs', [])
            # Check if key exists
            found = False
            for env in envs:
                if env.get('key') == 'VIRTUALS_API_KEY':
                    env['value'] = new_key
                    found = True
                    break
            if not found:
                envs.append({'key': 'VIRTUALS_API_KEY', 'value': new_key})
            
            service['envs'] = envs
            updated = True
            break
    
    if not updated:
        print("Error: 'backend' service not found in spec")
        return

    # 4. PUT update
    update_url = f"https://api.digitalocean.com/v2/apps/{app_id}"
    payload = {"spec": spec}
    data = json.dumps(payload).encode('utf-8')
    
    req = urllib.request.Request(update_url, data=data, method='PUT')
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print("SUCCESS: App updated with VIRTUALS_API_KEY")
            print(f"Live URL: {result.get('app', {}).get('live_url')}")
    except Exception as e:
        print(f"Error updating app: {e}")

if __name__ == "__main__":
    update_env()
