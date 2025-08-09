from pathlib import Path
from typing import List
from moviepy.editor import ColorClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip, TextClip
from moviepy.config import change_settings
from .models import Scene
from .config import VIDEO_WIDTH, VIDEO_HEIGHT, FPS
from .tts import tts_segment_to_file
import tempfile

change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

def build_video(scenes: List[Scene], out_path: Path, voice_lang: str = "en") -> Path:
    clips = []
    audio_clips = []
    temp_dir = Path(tempfile.mkdtemp(prefix="reel_tts_"))

    for scene in scenes:
        # TTS for the scene
        mp3_path = temp_dir / f"scene_{scene.index}.mp3"
        tts_segment_to_file(scene.text, mp3_path, lang=voice_lang)
        audio = AudioFileClip(str(mp3_path))
        # Simple colored background (can randomize color)
        bg = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(20 + scene.index*15 % 255, 40, 120), duration=audio.duration)
        txt = TextClip(scene.text, fontsize=48, color='white', size=(VIDEO_WIDTH-100, None), method='caption')
        txt = txt.set_position(('center','center')).set_duration(audio.duration)
        clip = CompositeVideoClip([bg, txt]).set_audio(audio)
        clips.append(clip)
        audio_clips.append(audio)

    final = concatenate_videoclips(clips)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    final.write_videofile(str(out_path), fps=FPS, codec='libx264', audio_codec='aac')
    final.close()
    for c in clips:
        c.close()
    for a in audio_clips:
        a.close()
    return out_path
