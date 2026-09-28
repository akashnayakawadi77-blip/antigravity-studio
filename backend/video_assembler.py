import os
import numpy as np

# Fix: Pillow 10+ removed ANTIALIAS; MoviePy still uses it internally
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import (
    VideoClip, AudioFileClip, CompositeVideoClip,
    concatenate_videoclips, VideoFileClip, ImageClip
)
from backend.panda_animator import create_panda_frame, create_broll_frame

W, H = 1280, 720
FPS = 24


def _make_panda_clip(text: str, destination: str, duration: float) -> VideoClip:
    """Generate an animated panda VideoClip for a given duration."""
    total_frames = int(duration * FPS)

    def make_frame(t):
        frame_index = int(t * FPS)
        return create_panda_frame(
            width=W, height=H,
            caption_text=text,
            destination=destination,
            frame_index=frame_index,
            total_frames=total_frames,
            is_talking=True
        )

    return VideoClip(make_frame, duration=duration).set_fps(FPS)


def _make_broll_clip(description: str, destination: str, duration: float,
                     video_path: str = None) -> VideoClip:
    """Generate a B-roll clip — real footage if available, else animated gradient."""
    if video_path and os.path.exists(video_path):
        try:
            ext = os.path.splitext(video_path)[1].lower()
            # webm and mp4 both supported via ffmpeg
            clip = VideoFileClip(video_path, audio=False)  # mute source audio
            clip = clip.resize((W, H))
            if clip.duration < duration:
                # Loop if clip is shorter than needed
                repeats = int(np.ceil(duration / clip.duration))
                from moviepy.editor import concatenate_videoclips
                clip = concatenate_videoclips([clip] * repeats)
            clip = clip.subclip(0, min(duration, clip.duration))
            # Add subtle fade in/out
            clip = clip.fadein(0.5).fadeout(0.5)
            return clip
        except Exception as e:
            print(f"  Could not load B-roll ({os.path.basename(video_path)}): {e}. Using gradient.")

    # Animated gradient fallback
    def make_frame(t):
        return create_broll_frame(
            width=W, height=H,
            label_text=description,
            destination=destination,
            frame_index=int(t * FPS)
        )

    return VideoClip(make_frame, duration=duration).set_fps(FPS)


def _get_audio_duration(audio_path: str) -> float:
    """Get duration of an audio file in seconds."""
    try:
        clip = AudioFileClip(audio_path)
        dur = clip.duration
        clip.close()
        return dur
    except Exception:
        return 30.0  # fallback 30 seconds


def assemble_video(
    segments: list,
    voiceover_path: str,
    broll_paths: list,
    destination: str,
    output_path: str,
    progress_callback=None
) -> str:
    """
    Assembles the full YouTube video from segments, voiceover, and B-roll.

    segments: list of {'type': 'PANDA'|'BROLL', 'text': str, 'description': str}
    voiceover_path: path to the full MP3 voiceover (or None)
    broll_paths: list of local B-roll video file paths
    destination: destination name for theming
    output_path: where to save the final MP4
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Determine total audio duration to distribute across segments
    if voiceover_path and os.path.exists(voiceover_path):
        total_audio_dur = _get_audio_duration(voiceover_path)
    else:
        total_audio_dur = len(segments) * 25.0  # 25s per segment fallback

    # Calculate per-segment duration based on text length ratio
    total_chars = sum(max(len(s['text']), 50) for s in segments)
    clips = []
    broll_idx = 0

    for i, seg in enumerate(segments):
        seg_chars = max(len(seg['text']), 50)
        seg_duration = max(5.0, (seg_chars / total_chars) * total_audio_dur)
        seg_duration = min(seg_duration, 90.0)  # cap at 90s per segment

        if progress_callback:
            progress_callback(f"🎬 Rendering segment {i+1}/{len(segments)}: {seg['type']}...")

        if seg['type'] == 'PANDA':
            clip = _make_panda_clip(
                text=seg['text'][:200],
                destination=destination,
                duration=seg_duration
            )
        else:  # BROLL
            broll_path = broll_paths[broll_idx % len(broll_paths)] if broll_paths else None
            broll_idx += 1
            clip = _make_broll_clip(
                description=seg.get('description', destination)[:100],
                destination=destination,
                duration=seg_duration,
                video_path=broll_path
            )

        clips.append(clip)

    if progress_callback:
        progress_callback("🔗 Concatenating all clips...")

    # Concatenate all clips
    final_video = concatenate_videoclips(clips, method="compose")

    # Add voiceover audio
    if voiceover_path and os.path.exists(voiceover_path):
        if progress_callback:
            progress_callback("🎙️ Adding voiceover audio...")
        audio = AudioFileClip(voiceover_path)
        # Trim or pad to match video duration
        if audio.duration > final_video.duration:
            audio = audio.subclip(0, final_video.duration)
        final_video = final_video.set_audio(audio)

    if progress_callback:
        progress_callback("💾 Encoding final MP4 (this may take a few minutes)...")

    # Write final video
    final_video.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        bitrate="3000k",
        audio_bitrate="192k",
        threads=4,
        preset="ultrafast",
        logger=None
    )

    # Close all clips to free memory
    for c in clips:
        c.close()
    final_video.close()

    return output_path
