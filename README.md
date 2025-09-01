# Postify


##  Project Description

This project is an **AI-powered marketing assistant** designed to help users create effective marketing strategies, generate engaging content, and analyze performance. It simplifies the process of planning, posting, and optimizing social media campaigns.  

## AI Features  

- AI-Driven Marketing Plan  
- Content Creation Assistance  
- Insights & Performance Analysis  

## Tech Stack 

- Python  
- FastAPI  
- MongoDB 
- Docker
- LangGraph

##  How to Run  

1️⃣ Clone repo:
```bash
git clone <repo-link>
cd project-folder
```
2️⃣ Create a new environment:
```bash
conda create -n env-name python=3.10
```
3️⃣ Activate the environment:
```bash
conda activate env-name
```
### Install the required packages
```bash
cd src
cp .env.example .env
pip install -r requirements.txt
```
### Run Docker Compose Services
```bash
docker compose up
```
### Run the FastAPI server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```
