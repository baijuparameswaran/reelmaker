from pathlib import Path
from gtts import gTTS
from typing import List
from .models import Scene


def synthesize_scenes(scenes: List[Scene], out_dir: Path, lang: str = "en") -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    combined_path = out_dir / "narration.txt"
    # Save narration script for reference
    with combined_path.open('w', encoding='utf-8') as f:
        for s in scenes:
            f.write(s.text + "\n")
    # Produce individual mp3s and later combine with moviepy directly from text segments
    # Return directory path; combination handled in video assembly.
    return out_dir


def tts_segment_to_file(text: str, path: Path, lang: str = "en"):
    tts = gTTS(text=text, lang=lang)
    tts.save(str(path))
