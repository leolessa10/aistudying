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
# Unsplash API key. You need to create an account on Unsplash Developer.
UNSPLASH_ACCESS_KEY=
# Path to the Mistral model file used by llama.cpp. 
LLAMA_CLI_PATH=/aistudying/modelos/llama.cpp/build/bin/llama-cli

# Path to the Mistral model file (GGUF format). Download on https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF
MODEL_PATH=/aistudying/modelos/mistral-7b-instruct-v0.1.Q4_K_M.gguf

# Directory where the final generated videos will be stored.
VIDEO_FINAL_DIR=/repos/videofinal

# Temporary directory to store files during processing. Must be an accessible path on the system.
TEMP_DIR=/repos//tmp

# Server address where the backend API will be running. Can be an IP or a configured domain.
SERVER_HOST=server.com

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
