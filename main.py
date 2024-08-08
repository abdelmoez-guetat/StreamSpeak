from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from google.cloud import speech_v1
from typing import AsyncIterator
import io
import json


app = FastAPI(
    title="Speech Transcription API",
    description="This API provides an endpoint to transcribe audio files using Google Cloud Speech-to-Text with streaming recognition.",
    version="1.0.0",
    contact={
        "name": "Abdelmoez GUETAT",
        "email": "gabdelmoez@gmail.com",
    },
)


client = speech_v1.SpeechAsyncClient()

streaming_config = speech_v1.StreamingRecognitionConfig(
    config=speech_v1.RecognitionConfig(
        encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,  

        sample_rate_hertz=16000,
        language_code="en-US",  

    ),
    interim_results=True,
)

CHUNK_SIZE = 8192


async def request_generator(buffer: io.BytesIO) -> AsyncIterator[speech_v1.StreamingRecognizeRequest]:
    """
    Generates requests for streaming speech recognition using the provided audio buffer.

    Args:
        buffer (io.BytesIO): The audio buffer containing the audio data.

    Yields:
        speech_v1.StreamingRecognizeRequest: An asynchronous iterator yielding StreamingRecognizeRequest objects for the speech recognition service.
    """
    yield speech_v1.StreamingRecognizeRequest(streaming_config=streaming_config)
    while True:
        try:
            chunk = buffer.read(CHUNK_SIZE)
            if not chunk:
                break
            yield speech_v1.StreamingRecognizeRequest(audio_content=chunk)
        except (OSError, IOError) as e:
            raise HTTPException(status_code=500, detail=f"Error reading audio: {str(e)}")


async def recognize_speech(requests: AsyncIterator[speech_v1.StreamingRecognizeRequest]) -> AsyncIterator[str]:
    """
    Performs streaming speech recognition using the provided requests and Google Cloud Speech API.

    Args:
        requests (speech_v1.AsyncIterator[speech_v1.StreamingRecognizeRequest]): An asynchronous iterator yielding StreamingRecognizeRequest objects.

    Yields:
        str: An asynchronous iterator yielding JSON strings containing the recognized speech transcript and confidence information.
    """
    try:
        async for response in await client.streaming_recognize(requests):
            for result in response.results:
                data = {
                    "alternatives": [
                        {"transcript": alternative.transcript, "confidence": alternative.confidence}
                        for alternative in result.alternatives
                    ],
                    "is_final": result.is_final,
                }
                yield json.dumps(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during recognition: {str(e)}")


@app.post(
    "/transcribe",
    response_class=StreamingResponse,
    response_description="Streaming JSON response containing the recognized speech transcript.",
    responses={
        200: {
            "description": "A streaming response in JSON format.",
            "content": {
                "application/stream+json": {
                    "example": {"alternatives": [{"transcript": "string", "confidence": 0.9}], "is_final": True}
                }
            },
            "headers": {
                "Transfer-Encoding": {
                    "description": "Indicates that the response is sent in chunks.",
                    "schema": {
                        "type": "string",
                        "example": "chunked"
                    }
                }
            },
        },
        500: {"description": "Internal server error"},
    },)
async def transcribe_endpoint(file: UploadFile = File(...)):
    """
    Transcribes uploaded audio file using streaming speech recognition.

    Args:
        file (UploadFile): The uploaded audio file containing the speech data.

    Returns:
        StreamingResponse: A streaming response object containing the recognized speech transcript in JSON format.
        
    This endpoint accepts audio files and streams the transcription results back in real-time.
    """
    try:
        buffer = io.BytesIO(await file.read())
        requests = request_generator(buffer)
        return StreamingResponse(recognize_speech(requests), media_type="application/stream+json", headers={"Transfer-Encoding": "chunked"})
    except (ValueError, HTTPException) as e: 
        raise e 


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port)
