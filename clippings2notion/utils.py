import os

def load_dotenv():
    with open(".env", "r") as f:
        for line in f.readlines():
            key, value = line.split("=")
            os.environ[key] = value.strip()