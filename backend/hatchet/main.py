from .hatchet import hatchet
from .workflow import VanillaRagWorkflow

def start():
    worker = hatchet.worker('first-worker')
    worker.register_workflow(VanillaRagWorkflow())
    worker.start()