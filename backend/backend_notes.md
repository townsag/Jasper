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
    - What is the difference between a container and an image?
    - What is actually being built when you build an image
    - Why did I get the weird error when trying to connect to the flask backend from the host machine when the backend was running inside the container? ( curl: (56) Recv failure: Connection reset by peer) The error was resolved by adding --host=0.0.0.0 to the entrypoint command: CMD flask --app chat_microservice run --host=0.0.0.0 . Why did this resolve the error?
        - Limited understanding: The flask app by default will listen on 127.0.0.1 (loopback network interface) inside the container. Even if I map 5000 on the host machine to 5000 inside the container, that mapping goes to a different network interface than the loopback network interface (probably goes to eth0 inside the container). Instead I want to set the flask app listening on all available network interfaces (this includes the network interface between the container and host machine) so that the host machine can make requests to the flask app