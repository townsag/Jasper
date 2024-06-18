from hatchet_sdk import Hatchet
from dotenv import load_dotenv
import os
from pathlib import Path

print("\n=====\ncreating a connection to hatchet scheduler")
print("this is __name__ in hatchet.py:", __name__)
env_path = os.path.join(Path(__file__).parent.parent, ".env.worker")
# print(env_path)
load_dotenv(dotenv_path=env_path)
# print("token", os.environ.get("HATCHET_CLIENT_TOKEN"))
hatchet = Hatchet(debug=True)