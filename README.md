# Postify


##  Project Description

This project is an **AI-powered marketing assistant** designed to help users create effective marketing strategies, generate engaging content, and analyze performance. It simplifies the process of planning, posting, and optimizing social media campaigns.  

## AI Features  

- **AI-Driven Marketing Plans** - Generate comprehensive marketing strategies tailored to your business goals
- **Content Creation Assistance** - Create engaging posts, captions, and descriptions with AI
- **Interactive Chat & Voice Interface** - Conversational AI for marketing guidance and content ideation

## Tech Stack 

- **Backend Framework**: FastAPI
- **Programming Language**: Python 3.10+
- **AI Framework**: LangGraph, LangChain
- **Database**: MongoDB
- **Containerization**: Docker & Docker Compose
- **Environment Management**: Conda
- **Real-time Communication**: Socket.IO
- **Deployment**: Azure App Service / Azure Container Instances

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
### Configure environment variables:
Edit the `.env` file with your API keys and configuration:
```env
MODEL_NAME=your_model_name
GOOGLE_API_KEY=your_google_api_key
HF_TOKEN=your_huggingface_token
VOICE_URL=your_voice_model_url
MONGODB_URL=your_mongodb_connection_string
```

### Run Docker Compose Services
```bash
docker compose up
```
### Run the FastAPI server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```
