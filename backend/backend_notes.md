- next steps:
    - use the steps in this tutorial https://docs.docker.com/network/network-tutorial-standalone/ to verify that http communication exists between containers
    - refactor frontend to use environement variables for hostname and port instead of hardcoded values
    - look thuroughly at backend logs to figure out why it is exiting with 137

- how to run the chat microservice
    - cd /Users/andrewtownsend/Desktop/ML_personal_projects/Jasper/backend
    - flask --app chat_microservice run
- how to run the db init command
    - cd /Users/andrewtownsend/Desktop/ML_personal_projects/Jasper/backend
    - flask --app chat_microservice init-db 

- Weaviate info
    - How do I know when Weaviate is up and ready? Weaviate implements a readiness check at GET /v1/.well-known/ready. It will return a 2xx HTTP status code once everything is ready. To check for the readiness programmatically you can use curl in this simple bash loop:

        until curl --fail -s localhost:8080/v1/.well-known/ready; do
        sleep 1
        done
- cannot mock the attributes/methods of the specific oai_client object stored in the flask.g object because that object (g) is only "global" in the current application context and the application context has the same lifetime as a request. So if I change that client object using a monkeypatch before calling the endpoint it wont impact the behavior inside the call to the endpoint because a new application context will be created.

- ToDo:
    - add the little bits of important information for pytest
        - how to run pytest tests in verbose mode
            - pytest -v
        - how to trigger pdb on the first error
            - pytest -x --pdb
        - how to print all the fixtures applied to each test
            - pytest --fixtures-per-test
        - how to show the coverage of the testing
            - coverage run -m pytest -v
              coverage report
              coverage html
        - how to allow print statements in the pytest for debugging your tests
            - pytest --capture=no
        - __IMPORTANT__: do not try to mock the behavior of functions in modules that your code imports before the monkeypatch executes. As Anrej Karpathy would say, this is the path to suffering

- docker info:
    - view images:
        - sudo docker images
    - view running and stopped containers:
        - sudo docker ps -a 
    - build the image:
        - cd backend/
        - sudo docker build -t chat-microservice .
    - run the container:
        - sudo docker run -p 5000:5000 chat-microservice
    - stop the container:
        - sudo docker stop <container id>
    - delete the container
        - sudo docker rm <container id>
    - delete the image
        - sudo docker rmi <image name or id>
    - show networks available to docker
        - sudo docker network ls
    - inspect a specific network
        - sudo docker network inspect <name>
    - start a terminal inside a container
        - docker exec -it <container-name> sh
    - What is the difference between a container and an image?
    - What is actually being built when you build an image
    - Why did I get the weird error when trying to connect to the flask backend from the host machine when the backend was running inside the container? ( curl: (56) Recv failure: Connection reset by peer) The error was resolved by adding --host=0.0.0.0 to the entrypoint command: CMD flask --app chat_microservice run --host=0.0.0.0 . Why did this resolve the error?
        - Limited understanding: The flask app by default will listen on 127.0.0.1 (loopback network interface) inside the container. Even if I map 5000 on the host machine to 5000 inside the container, that mapping goes to a different network interface than the loopback network interface (probably goes to eth0 inside the container). Instead I want to set the flask app listening on all available network interfaces (this includes the network interface between the container and host machine) so that the host machine can make requests to the flask app

- notes for backing up the weaviate data:
    - created backup using:
        - docker run --rm --volumes-from jasper-weaviate-1 -v $(pwd):/backup ubuntu tar cvf /backup/backup.tar /var/lib/weaviate
    - create volume on second machine:
        - sudo docker volume create weaviate_data
    - untar the backup into the named volume on second machine
        - cd /directory/with/backup/
        - sudo docker run --rm -v weaviate_data:/var/lib/weaviate -v $(pwd):/backup ubuntu bash -c "cd /var/lib/weaviate && tar xvf /backup/backup.tar --strip 3"
            - use --strip 3 to copy the contents of the the .tar file without the leading directory structure (/var/lib/weaviate/)
            - this is not the best solution because the number of directories to strip would depend on the directory structure of the volume that is being archived, therefore this solutions is not very general
            - consider a different solution with these commands to backup and restore the volume:
                - docker run --rm --volumes-from jasper-weaviate-1 -v $(pwd):/backup ubuntu tar cvf /backup/backup.tar -C /var/lib/weaviate .
                - sudo docker run --rm -v weaviate_data:/var/lib/weaviate -v $(pwd):/backup ubuntu bash -c "cd /var/lib/weaviate && tar xvf /backup/backup.tar --strip 1"
                    - not sure if we need the --strip 1
    - create an ubuntu container from which I can verify the migration
        - sudo docker run --rm -v weaviate_data:/var/lib/weaviate -it ubuntu bash
    - instructions:
        - https://docs.docker.com/storage/volumes/#back-up-restore-or-migrate-data-volumes
    - __REMEMBER__: if you dont add the external:true flag to volumes in your docker compose files, then that volume will be different than the volume that you created using docker volume create, this will be hard to debug

- SSH:
	- ssh into the google cloud compute engine vm:
		- ssh -i ~/.ssh/id_rsa townsag@35.223.114.159  
	- create forward the requests from localhoast:8080 on my local machine to localhost:8080 on the VM
		- ssh -L 8080:localhost:8080 townsag@35.223.114.159

- steps to add the SSH key to the vm:
	- https://cloud.google.com/compute/docs/connect/add-ssh-keys#console
	- navigate to the metadata page: https://console.cloud.google.com/compute/metadata/sshKeys
	- add this to the metadata page:
		ssh-rsa AAAAB3N.......xdbfPgEE= townsag


- resource for installing pyenv:
    - https://www.dwarmstrong.org/pyenv/
- resource for installing docker engine:
    - https://docs.docker.com/engine/install/debian/