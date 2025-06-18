# A/B Testing Data Collection for AI Fine-Tuning

## CSV Log File Structure

The system automatically logs all naming attempts to `naming_ab_testing_log.csv` in the program directory. This data can be used for fine-tuning the AI naming agent or analyzing user preferences.

### CSV Columns

| Column | Description | Example Values |
|--------|-------------|----------------|
| `timestamp` | When the attempt occurred | `2024-06-18T14:30:25.123456` |
| `session_id` | Unique ID for related attempts | `20240618_143025` |
| `attempt_number` | Which attempt in the session (1, 2, 3) | `1`, `2`, `3` |
| `source_path` | Original directory path | `/home/user/News/transcripts/audio_dir` |
| `generated_name` | AI-generated directory name | `transNewsIndPakEscalationAnalysis` |
| `generated_name_length` | Length of generated name | `33` |
| `optimal_parent_path` | AI-suggested parent directory | `/DATA-HOME/filetree/roots/documents/Text Documents` |
| `user_action` | What the user decided | `accept`, `retry`, `cancel`, `moved_successfully` |
| `user_feedback` | Specific feedback provided | `"Too generic - should mention India-Pakistan"` |
| `final_destination` | Where directory actually ended up | `/DATA-HOME/filetree/roots/documents/Text Documents/transNewsIndPakEscalationAnalysis` |
| `files_analyzed` | Number of files the AI analyzed | `5` |
| `has_audio_files` | Whether audio files were processed | `yes`, `no` |
| `source_is_news_transcript` | Special News/transcripts handling | `yes`, `no` |
| `content_type_prefix` | First 4 chars of generated name | `trans`, `aud`, `doc` |
| `feedback_length` | Length of user feedback | `45` |
| `feedback_categories` | Categorized feedback types | `specificity\|content_focus` |

### User Action Types

- **`accept`** - User accepted the generated name
- **`retry`** - User requested a different name  
- **`cancel`** - User cancelled the naming process
- **`generation_failed`** - AI failed to generate a name
- **`max_retries_reached`** - Hit the 3-attempt limit
- **`moved_successfully`** - Directory successfully moved
- **`move_failed`** - Error moving to DATA-HOME location
- **`local_rename_success`** - Successfully renamed locally
- **`rename_failed`** - Error during renaming
- **`total_failure`** - All operations failed

### Feedback Categories

The system automatically categorizes user feedback:

- **`specificity`** - Comments about being too generic/specific
- **`length`** - Comments about name length
- **`location`** - Comments about directory placement
- **`content_focus`** - Comments about topic/subject focus
- **`abbreviations`** - Comments about abbreviations used
- **`missing_info`** - Comments about missing information
- **`context`** - Comments about contextual information
- **`other`** - Uncategorized feedback

### Example Session Data

```csv
timestamp,session_id,attempt_number,source_path,generated_name,user_action,user_feedback,feedback_categories
2024-06-18T14:30:25,20240618_143025,1,/home/user/News/transcripts/audio,audTransNewsRecPod,retry,"Too generic - should mention specific topic",specificity|content_focus
2024-06-18T14:31:15,20240618_143025,2,/home/user/News/transcripts/audio,transNewsIndPakBorderDispute,retry,"Good topic but wrong location - should be in documents",location
2024-06-18T14:32:05,20240618_143025,3,/home/user/News/transcripts/audio,transNewsIndPakEscalationAnalysis,accept,"",
2024-06-18T14:32:20,20240618_143025,3,/home/user/News/transcripts/audio,transNewsIndPakEscalationAnalysis,moved_successfully,"",
```

## Usage for Fine-Tuning

This data can be used to:

1. **Identify patterns** in successful vs. rejected names
2. **Analyze feedback themes** to improve prompts
3. **Train custom models** on preferred naming patterns
4. **A/B test** different prompt strategies
5. **Optimize routing rules** for different content types
6. **Measure user satisfaction** and system effectiveness

## Data Privacy

- No file content is logged, only metadata and generated names
- Personal paths can be sanitized before sharing data
- Session IDs are timestamps, not linked to user identity
- Feedback is stored as provided by the user