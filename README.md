# InvoiceWizzard - AI powered Web Application
This repository contains a backend of web application designed to create, generate, manage invoices and extract their data using LLM models.
<p align="center">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=python,fastapi,kafka,postgres,redis,docker," />
  </a>
</p>

## Requirements:
* Linux, Windows 10/11 or macOS operating system 
* Docker
* Docker-Compose

## Running application locally:
1. Copy content of ```.env.template``` file.
2. Create ```.env``` file and paste the previously copied content into it.
3. If you use Windows or Linux system with Nvidia GPU go to ```docker-compose.yml``` and uncomment this ollama section:
```
# deploy:
    #   resources:
    #     reservations:
    #       devices:
    #       - driver: nvidia
    #         count: 1
    #         capabilities: [gpu]
```
3. Run command ```docker-compose up -d```.
4. Run migration with ```run_migration.sh``` script.
6. To verify app open web browser at ```http://localhost:8081/docs``` address.


## Architecture Diagram
<div style="text-align: center;">
    <img width="100%" src="/readme_images/InvoiceWizzard.png">
</div>