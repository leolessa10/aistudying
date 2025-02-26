# Flask Backend for Video Generation with Llama.cpp and Unsplash

## Overview
This is a Python Flask backend that uses the **llama.cpp** model (`mistral-7b-instruct-v0.1.Q4_K_M.gguf`) to generate videos. The videos are created based on a summary and the age of the target audience, provided via a React frontend. The images used in the video are fetched from the Unsplash API.

## Prerequisites

### System Packages
Ensure you have the following packages installed:
- `python3`
- `python3-pip`
- `python3-venv`
- `python-dotenv`
- `cmake`
- `build-essential`

### Required Python Libraries
Install the necessary Python libraries using pip:
```bash
pip install flask requests gtts moviepy retrying transformers torch flask_cors python-dotenv
```

### Install Llama.cpp Model
Clone the Llama.cpp repository and set up the model:
```bash
git clone https://github.com/ggerganov/llama.cpp
```

### Node.js Requirement
The project also requires the **axios** module for Node.js:
```bash
npm install axios
```

## Environment Variables

### Backend
Create a `.env` file in the backend project directory and define the following environment variables:
```ini
UNSPLASH_ACCESS_KEY= #Chave de API do Unsplash. Você precisa criar uma conta no Unsplash Developer.
LLAMA_CLI_PATH=/aistudying/modelos/llama.cpp/build/bin/llama-cli  #Caminho para o arquivo do modelo Mistral usado pelo llama.cpp.
MODEL_PATH=/aistudying/modelos/mistral-7b-instruct-v0.1.Q4_K_M.gguf  #Diretório onde os vídeos finais gerados serão armazenados.
VIDEO_FINAL_DIR= /repos/videofinal # Diret[orio ondeo arquivo finalserá gerado.
TEMP_DIR= /tmp # Diretório onde os vídeos finais gerados serão armazenados. Deve ser um caminho acessível no sistema
SERVER_HOST= server.com #Endereço do servidor onde a API do backend estará rodando. Pode ser um IP ou um domínio configurado.
```

### Frontend
Create a `.env` file in the `/frontend` directory and define the following environment variable:
```ini
REACT_APP_API_BASE_URL=http://IPouNOMEdoSERVER:5000
```

## Running the Backend
After setting up the dependencies, you can run the Flask backend using:
```bash
python app.py
```

## Contribution
Feel free to contribute by submitting issues or pull requests.

## License
This project is licensed under an open-source license (MIT, GPL, etc.).
