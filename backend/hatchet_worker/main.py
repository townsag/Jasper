from .hatchet import hatchet
from .workflow import VanillaRagWorkflow

def start():
    worker = hatchet.worker('first-worker')
    worker.register_workflow(VanillaRagWorkflow())
    worker.start()

print("this is name in main.py:", __name__)

if __name__ == "__main__":
    start()