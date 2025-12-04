# Maya1 TTS Project Walkthrough

## Overview
This project provides a high-performance TTS pipeline using the **Maya1** model, optimized for NVIDIA L4 GPUs. It includes a FastAPI backend and a React/Vite frontend for expressive speech synthesis.

**Repository**: [https://github.com/Chaudharyritik/dbee-tts-maya1-new](https://github.com/Chaudharyritik/dbee-tts-maya1-new)

## Prerequisites
- **NVIDIA GPU** (L4 recommended, 24GB VRAM).
- **Docker** & **NVIDIA Container Toolkit**.
- **Python 3.10+** (for local dev).
- **Node.js 18+** (for local dev).

## Running the Project

### Option 1: Direct Execution (Recommended for Dev/VM)

Since you are running on a VM with a GPU, you can run the project directly. The model will be downloaded from Hugging Face on the first run.

1.  **Start the Application**:
    ```bash
    ./start_dev.sh
    ```
    This script handles:
    - Python virtual environment creation.
    - Installation of dependencies (including `torch`, `transformers`, `snac`).
    - Starting the FastAPI backend (port 8000).
    - Starting the Vite frontend (port 5173).

2.  **Using Existing Model**:
    *   **Automatic**: If your model is already in the default Hugging Face cache (`~/.cache/huggingface/hub/models--maya-research--maya1`), the application will detect it automatically. You don't need to do anything special.
    *   **Explicit Path**: If you want to point to a specific folder (e.g., a specific snapshot), set the variable:
        ```bash
        # Example: Pointing to a specific snapshot in the cache
        export MODEL_PATH="/home/username/.cache/huggingface/hub/models--maya-research--maya1/snapshots/YOUR_SNAPSHOT_HASH"
        ./start_dev.sh
        ```

3.  **First Run Note**:
    If the model is not found locally, it will download the **Maya1 model (approx 6GB)** on the first run.

### Option 2: Docker

If you prefer containerization:
1.  `docker build -t maya1-tts .`
2.  `docker run --gpus all -p 8000:8000 maya1-tts`

## Using the Interface

1.  **Voice Description**: Enter a natural language description (e.g., "Old wizard, raspy voice").
2.  **Input Text**: Type your text. Use tags like `<laugh>` for expressions.
3.  **Synthesize**: Click to generate.

## Architecture Notes
- **Backend**: `backend/app` - FastAPI application. `tts_service.py` handles the model loading (currently a placeholder for dev, uncomment lines to load actual model).
- **Frontend**: `frontend/src` - React application with TailwindCSS.
- **Model**: Uses `maya-research/maya1` from Hugging Face.
