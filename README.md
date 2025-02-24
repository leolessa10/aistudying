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
UNSPLASH_ACCESS_KEY=
LLAMA_CLI_PATH=
MODEL_PATH=
VIDEO_FINAL_DIR=
TEMP_DIR=
SERVER_HOST=
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
