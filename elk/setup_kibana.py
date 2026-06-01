"""
Скрипт создания Index Pattern в Kibana через API.
Запускать после того как все сервисы подняты: docker-compose up --build

Запуск: python elk/setup_kibana.py
"""
import urllib.request
import urllib.error
import json
import time


KIBANA_URL = "http://localhost:5601"
INDEX_PATTERN = "deeplink-logs-*"


def wait_for_kibana():
    print("Ожидание запуска Kibana...")
    for i in range(30):
        try:
            req = urllib.request.Request(f"{KIBANA_URL}/api/status")
            req.add_header("kbn-xsrf", "true")
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read())
                if data.get("status", {}).get("overall", {}).get("level") == "available":
                    print("Kibana готова!")
                    return True
        except Exception:
            pass
        print(f"  попытка {i+1}/30...")
        time.sleep(5)
    return False


def create_index_pattern():
    print(f"Создание index pattern: {INDEX_PATTERN}")
    payload = json.dumps({
        "attributes": {
            "title": INDEX_PATTERN,
            "timeFieldName": "@timestamp"
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{KIBANA_URL}/api/saved_objects/index-pattern",
        data=payload,
        method="POST"
    )
    req.add_header("Content-Type", "application/json")
    req.add_header("kbn-xsrf", "true")

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            print(f"Index pattern создан: {result.get('id')}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if "Saved object [index-pattern" in body and "already exists" in body:
            print("Index pattern уже существует, пропускаем.")
            return True
        print(f"Ошибка: {e.code} — {body}")
        return False


if __name__ == "__main__":
    if wait_for_kibana():
        create_index_pattern()
        print("\nГотово! Открывай Kibana: http://localhost:5601")
        print("Stack Management → Index Patterns — там будет deeplink-logs-*")
        print("Discover → выбери deeplink-logs-* — там все логи")
    else:
        print("Kibana не ответила за отведённое время.")
