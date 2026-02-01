import requests, json

def fetch_demo():
    # Use a reliable public JSON endpoint for demo purposes
    # This returns a simple object we can treat as "KPIs"
    url = "https://jsonplaceholder.typicode.com/todos/1"
    resp = requests.get(url)
    data = resp.json()
    # Map fields to fake KPI names for illustration
    sessions = data.get('id', 0) * 1000  # just a placeholder calculation
    users = data.get('userId', 0) * 500
    bounce_rate = 0.25  # static example
    return sessions, users, bounce_rate

if __name__ == "__main__":
    s, u, br = fetch_demo()
    print(f"Demo KPI → Sessions: {s:,}, Users: {u:,}, Bounce Rate: {br:.1%}")
