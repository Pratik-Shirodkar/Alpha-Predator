import os
import json
import yaml
import urllib.request
import urllib.error

def deploy():
    # 1. Load .env
    env_vars = {}
    try:
        with open('backend/.env', 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    k, v = line.strip().split('=', 1)
                    env_vars[k] = v.strip('"\'')
    except Exception as e:
        print(f"Error loading .env: {e}")
        return

    # 2. Load app.yaml
    try:
        with open('app.yaml', 'r') as f:
            spec = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading app.yaml: {e}")
        return

    # 3. Inject secrets
    # The spec has 'envs' list with 'key' and 'value'
    if 'services' in spec:
        for service in spec['services']:
            if 'envs' in service:
                for env_item in service['envs']:
                    val = env_item.get('value', '')
                    if val.startswith('${') and val.endswith('}'):
                        var_name = val[2:-1]
                        if var_name in env_vars:
                            env_item['value'] = env_vars[var_name]
                        else:
                            print(f"Warning: {var_name} not found in .env")

    # 4. Prepare API payload
    payload = {"spec": spec}
    data = json.dumps(payload).encode('utf-8')

    # 5. Send request
    token = os.environ.get('DO_TOKEN')
    if not token:
        print("Error: DO_TOKEN env var not set")
        return

    url = "https://api.digitalocean.com/v2/apps"
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', f'Bearer {token}')

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            app_id = result.get('app', {}).get('id')
            live_url = result.get('app', {}).get('live_url')
            print(f"SUCCESS: App created! ID: {app_id}")
            print(f"Live URL (pending build): {live_url}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    deploy()
