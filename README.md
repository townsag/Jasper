# Jasper
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![Svelte](https://img.shields.io/badge/svelte-%23f1413d.svg?style=for-the-badge&logo=svelte&logoColor=white)
![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)

Jasper is a programming companion for developers working on projects in JAX. I was motivated to start this project because GPT-3.5 is pretty bad at writing JAX and I want the benefits of writing code with an LLM companion but grounded in the truthfulness of the JAX documentation. Jasper uses the RAG pattern to find chunks of text from the JAX documentation website that are semantically similar to the question asked in the chat. These chunks are then appended to the user question when it is sent to a chat api endpoint for completion.

Jax + expert ~= JAXpert ~= Jasper

## Example View of the chat page
<img src="/assets/chat_example.png" width="650">

## Example View of the login page
![Screenshot of the login page](/assets/login_example.png)
