# Speech Transcription API

This repository contains a FastAPI application that provides an endpoint to transcribe audio files using Google Cloud Speech-to-Text with streaming recognition.

## Features

- Transcribes uploaded audio files using streaming speech recognition.
- Supports real-time streaming response in JSON format.
- Integrated with Google Cloud Speech-to-Text.

## Requirements

- Docker
- Google Cloud credentials with access to the Speech-to-Text API.

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/speech-transcription-api.git
cd speech-transcription-api
```

### 2. Set Up Google Cloud Credentials

Ensure that your Google Cloud credentials are set up using `gcloud`. Follow these steps:

1. **Authenticate with Google Cloud**:

```bash
gcloud auth login
```
2. **Set your Google Cloud project**:

```bash
gcloud config set project YOUR_PROJECT_ID
```
Replace YOUR_PROJECT_ID with your actual Google Cloud project ID.

3. **Enable the Speech-to-Text API**:

```bash
gcloud services enable speech.googleapis.com
```

3. **Set up Application Default Credentials**:

```bash
gcloud auth application-default login
```

### 3. Build the Docker Image

Build the Docker image using the Dockerfile provided.

```bash
docker build -t speech-transcription-api .
```

### 4. Run the Docker Container

Run the Docker container:

```bash
docker run -p 3000:3000 --name speech-transcription-api -v ~/.config/gcloud/application_default_credentials.json:/app/application_default_credentials.json -e GOOGLE_APPLICATION_CREDENTIALS="/app/application_default_credentials.json" speech-transcription-api

```

This command:

    Runs the container in detached mode.
    Maps port 3000 of the container to port 3000 of your local machine.
    Sets the GOOGLE_APPLICATION_CREDENTIALS environment variable inside the container.

### 5. Access the API
Once the container is running, you can access the API at:
```
http://localhost:3000/docs
```
Here, you can interact with the API through the automatically generated Swagger UI.

### 6. Transcribe an Audio File Using `curl`

You can use `curl` to upload an audio file and get the transcription results. Here's an example:
```bash
curl -N -X POST "http://localhost:3000/transcribe" \
-H "accept: application/stream+json" \
-H "Content-Type: multipart/form-data" \
-F "file=@/path/to/your/audio-file.wav"
```

* Replace /path/to/your/audio-file.wav with the path to the audio file you want to transcribe.
* The response will be streamed back in real-time as JSON.

### Example Response 
The response will look something like this:
```json
{"alternatives": [{"transcript": "This", "confidence": 0.65}], "is_final": false}
{"alternatives": [{"transcript": "This is", "confidence": 0.88}], "is_final": false}
{"alternatives": [{"transcript": "This is a sample", "confidence": 0.86}], "is_final": false}
{"alternatives": [{"transcript": "This is a sample transcription.", "confidence": 0.97}], "is_final": true}
```

##  Endpoints
***/transcribe*** **[POST]**

Upload an audio file to be transcribed.
* Consumes: `multipart/form-data`
* Produces: `application/stream+json`
* Parameters:
    * file: The audio file to be transcribed (required).
* Response:
    * A streaming JSON response containing the recognized speech transcript.

##  Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

##  License

This project is licensed under the MIT License.