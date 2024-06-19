from hatchet_sdk import Hatchet, ClientConfig
from dotenv import load_dotenv
import os
from pathlib import Path

print("\n=====\ncreating a connection to hatchet scheduler")
print("this is __name__ in hatchet.py:", __name__)
env_path = os.path.join(Path(__file__).parent.parent, ".env.worker")
# print(env_path)
load_dotenv(dotenv_path=env_path)
# print("token", os.environ.get("HATCHET_CLIENT_TOKEN"))
# hatchet_scheduler_host_port = os.environ.get("PRIVATE_HATCHET_SCHEDULER_HOST") + ":" + os.environ.get("PRIVATE_HATCHET_SCHEDULER_PORT")
# print("this is hatchet scheduler host port:", hatchet_scheduler_host_port)
# config = ClientConfig(
#     host_port=hatchet_scheduler_host_port
# )
# print("this is the client config object:", config.__dict__)
# hatchet = Hatchet(debug=True, config=config)
hatchet = Hatchet(debug=True)
print("\n=====\nthis is the connection to the hatchet scheduler:", hatchet.client.config.host_port)