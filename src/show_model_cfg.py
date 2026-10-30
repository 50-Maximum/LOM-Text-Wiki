# -*- coding: utf-8 -*-
"""只看模型相关配置，不打印任何密钥。"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = r"C:\Users\Luo\.openclaw\openclaw.json"
d = json.load(open(p, encoding="utf-8"))

def show(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if any(x in k.lower() for x in ("key", "token", "secret", "password")):
                continue
            show(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            show(v, f"{path}[{i}]")
    else:
        print(f"{path} = {obj}")

print("== agents.defaults ==")
show(d.get("agents", {}).get("defaults", {}), "agents.defaults")
print("\n== models ==")
show(d.get("models", {}), "models")
