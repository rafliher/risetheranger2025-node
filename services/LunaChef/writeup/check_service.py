import requests

ips = {
    "node1": "52.221.234.242",
    "node2": "52.221.242.191",
    "node3": "18.142.56.63",
    "node4": "175.41.158.164",
    "node5": "54.179.6.202",
    "node6": "52.221.208.137",
    "node7": "47.129.48.212",
    "node8": "47.129.43.88",
    "node9": "3.0.58.16",
    "node10": "13.229.240.27",
}

port = [
    11000,
    12000,
    13000,
    14000,
    # 15000
]

for name, ip in ips.items():
    for p in port:
        try:
            r = requests.get(f"http://{ip}:{p}", timeout=5)
            print(f"[{name}] {ip}:{p} -> {r.status_code}")
        except Exception as e:
            print(f"[{name}] {ip}:{p} -> ERROR: {e}")
