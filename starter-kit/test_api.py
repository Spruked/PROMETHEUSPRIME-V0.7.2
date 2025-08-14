import requests

BASE_URL = "http://localhost:5000"

def test_health():
    r = requests.get(f"{BASE_URL}/", timeout=10)
    print("/ =>", r.status_code, r.text)

def test_prompt():
    payload = {"title": "Test", "description": "Demo"}
    r = requests.post(f"{BASE_URL}/prompt", json=payload, timeout=10)
    print("/prompt =>", r.status_code, r.json())

def test_vault_files():
    r = requests.get(f"{BASE_URL}/vault-files", timeout=10)
    print("/vault-files =>", r.status_code, r.json())

def test_helix():
    payload = {"input": "Reflect on the nature of truth."}
    r = requests.post(f"{BASE_URL}/helix/process", json=payload, timeout=10)
    print("/helix/process =>", r.status_code, r.json())

def test_reflect():
    payload = {"input": "Mirror this phrase."}
    r = requests.post(f"{BASE_URL}/api/reflect", json=payload, timeout=10)
    print("/api/reflect =>", r.status_code, r.json())

if __name__ == "__main__":
    test_health()
    test_prompt()
    test_vault_files()
    test_helix()
    test_reflect()
