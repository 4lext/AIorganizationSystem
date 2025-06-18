# setup_instructions.md
"""
# Audio Processing and Directory Organization System

## Setup Instructions

1. Install required packages:
   ```bash
   pip install openai-whisper anthropic
   ```

2. Set up Anthropic API key (optional, for AI naming):
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

3. Run the system:
   ```bash
   python main_orchestrator.py /path/to/your/directory
   ```

## System Architecture

The system consists of several interconnected components:

1. **AudioProcessor**: Detects and transcribes audio files
2. **DirectoryAnalyzer**: Creates file tree snapshots and extracts text snippets  
3. **DirectoryNamingAgent**: Uses AI to generate contextual directory names
4. **Main Orchestrator**: Coordinates all components

## Taxonomical Naming Structure

The system uses a structured taxonomy for consistent naming:

- **Content Types**: aud (audio), trans (transcription), doc (documentation), etc.
- **Context Indicators**: mtg (meeting), proj (project), res (research), etc.  
- **Temporal Markers**: day (daily), wk (weekly), curr (current), etc.

## Example Usage

Input directory with audio files → Transcription → Analysis → AI naming → Organized output

Example output directory names:
- `audTransMtgQ42024` (Audio transcription from Q4 2024 meeting)
- `resProjInterviews` (Research project interviews)
- `lectureSeries2024` (Lecture series from 2024)
"""
