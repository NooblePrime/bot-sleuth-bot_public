import json
from time import time

def logCheck(name: str, message: str):
    try:
        with open("cache.json", 'r+') as file:
            cache = json.load(file)
            last_checked = cache["checked_users"].get(name, {}).get("time", 0)
            if time() - last_checked > 86400:  # 24 hours
                cache["checked_users"][name] = {"time": time(), "message": message}
                file.seek(0)
                json.dump(cache, file, indent=4)
                file.truncate()
    except (FileNotFoundError, json.JSONDecodeError):
        cache = {"checked_users": {name: {"time": time(), "message": message}}, "cooldowns": {}}
        with open("cache.json", 'w') as file:
            json.dump(cache, file, indent=4)

def logCooldown(name: str):
    try:
        with open("cache.json", 'r+') as file:
            cache = json.load(file)
            cache["cooldowns"][name] = {"time": time()}
            file.seek(0)
            json.dump(cache, file, indent=4)
            file.truncate()
    except (FileNotFoundError, json.JSONDecodeError):
        cache = {"checked_users": {}, "cooldowns": {name: {"time": time()}}}
        with open("cache.json", 'w') as file:
            json.dump(cache, file, indent=4)

def checkIfVisited(id: str):
    try:
        with open('cache.json', 'r') as file:
            cache = json.load(file)
            return id in cache.get("visited_posts", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return False

def logVisit(id: str):
    try:
        with open('cache.json', 'r+') as file:
            cache = json.load(file)
            if "visited_posts" not in cache:
                cache["visited_posts"] = []
            cache["visited_posts"].append(id)
            file.seek(0)
            json.dump(cache, file, indent=4)
            file.truncate()
    except (FileNotFoundError, json.JSONDecodeError):
        cache = {"visited_posts": [id]}
        with open('cache.json', 'w') as file:
            json.dump(cache, file, indent=4)

def cacheCleaner():
    try:
        with open("cache.json", 'r+') as file:
            cache = json.load(file)
            for user in list(cache["checked_users"]):
                if time() - cache["checked_users"][user]["time"] > 86400:
                    del cache["checked_users"][user]
            for user in list(cache["cooldowns"]):
                if time() - cache["cooldowns"][user]["time"] > 600:
                    del cache["cooldowns"][user]
            if "visited_posts" in cache and len(cache["visited_posts"]) > 200:
                cache["visited_posts"] = cache["visited_posts"][-200:]
            file.seek(0)
            json.dump(cache, file, indent=4)
            file.truncate()
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    except Exception as e:
        print("Error in cacheCleaner:", e)
        pass
    return