from .hatchet import hatchet
from .workflow import VanillaRagWorkflow

def start():
    print("\n=====\ncreating hatchet worker")
    worker = hatchet.worker('first-worker')
    print("\n=====\nregistering rag workflow")
    worker.register_workflow(VanillaRagWorkflow())
    print("\n=====\nstarting worker process")
    worker.start()

print("this is name in main.py:", __name__)

if __name__ == "__main__":
    start()