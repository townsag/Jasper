from hatchet_sdk import Hatchet
from dotenv import load_dotenv
 
load_dotenv(dotenv_path=".env.hatchet")
hatchet = Hatchet(debug=True)