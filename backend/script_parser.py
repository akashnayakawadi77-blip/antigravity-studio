import os
import re

def parse_script_segments(script: str) -> list:
    """
    Parses the generated script and splits it into segments.
    Returns a list of dicts: {'type': 'PANDA'|'BROLL', 'text': '...', 'description': '...'}
    """
    segments = []
    
    # Split on known tags
    # Look for [TRAVELING PANDA ON SCREEN] and [B-ROLL] blocks
    lines = script.split('\n')
    current_type = 'PANDA'
    current_text = []
    current_description = []
    
    for line in lines:
        line_stripped = line.strip()
        
        if '[TRAVELING PANDA ON SCREEN]' in line_stripped.upper() or '[PANDA ON SCREEN]' in line_stripped.upper():
            if current_text or current_description:
                segments.append({
                    'type': current_type,
                    'text': ' '.join(current_text).strip(),
                    'description': ' '.join(current_description).strip()
                })
                current_text = []
                current_description = []
            current_type = 'PANDA'
        elif '[B-ROLL]' in line_stripped.upper():
            if current_text or current_description:
                segments.append({
                    'type': current_type,
                    'text': ' '.join(current_text).strip(),
                    'description': ' '.join(current_description).strip()
                })
                current_text = []
                current_description = []
            current_type = 'BROLL'
        elif line_stripped.startswith('(Visual:') or line_stripped.startswith('(Prompt'):
            current_description.append(line_stripped)
        elif line_stripped.startswith("Pando's") or line_stripped.startswith("Traveling Panda") or 'Audio:' in line_stripped or 'Voiceover:' in line_stripped:
            # Extract just the spoken text
            spoken = re.sub(r"^(Pando's Audio:|Pando's Voiceover:|Traveling Panda's Audio:|Traveling Panda's Voiceover:|Voiceover:|Audio:)\s*", '', line_stripped)
            spoken = spoken.strip('"').strip()
            if spoken:
                current_text.append(spoken)
        elif line_stripped and not line_stripped.startswith('#') and not line_stripped.startswith('**') and not line_stripped.startswith('---'):
            # Clean up markdown and grab plain text that looks like narration
            clean = re.sub(r'[\*\#\[\]\(\)]', '', line_stripped).strip()
            if len(clean) > 20 and not clean.startswith('0:') and not clean.startswith('1:'):
                if current_type == 'PANDA':
                    current_text.append(clean)
    
    # Add last segment
    if current_text or current_description:
        segments.append({
            'type': current_type,
            'text': ' '.join(current_text).strip(),
            'description': ' '.join(current_description).strip()
        })
    
    # Filter out empty segments
    segments = [s for s in segments if s['text'] or s['description']]
    
    # If parsing failed / too few segments, create a single PANDA segment with full script
    if len(segments) < 2:
        # Extract all quoted speech and narration
        all_text = re.sub(r'\[.*?\]', '', script)  # remove tags
        all_text = re.sub(r'\(.*?\)', '', all_text)  # remove stage directions
        all_text = re.sub(r'[#\*]', '', all_text)    # remove markdown
        all_text = ' '.join(all_text.split())
        segments = [{'type': 'PANDA', 'text': all_text[:3000], 'description': ''}]
    
    return segments
