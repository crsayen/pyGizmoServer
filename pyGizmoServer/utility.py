import yaml


class DotDict(dict):
    def __getattr__(self, item):
        val = self[item]
        if isinstance(val, dict):
            return DotDict(val)
        else:
            return val


class Settings:
    @classmethod
    def load(cls, filename):
        try:
            with open(f"./config/{filename}.yml") as f:
                return DotDict(yaml.load(f, Loader=yaml.CLoader))
        except Exception:
            with open(f"./config/{filename}.yml") as f:
                return DotDict(yaml.load(f, Loader=yaml.FullLoader))
        except Exception as e:
            print(f"{e}")
            return None
