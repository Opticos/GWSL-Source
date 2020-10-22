# Get Settings
import json

path = None


def create(path):
    with open(path, "w") as obj:
        app = {
            "conf_ver": 3,
            "general": {"clipboard": True, "position": "right"},
            "graphics": {"window_mode": "multi"},
            "putty": {"ip": None},
            "distro_blacklist": ["docker"],
            "app_blacklist": ["exampleblock"],
        }

        json.dump(app, obj, indent=True)
        obj.close()


"""
def get(setting):
    settings = setting.split(sep=".")
    with open(path, "r") as obj:
        current = json.load(obj)
        try:
            for s in settings:
                current = current[s]
            obj.close()
            return current
        except:
            return None
"""


def read():
    with open(path, "r") as obj:
        current = json.load(obj)
        obj.close()
        return current


def set(json_f):
    with open(path, "w") as obj:
        json.dump(json_f, obj, indent=True)
        obj.close()
