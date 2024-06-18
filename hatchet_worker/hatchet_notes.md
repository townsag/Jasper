- hatchet lite
    - running hatchet lite service:
        cd Jasper/
        sudo docker compose -f docker-compose.hatchet.yml start
    - stopping hatchet lite service:
        cd Jasper/
        sudo docker compose -f docker-compose.hatchet.yml stop
    - running hatchet worker python process
        - pyenv activate jasper_hatchet
        - python Jasper/backend/hatchet/first_worker.py
- example rag workflow input:
    {"messages": [{"role": "user","content": "what is the purpose of the einsum function"}]}