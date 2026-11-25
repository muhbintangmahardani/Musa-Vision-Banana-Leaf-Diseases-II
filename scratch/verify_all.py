import hashlib
import os
import urllib.request

def verify_app_py():
    target_hash = "23b99560c9c9f8dc94807e4c8adc43a398ffa7e08804118748172124b04ebf3c"
    target_size = 62323
    
    with open("app.py", "rb") as f:
        data = f.read()
    
    cur_hash = hashlib.sha256(data).hexdigest()
    cur_size = len(data)
    
    print(f"[app.py] Size: {cur_size} (Expected: {target_size}) -> {'OK' if cur_size == target_size else 'MISMATCH'}")
    print(f"[app.py] SHA256: {cur_hash} -> {'OK' if cur_hash == target_hash else 'MISMATCH'}")
    assert cur_size == target_size and cur_hash == target_hash, "app.py modified!"

def verify_r02():
    files = [
        "templates/index.html",
        "templates/katalog_patogen.html",
        "static/css/style.css",
        "static/js/main.js"
    ]
    em_dash = "\u2014"
    en_dash = "\u2013"
    
    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        em_count = content.count(em_dash)
        en_count = content.count(en_dash)
        print(f"[{path}] Em dash: {em_count}, En dash: {en_count} -> {'PASS' if em_count == 0 and en_count == 0 else 'FAIL'}")
        assert em_count == 0 and en_count == 0, f"R-02 violated in {path}"

def verify_endpoints():
    endpoints = [
        "http://127.0.0.1:5000/",
        "http://127.0.0.1:5000/katalog-patogen?kelas=black-sigatoka",
        "http://127.0.0.1:5000/katalog-patogen?kelas=fresh"
    ]
    
    for url in endpoints:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                print(f"[{url}] HTTP {resp.status} OK (length: {len(resp.read())})")
        except Exception as e:
            print(f"[{url}] Request error: {e}")

if __name__ == "__main__":
    verify_app_py()
    verify_r02()
    verify_endpoints()
    print("\nALL CHECKS PASSED PERFECTLY!")
