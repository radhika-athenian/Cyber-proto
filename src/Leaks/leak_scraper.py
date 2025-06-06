import os
import re
import json
import time
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from datetime import datetime
from urllib.parse import urljoin

BASE_URL = "https://paste.ee"
LATEST_PASTES_URL = "https://paste.ee/latest"
DATA_DIR = "data"
TEST_SAMPLE_DIR = "leaks/test_samples"
OUTPUT_FILE = os.path.join(DATA_DIR, "leaks.json")

def can_scrape(url):
    rp = RobotFileParser()
    rp.set_url(urljoin(url, "/robots.txt"))
    rp.read()
    return rp.can_fetch("*", url)

def extract_paste_links(html):
    soup = BeautifulSoup(html, "html.parser")
    return list(set(
        urljoin(BASE_URL, a['href']) for a in soup.find_all("a", href=True) if "/p/" in a['href']
    ))[:10]

def fetch_paste_content(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            pre = soup.find("pre")
            return pre.text if pre else ""
    except Exception as e:
        print(f"[!] Error fetching {url}: {e}")
    return ""

def extract_leaks(text, domain, source="unknown"):
    leaks = []
    for line in text.splitlines():
        if domain in line:
            leaks.append({
                "content": line.strip(),
                "timestamp": datetime.now().isoformat(),
                "type": classify_leak(line),
                "source": source
            })
    return leaks

def classify_leak(line):
    if re.search(r"(password|pwd)[=: ]", line, re.IGNORECASE):
        return "credentials"
    elif re.search(r"(key|token|secret)[=: ]", line, re.IGNORECASE):
        return "api_key"
    elif re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", line):
        return "email"
    return "unknown"

def scrape_online(domain):
    if not can_scrape(LATEST_PASTES_URL):
        print("[!] robots.txt blocks scraping")
        return []

    print("[*] Scraping latest online pastes...")
    res = requests.get(LATEST_PASTES_URL)
    paste_links = extract_paste_links(res.text)
    leaks = []

    for link in paste_links:
        print(f"[>] Fetching: {link}")
        content = fetch_paste_content(link)
        leaks += extract_leaks(content, domain, source=link)
        time.sleep(1)

    return leaks

def process_offline_samples(domain):
    print("[*] Processing local test samples...")
    leaks = []

    for fname in os.listdir(TEST_SAMPLE_DIR):
        path = os.path.join(TEST_SAMPLE_DIR, fname)
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                leaks += extract_leaks(content, domain, source=fname)

    return leaks

def save_to_json(data, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[✓] Saved {len(data)} leaks to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Leak scraper tool")
    parser.add_argument("--domain", required=True, help="Target domain to search for")
    parser.add_argument("--mode", choices=["online", "offline"], default="online",
                        help="Run mode: 'online' for web scraping, 'offline' to parse local test samples")
    args = parser.parse_args()

    target_domain = args.domain.lower().strip()
    mode = args.mode

    if mode == "online":
        leaks = scrape_online(target_domain)
    else:
        leaks = process_offline_samples(target_domain)

    if leaks:
        save_to_json(leaks, OUTPUT_FILE)
    else:
        print(f"[!] No leaks found in {mode} mode for {target_domain}")
