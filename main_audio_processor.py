# main_audio_processor.py
"""
Main audio processing script that detects audio files, handles transcription,
and coordinates with the directory analysis system.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional, Tuple
import whisper
import json
from datetime import datetime

class AudioProcessor:
    def __init__(self, whisper_model_size: str = "base"):
        """Initialize the audio processor with Whisper model."""
        self.audio_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.aac', '.ogg', '.wma'}
        self.whisper_model = whisper.load_model(whisper_model_size)

    def detect_audio_files(self, directory: str) -> List[Path]:
        """Detect all audio files in the given directory."""
        directory_path = Path(directory)
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory {directory} does not exist")

        audio_files = []
        for file_path in directory_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.audio_extensions:
                audio_files.append(file_path)

        return audio_files

    def prompt_user_for_transcription(self, audio_files: List[Path]) -> bool:
        """Prompt user whether to proceed with transcription."""
        if not audio_files:
            print("No audio files found in the directory.")
            return False

        print(f"Found {len(audio_files)} audio file(s):")
        for audio_file in audio_files:
            print(f"  - {audio_file.name}")

        while True:
            response = input("\nWould you like to run transcription on these files? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")

    def create_subdirectory(self, parent_dir: Path, subdir_name: str = "transcribed_audio") -> Path:
        """Create a subdirectory for processed files."""
        subdir_path = parent_dir / subdir_name
        subdir_path.mkdir(exist_ok=True)
        return subdir_path

    def transcribe_audio(self, audio_file: Path) -> str:
        """Transcribe audio file using Whisper."""
        print(f"Transcribing {audio_file.name}...")
        try:
            result = self.whisper_model.transcribe(str(audio_file))
            return result["text"]
        except Exception as e:
            print(f"Error transcribing {audio_file.name}: {e}")
            return ""

    def save_transcription(self, transcription: str, output_path: Path) -> None:
        """Save transcription to text file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(transcription)

    def move_audio_file(self, audio_file: Path, destination_dir: Path) -> None:
        """Move audio file to destination directory."""
        destination_path = destination_dir / audio_file.name
        shutil.move(str(audio_file), str(destination_path))

    def process_directory(self, directory: str) -> Optional[Path]:
        """Main processing function for a directory."""
        try:
            # Step 1: Detect audio files
            audio_files = self.detect_audio_files(directory)

            if not audio_files:
                print(f"No audio files found in {directory}")
                return None

            # Step 2: Prompt user
            if not self.prompt_user_for_transcription(audio_files):
                print("Transcription cancelled by user.")
                return None

            # Step 3: Create subdirectory
            parent_dir = Path(directory)
            subdir = self.create_subdirectory(parent_dir)

            # Step 4: Process each audio file
            for audio_file in audio_files:
                # Transcribe
                transcription = self.transcribe_audio(audio_file)

                if transcription:
                    # Save transcription
                    transcript_filename = f"{audio_file.stem}_transcript.txt"
                    transcript_path = subdir / transcript_filename
                    self.save_transcription(transcription, transcript_path)
                    print(f"Saved transcription: {transcript_path}")

                # Move original audio file
                self.move_audio_file(audio_file, subdir)
                print(f"Moved audio file: {audio_file.name}")

            print(f"\nProcessing complete. Files moved to: {subdir}")
            return subdir

        except Exception as e:
            print(f"Error processing directory: {e}")
            return None
