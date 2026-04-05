import os
from pathlib import Path


def ingest(file_path: str) -> str:

    # Route file to the correct extractor and return extracted text.
    # Supported: .pdf, .mp4, .mp3, .wav, .md, .txt

    if file_path.startswith("http://") or file_path.startswith("https://"):
        # Process as a web URL
        return _ingest_video_url(file_path)

    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        return _ingest_pdf(path)
    elif ext in (".mp4", ".webm", ".mkv"):
        return _ingest_video(path)
    elif ext in (".mp3", ".wav", ".ogg", ".m4a"):
        return _ingest_audio(path)
    elif ext in (".md", ".txt", ".rst"):
        return path.read_text(encoding="utf-8", errors="replace")
    else:
        return f"Unsupported format: {ext}"


def _ingest_pdf(path: Path) -> str:
    # Extract text from PDF using Docling (primary) or Marker (fallback).
    try:
        from docling.document_converter import DocumentConverter

        converter = DocumentConverter()
        result = converter.convert(str(path))
        return result.document.export_to_markdown()
    except ImportError:
        pass

    try:
        from marker.convert import convert_single_pdf

        text, _, _ = convert_single_pdf(str(path), None, None)
        return text
    except ImportError:
        pass

    return f"(No PDF extractor installed. Place Docling or Marker .whl in venv.)\nFile: {path.name}"


def _ingest_video_url(url: str) -> str:
    try:
        import os
        import tempfile

        import whisper
        import yt_dlp

        with tempfile.TemporaryDirectory() as temp_dir:
            out_file = os.path.join(temp_dir, "audio.mp3")
            ydl_opts = {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                "outtmpl": os.path.join(temp_dir, "audio.%(ext)s"),
                "quiet": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            model = whisper.load_model("base")
            result = model.transcribe(out_file)
            return result["text"]
    except ImportError:
        return f"(whisper / yt-dlp not installed. Run: pip install openai-whisper yt-dlp openai-whisper)\\nURL: {url}"


def _ingest_video(path: Path) -> str:
    """Transcribe local video using Whisper."""
    try:
        import whisper

        model = whisper.load_model("base")
        result = model.transcribe(str(path))
        return result["text"]
    except ImportError:
        return f"(whisper not installed. Run: pip install openai-whisper)\\nFile: {path.name}"


def _ingest_audio(path: Path) -> str:
    try:
        import whisper

        model = whisper.load_model("base")
        result = model.transcribe(str(path))
        return result["text"]
    except ImportError:
        return f"(whisper not installed. Run: pip install openai-whisper)\\nFile: {path.name}"
