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