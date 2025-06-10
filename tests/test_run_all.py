import sys
import types

# Create dummy modules so scanner imports succeed without heavy dependencies
sys.modules.setdefault("nmap", types.ModuleType("nmap"))
dateutil = types.ModuleType("dateutil")
parser = types.ModuleType("parser")
parser.parse = lambda x: x
dateutil.parser = parser
sys.modules.setdefault("dateutil", dateutil)
sys.modules.setdefault("pytz", types.ModuleType("pytz"))
sys.modules.setdefault("requests", types.ModuleType("requests"))
wap_module = types.ModuleType("Wappalyzer")
class DummyWappalyzer:
    @staticmethod
    def latest():
        return DummyWappalyzer()
    def analyze(self, page):
        return []

class DummyWebPage:
    @staticmethod
    def new_from_response(response):
        return DummyWebPage()

wap_module.Wappalyzer = DummyWappalyzer
wap_module.WebPage = DummyWebPage
sys.modules.setdefault("Wappalyzer", wap_module)

from src.Scanners import run_scanners


def test_run_all_returns_expected_keys(monkeypatch):
    # Patch scanner functions to avoid heavy operations
    monkeypatch.setattr(run_scanners, "run_sublist3r", lambda domain: ["a." + domain])
    monkeypatch.setattr(run_scanners, "resolve_subdomains", lambda subs: [{"subdomain": subs[0], "ip": "1.1.1.1"}])
    monkeypatch.setattr(run_scanners, "scan_ports", lambda assets, ports="1-100": [
        {"subdomain": assets[0]["subdomain"], "ports": []}
    ])
    monkeypatch.setattr(run_scanners, "scan_ssl", lambda assets: [
        {"subdomain": assets[0]["subdomain"], "ssl": True}
    ])
    monkeypatch.setattr(run_scanners, "detect_technologies", lambda doms, workers=1: [
        {"subdomain": doms[0], "technologies": []}
    ])

    saved = {}

    def fake_save(domain, prefix, data):
        saved[prefix] = data
        return f"{prefix}.json"

    monkeypatch.setattr(run_scanners, "save_json", fake_save)

    result = run_scanners.run_all("example.com", ports="1-10", workers=1)

    assert result == {
        "assets": "assets.json",
        "ports": "ports.json",
        "ssl": "ssl_results.json",
        "tech": "tech_stack.json",
    }
    # ensure save_json called for each prefix
    assert set(saved.keys()) == {"assets", "ports", "ssl_results", "tech_stack"}

