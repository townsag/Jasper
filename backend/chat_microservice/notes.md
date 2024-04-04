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
