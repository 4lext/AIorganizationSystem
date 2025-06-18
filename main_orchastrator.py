# main_orchastrator.py
"""
Main orchestrator that coordinates all components of the system.
"""

import sys
import os
from pathlib import Path
import json
import shutil
import csv
from datetime import datetime

# Import the other components of the system
from main_audio_processor import AudioProcessor
from directory_analyzer import DirectoryAnalyzer
from ai_naming_agent import DirectoryNamingAgent

def main():
    """Main function that orchestrates the entire process."""
    if len(sys.argv) != 2:
        print("Usage: python main_orchastrator.py <directory_path>")
        print("  directory_path: Path to directory containing audio files")
        print("  DATA_HOME environment variable should be set to your DATA-HOME root path")
        print("")
        print("Example:")
        print("  # Process current directory")
        print("  python main_orchastrator.py .")
        print("")
        print("  # Process specific directory")
        print("  python main_orchastrator.py /path/to/audio/files")
        sys.exit(1)

    directory_path = sys.argv[1]

    # Get DATA-HOME from environment variable
    data_home_root = os.getenv('DATA_HOME')
    if not data_home_root:
        print("Warning: DATA_HOME environment variable not set.")
        print("Please set DATA_HOME to your DATA-HOME root directory:")
        print("  export DATA_HOME=/path/to/your/DATA-HOME")
        print("Proceeding without DATA-HOME integration...")
        data_home_root = None
    else:
        print(f"Using DATA-HOME: {data_home_root}")

    # Validate directory exists
    if not os.path.exists(directory_path):
        print(f"Error: Directory '{directory_path}' does not exist.")
        sys.exit(1)

    # Validate DATA-HOME structure exists if DATA_HOME is set
    if data_home_root:
        filetree_path = os.path.join(data_home_root, "filetree/roots")
        if not os.path.exists(filetree_path):
            print(f"Warning: DATA-HOME structure not found at '{filetree_path}'")
            print("Expected structure: DATA_HOME/filetree/roots/")
            print("Proceeding without DATA-HOME integration...")
            data_home_root = None
        else:
            print(f"✅ DATA-HOME structure validated at: {filetree_path}")

    print("🎵 Audio Processing and Directory Organization System")
    print("=" * 50)

    # Step 1: Process audio files
    print("\n📁 Step 1: Audio Detection and Transcription")
    audio_processor = AudioProcessor()
    processed_subdir = audio_processor.process_directory(directory_path)

    # Determine if we should proceed with directory analysis
    target_directory = None

    if processed_subdir:
        # Audio files were processed
        target_directory = processed_subdir
        proceed_with_analysis = prompt_user_consent(
            "\n🔍 Would you like to proceed with Step 2: Directory Analysis and AI Organization?",
            "This will analyze the directory structure and content to generate an intelligent name and optimal placement."
        )
    else:
        # No audio files found, ask if user wants to analyze directory anyway
        print(f"\nNo audio files found in {directory_path}")
        proceed_with_analysis = prompt_user_consent(
            "\n🔍 Would you like to analyze and organize this directory anyway?",
            "This will analyze the existing directory structure and content to generate an intelligent name and optimal placement."
        )
        if proceed_with_analysis:
            target_directory = Path(directory_path)

    if not proceed_with_analysis:
        print("Directory analysis cancelled by user.")
        if processed_subdir:
            print(f"Audio processing completed. Files are located at: {processed_subdir}")
        sys.exit(0)

    if not target_directory:
        print("No target directory available for analysis.")
        sys.exit(0)

    # Step 2: Analyze directory structure
    print("\n🔍 Step 2: Directory Analysis")
    analyzer = DirectoryAnalyzer()
    analysis_data = analyzer.create_analysis_payload(target_directory)

    # Save analysis data for debugging
    analysis_file = target_directory / "analysis_data.json"
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, indent=2, ensure_ascii=False)
    print(f"Analysis data saved to: {analysis_file}")

    # Display analysis summary to user
    print(f"\n📊 Analysis Summary:")
    print(f"  • Files analyzed: {analysis_data['analysis_metadata']['total_files_analyzed']}")
    print(f"  • Directory depth: {analysis_data['analysis_metadata']['max_depth']}")
    print(f"  • Target directory: {target_directory}")

    # Ask for consent to proceed with AI naming
    proceed_with_naming = prompt_user_consent(
        "\n🤖 Would you like to proceed with Step 3: AI-Powered Directory Naming?",
        "This will use AI to generate an intelligent directory name based on the analysis."
    )

    if not proceed_with_naming:
        print("AI naming cancelled by user.")
        print(f"Analysis complete. Directory remains at: {target_directory}")
        sys.exit(0)

    # Step 3: Generate intelligent directory name
    print("\n🤖 Step 3: AI-Powered Directory Naming")

    # Check if Anthropic API key is available
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("Warning: ANTHROPIC_API_KEY not found in environment variables.")
        print("Please set your Anthropic API key to use AI naming features.")
        print("Using fallback naming method...")

    naming_agent = DirectoryNamingAgent(api_key)

    # Generate session ID for A/B testing tracking
    session_id = generate_session_id()
    had_audio_files = bool(processed_subdir)

    # Create analysis summary for logging
    analysis_summary = {
        'total_files_analyzed': analysis_data['analysis_metadata']['total_files_analyzed'],
        'had_audio_files': had_audio_files
    }

    # Retry loop for directory naming
    max_retries = 3
    retry_count = 0
    feedback_history = []
    current_analysis_data = analysis_data  # Keep track of current analysis

    while retry_count <= max_retries:
        if data_home_root:
            # Generate name and determine optimal placement
            # Pass the original directory path for source-based routing rules
            if retry_count == 0:
                # First attempt - no feedback, use initial analysis
                new_directory_name, optimal_parent_path = naming_agent.generate_directory_name_and_path(
                    current_analysis_data, data_home_root, source_path=directory_path
                )
            else:
                # Retry with feedback - create new analysis focusing on file endings
                print(f"🔄 Retry attempt {retry_count}/{max_retries} - Re-analyzing with different approach...")
                current_analysis_data = analyzer.create_retry_analysis_payload(target_directory)

                # Save retry analysis data for debugging
                retry_analysis_file = target_directory / f"retry_analysis_data_{retry_count}.json"
                with open(retry_analysis_file, 'w', encoding='utf-8') as f:
                    json.dump(current_analysis_data, f, indent=2, ensure_ascii=False)
                print(f"Retry analysis data saved to: {retry_analysis_file}")

                combined_feedback = " | ".join(feedback_history)
                new_directory_name, optimal_parent_path = naming_agent.generate_directory_name_and_path_with_feedback(
                    current_analysis_data, data_home_root, source_path=directory_path, feedback=combined_feedback
                )
        else:
            # Fallback to original behavior without DATA-HOME integration
            if retry_count == 0:
                new_directory_name = naming_agent.generate_directory_name(current_analysis_data)
            else:
                # Retry with new analysis of file endings
                print(f"🔄 Retry attempt {retry_count}/{max_retries} - Re-analyzing with different approach...")
                current_analysis_data = analyzer.create_retry_analysis_payload(target_directory)

                combined_feedback = " | ".join(feedback_history)
                new_directory_name = naming_agent.generate_directory_name_with_feedback(current_analysis_data, feedback=combined_feedback)
            optimal_parent_path = None

        if not new_directory_name:
            # Log failed generation
            log_naming_attempt(
                session_id=session_id,
                attempt_number=retry_count + 1,
                source_path=directory_path,
                generated_name="",
                optimal_parent=optimal_parent_path or "",
                user_action="generation_failed",
                feedback="",
                analysis_summary=analysis_summary
            )
            print("Failed to generate directory name")
            break

        # Show the generated name and path
        print(f"\n📝 Generated directory name: {new_directory_name}")
        if optimal_parent_path:
            print(f"📂 Optimal parent directory: {optimal_parent_path}")

        # Show analysis type for user awareness
        extraction_type = current_analysis_data['analysis_metadata'].get('extraction_type', 'beginning_of_files')
        if retry_count > 0:
            print(f"📊 Analysis focus: {extraction_type} (snippet length: {current_analysis_data['analysis_metadata']['snippet_max_length']} chars)")

        # Ask user if they're satisfied with the name
        user_choice = prompt_user_naming_satisfaction()

        if user_choice == "accept":
            # Log accepted attempt
            log_naming_attempt(
                session_id=session_id,
                attempt_number=retry_count + 1,
                source_path=directory_path,
                generated_name=new_directory_name,
                optimal_parent=optimal_parent_path or "",
                user_action="accept",
                feedback="",
                analysis_summary=analysis_summary
            )
            break
        elif user_choice == "retry" and retry_count < max_retries:
            # Collect feedback
            feedback = collect_user_feedback(new_directory_name, optimal_parent_path)
            feedback_history.append(feedback)

            # Log retry attempt with feedback
            log_naming_attempt(
                session_id=session_id,
                attempt_number=retry_count + 1,
                source_path=directory_path,
                generated_name=new_directory_name,
                optimal_parent=optimal_parent_path or "",
                user_action="retry",
                feedback=feedback,
                analysis_summary=analysis_summary
            )

            retry_count += 1
        else:
            if retry_count >= max_retries:
                print(f"Maximum retry attempts ({max_retries}) reached. Using current name.")
                # Log max retries reached
                log_naming_attempt(
                    session_id=session_id,
                    attempt_number=retry_count + 1,
                    source_path=directory_path,
                    generated_name=new_directory_name,
                    optimal_parent=optimal_parent_path or "",
                    user_action="max_retries_reached",
                    feedback="",
                    analysis_summary=analysis_summary
                )
            else:
                # Log cancellation
                log_naming_attempt(
                    session_id=session_id,
                    attempt_number=retry_count + 1,
                    source_path=directory_path,
                    generated_name=new_directory_name,
                    optimal_parent=optimal_parent_path or "",
                    user_action="cancel",
                    feedback="",
                    analysis_summary=analysis_summary
                )
            break

    # Continue with the final name choice
    if new_directory_name:
        if data_home_root and optimal_parent_path:
            # Show preview of final path
            final_path = Path(optimal_parent_path) / new_directory_name

            # Check for naming conflicts and show final name
            counter = 1
            original_new_name = new_directory_name
            temp_final_path = final_path
            while temp_final_path.exists():
                conflict_name = f"{original_new_name}{counter}"
                temp_final_path = Path(optimal_parent_path) / conflict_name
                counter += 1

            if counter > 1:
                print(f"⚠️  Conflict detected. Final name will be: {temp_final_path.name}")
                final_path = temp_final_path
                new_directory_name = temp_final_path.name

            # Ask for final consent to move/rename
            proceed_with_move = prompt_user_consent(
                f"\n📦 Would you like to move and rename the directory?",
                f"This will move '{target_directory}' to '{final_path}'"
            )

            if not proceed_with_move:
                print("Directory move cancelled by user.")
                print(f"Directory remains at: {target_directory}")
                sys.exit(0)

            # NOW perform the actual operations after consent
            try:
                # Ensure parent directory exists
                print(f"Creating parent directory: {optimal_parent_path}")
                os.makedirs(optimal_parent_path, exist_ok=True)

                # Move the directory
                print(f"Moving directory from {target_directory} to {final_path}")
                shutil.move(str(target_directory), str(final_path))
                print(f"✅ Directory moved to optimal location: {final_path}")
                final_location = final_path

                # Log successful move
                log_naming_attempt(
                    session_id=session_id,
                    attempt_number=retry_count + 1,
                    source_path=directory_path,
                    generated_name=new_directory_name,
                    optimal_parent=optimal_parent_path,
                    user_action="moved_successfully",
                    final_destination=str(final_path),
                    analysis_summary=analysis_summary
                )
            except Exception as e:
                print(f"Error moving directory to optimal location: {e}")
                print("Falling back to local rename...")

                # Log move failure
                log_naming_attempt(
                    session_id=session_id,
                    attempt_number=retry_count + 1,
                    source_path=directory_path,
                    generated_name=new_directory_name,
                    optimal_parent=optimal_parent_path,
                    user_action="move_failed",
                    feedback=f"Move error: {str(e)}",
                    analysis_summary=analysis_summary
                )

                # Fallback to local rename
                parent_dir = target_directory.parent
                new_path = parent_dir / new_directory_name
                try:
                    target_directory.rename(new_path)
                    print(f"✅ Directory renamed locally: {new_path}")
                    final_location = new_path

                    # Log successful local rename
                    log_naming_attempt(
                        session_id=session_id,
                        attempt_number=retry_count + 1,
                        source_path=directory_path,
                        generated_name=new_directory_name,
                        optimal_parent="local_fallback",
                        user_action="local_rename_success",
                        final_destination=str(new_path),
                        analysis_summary=analysis_summary
                    )
                except Exception as e2:
                    print(f"Error with local rename: {e2}")
                    final_location = target_directory

                    # Log total failure
                    log_naming_attempt(
                        session_id=session_id,
                        attempt_number=retry_count + 1,
                        source_path=directory_path,
                        generated_name=new_directory_name,
                        optimal_parent="local_fallback",
                        user_action="total_failure",
                        feedback=f"Local rename error: {str(e2)}",
                        final_destination=str(target_directory),
                        analysis_summary=analysis_summary
                    )
        else:
            # Local rename without DATA-HOME integration
            # Check for naming conflicts and show final name
            parent_dir = target_directory.parent
            new_path = parent_dir / new_directory_name
            counter = 1
            original_new_name = new_directory_name
            temp_new_path = new_path
            while temp_new_path.exists():
                conflict_name = f"{original_new_name}{counter}"
                temp_new_path = parent_dir / conflict_name
                counter += 1

            if counter > 1:
                print(f"⚠️  Conflict detected. Final name will be: {temp_new_path.name}")
                new_path = temp_new_path
                new_directory_name = temp_new_path.name

            # Ask for consent to rename locally
            proceed_with_rename = prompt_user_consent(
                f"\n📝 Would you like to rename the directory?",
                f"This will rename '{target_directory.name}' to '{new_directory_name}'"
            )

            if not proceed_with_rename:
                print("Directory rename cancelled by user.")
                print(f"Directory remains at: {target_directory}")
                sys.exit(0)

            # NOW perform the actual rename after consent
            try:
                print(f"Renaming directory from {target_directory} to {new_path}")
                target_directory.rename(new_path)
                print(f"✅ Directory renamed to: {new_path}")
                final_location = new_path

                # Log successful local rename
                log_naming_attempt(
                    session_id=session_id,
                    attempt_number=retry_count + 1,
                    source_path=directory_path,
                    generated_name=new_directory_name,
                    optimal_parent="no_data_home",
                    user_action="local_rename_success",
                    final_destination=str(new_path),
                    analysis_summary=analysis_summary
                )
            except Exception as e:
                print(f"Error renaming directory: {e}")
                final_location = target_directory

                # Log rename failure
                log_naming_attempt(
                    session_id=session_id,
                    attempt_number=retry_count + 1,
                    source_path=directory_path,
                    generated_name=new_directory_name,
                    optimal_parent="no_data_home",
                    user_action="rename_failed",
                    feedback=f"Rename error: {str(e)}",
                    final_destination=str(target_directory),
                    analysis_summary=analysis_summary
                )
    else:
        print("Failed to generate directory name")
        final_location = target_directory

    print("\n🎉 Processing complete!")
    print(f"Final location: {final_location}")

    # Display organization summary
    if data_home_root and 'optimal_parent_path' in locals():
        relative_path = os.path.relpath(str(final_location), data_home_root)
        print(f"DATA-HOME relative path: {relative_path}")
        print(f"Taxonomical classification: {new_directory_name if 'new_directory_name' in locals() else 'default'}")

    # Mention A/B testing log
    script_dir = Path(__file__).parent
    log_file = script_dir / "naming_ab_testing_log.csv"
    print(f"\n📊 Session data logged to: {log_file}")
    print(f"   Session ID: {session_id}")
    if retry_count > 0:
        print(f"   Total attempts: {retry_count + 1}")
        print(f"   Feedback provided: {len(feedback_history)} times")


def log_naming_attempt(session_id: str, attempt_number: int, source_path: str, generated_name: str,
                      optimal_parent: str, user_action: str, feedback: str = "",
                      final_destination: str = "", analysis_summary: dict = None):
    """Log naming attempt data to CSV for A/B testing analysis."""

    # Get the directory where the script is located
    script_dir = Path(__file__).parent
    log_file = script_dir / "naming_ab_testing_log.csv"

    # Prepare log data
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'session_id': session_id,
        'attempt_number': attempt_number,
        'source_path': source_path,
        'generated_name': generated_name,
        'generated_name_length': len(generated_name) if generated_name else 0,
        'optimal_parent_path': optimal_parent or "",
        'user_action': user_action,  # 'accept', 'retry', 'cancel'
        'user_feedback': feedback,
        'final_destination': final_destination,
        'files_analyzed': analysis_summary.get('total_files_analyzed', 0) if analysis_summary else 0,
        'has_audio_files': 'yes' if analysis_summary and analysis_summary.get('had_audio_files', False) else 'no',
        'source_is_news_transcript': 'yes' if 'News/transcripts' in source_path else 'no',
        'content_type_prefix': generated_name[:4] if generated_name and len(generated_name) >= 4 else "",
        'feedback_length': len(feedback) if feedback else 0,
        'feedback_categories': categorize_feedback(feedback) if feedback else ""
    }

    # Create CSV with headers if it doesn't exist
    file_exists = log_file.exists()

    with open(log_file, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = log_entry.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header if file is new
        if not file_exists:
            writer.writeheader()
            print(f"📊 Created A/B testing log: {log_file}")

        # Write the log entry
        writer.writerow(log_entry)


def categorize_feedback(feedback: str) -> str:
    """Categorize user feedback into standardized categories for analysis."""
    if not feedback:
        return ""

    feedback_lower = feedback.lower()
    categories = []

    # Content specificity
    if any(word in feedback_lower for word in ['generic', 'specific', 'vague', 'unclear']):
        categories.append('specificity')

    # Length concerns
    if any(word in feedback_lower for word in ['long', 'short', 'length', 'brief', 'verbose']):
        categories.append('length')

    # Location/path concerns
    if any(word in feedback_lower for word in ['location', 'directory', 'path', 'folder', 'place']):
        categories.append('location')

    # Content focus
    if any(word in feedback_lower for word in ['topic', 'subject', 'focus', 'about', 'theme']):
        categories.append('content_focus')

    # Abbreviation concerns
    if any(word in feedback_lower for word in ['abbreviation', 'abbrev', 'short', 'expand']):
        categories.append('abbreviations')

    # Missing information
    if any(word in feedback_lower for word in ['missing', 'include', 'add', 'mention']):
        categories.append('missing_info')

    # Context concerns
    if any(word in feedback_lower for word in ['context', 'background', 'situation']):
        categories.append('context')

    return '|'.join(categories) if categories else 'other'


def generate_session_id() -> str:
    """Generate a unique session ID for tracking related attempts."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def prompt_user_naming_satisfaction() -> str:
    """Ask user if they're satisfied with the generated name."""
    print("\n🤔 How do you feel about this directory name and location?")
    print("  1. ✅ Accept - I like this name and location")
    print("  2. 🔄 Try again - I'd like a different name")

    while True:
        response = input("\nChoose option (1 or 2): ").strip()
        if response == "1":
            return "accept"
        elif response == "2":
            return "retry"
        else:
            print("Please enter '1' to accept or '2' to try again.")


def collect_user_feedback(directory_name: str, parent_path: str = None) -> str:
    """Collect specific feedback about what the user didn't like."""
    print(f"\n💬 What didn't you like about the name '{directory_name}'?")
    if parent_path:
        print(f"   or the location '{parent_path}'?")

    print("\nPlease be specific about what you'd like changed:")
    print("  • Too generic? (suggest more specific terms)")
    print("  • Wrong focus? (mention what should be emphasized)")
    print("  • Poor location? (suggest better parent directory)")
    print("  • Missing context? (what information should be included)")
    print("  • Too long/short? (preferred length)")
    print("  • Wrong abbreviations? (suggest alternatives)")

    feedback = input("\nYour feedback: ").strip()

    if not feedback:
        return "Please make the name more specific and descriptive"

    return feedback


def prompt_user_consent(question: str, description: str = "") -> bool:
    """Prompt user for consent with a clear question and optional description."""
    print(question)
    if description:
        print(f"  {description}")

    while True:
        response = input("\nProceed? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")

if __name__ == "__main__":
    main()
