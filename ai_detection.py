import fastapi

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from tika import parser

app = FastAPI
(
    title="File Upload and Metadata Analysis API",
    description="An API for uploading audio/video files and analyzing their metadata using Apache Tika",
    version="1.0.0",
    contact={
        "name": "Your Name",
        "email": "yourname@example.com",
    }
)

@app.post("/upload", summary="Upload a file for analysis", description="Upload an audio or video file and get a metadata analysis.")
async def handle_file_upload(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    try:
        file_content = await file.read()
        metadata = analyze_metadata(file_content)
        return JSONResponse(content={"metadata": metadata}, status_code=200)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze file: {e}")

def analyze_metadata(file_content: bytes):
    parsed = parser.from_buffer(file_content)
    metadata = parsed["metadata"]
    
    mime_type = metadata.get("Content-Type")
    creation_date = metadata.get("Creation-Date")
    codec = metadata.get("xmpDM:audioCompressor") or metadata.get("xmpDM:videoCompressor")

    if mime_type is None or not (mime_type.startswith("audio/") or mime_type.startswith("video/")):
        return "Suspicious file type"
    if not creation_date:
        return "Suspicious: Missing creation time"
    if codec and not is_trusted_codec(codec):
        return "Suspicious: Unusual codec detected"
    
    return "File looks safe"

def is_trusted_codec(codec):
    trusted_codecs = ["mp3", "mp4", "aac"]
    return any(codec.lower() in trusted_codec for trusted_codec in trusted_codecs)