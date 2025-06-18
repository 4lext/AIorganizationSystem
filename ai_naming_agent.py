# ai_naming_agent.py
"""
AI agent for generating contextual directory names based on file analysis.
"""

import anthropic
import json
import os
from typing import Dict, Optional
import re

class DirectoryNamingAgent:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the AI naming agent."""
        self.client = None
        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)

        # Enhanced taxonomical structure for naming convention and DATA-HOME integration
        self.naming_taxonomy = {
            "content_types": {
                "audio": "aud",
                "transcription": "trans",
                "documentation": "doc",
                "code": "code",
                "data": "data",
                "media": "media",
                "archive": "arch",
                "image": "img",
                "video": "vid",
                "literature": "lit",
                "game": "game",
                "software": "soft"
            },
            "context_indicators": {
                # Professional contexts
                "meeting": "mtg",
                "interview": "intv",
                "presentation": "pres",
                "lecture": "lect",
                "conference": "conf",
                "research": "res",
                "project": "proj",
                "client": "cli",
                "contract": "contr",
                "certification": "cert",
                "correspondence": "corr",
                "upwork": "upw",
                "strategy": "strat",
                "politics": "pol",

                # Personal contexts
                "personal": "pers",
                "financial": "fin",
                "medical": "med",
                "identity": "id",
                "family": "fam",
                "friends": "frnd",

                # Content types
                "podcast": "pod",
                "recording": "rec",
                "music": "mus",
                "book": "book",
                "movie": "mov",
                "show": "show",
                "anime": "ani",
                "news": "news",
                "scientific": "sci",
                "educational": "edu",
                "entertainment": "ent",

                # Technical contexts
                "backup": "bkup",
                "dump": "dump",
                "template": "tmpl",
                "experiment": "exp",
                "library": "lib",
                "tool": "tool",
                "configuration": "cfg",
                "development": "dev",
                "system": "sys"
            },
            "temporal_markers": {
                "daily": "day",
                "weekly": "wk",
                "monthly": "mon",
                "quarterly": "qtr",
                "yearly": "yr",
                "historical": "hist",
                "current": "curr",
                "recent": "rec",
                "ongoing": "ong"
            },
            "quality_indicators": {
                "draft": "drft",
                "final": "fin",
                "review": "rev",
                "approved": "appr",
                "archived": "arch",
                "working": "wip"
            }
        }

        # DATA-HOME directory mapping for optimal placement
        self.data_home_mapping = {
            # Audio content mappings
            "aud": {
                "primary_path": "audio",
                "context_mappings": {
                    "book": "audio/books",
                    "mus": "audio/music",
                    "pod": "audio/podcasts",
                    "rec": "audio/recordings",
                    "game": "audio/soundtracks/games",
                    "mov": "audio/soundtracks/movies",
                    "show": "audio/soundtracks/television"
                }
            },

            # Transcription mappings
            "trans": {
                "primary_path": "documents/Text Documents",  # Default for transcripts
                "context_mappings": {
                    "mtg": "documents/professional",
                    "intv": "documents/professional",
                    "res": "documents/professional",
                    "pers": "documents/personal",
                    "fin": "documents/personal/financial",
                    "med": "documents/personal/medical",
                    "news": "documents/Text Documents"  # News transcripts go to Text Documents
                }
            },

            # Documentation mappings
            "doc": {
                "primary_path": "documents",
                "context_mappings": {
                    "tmpl": "documents/_templates",
                    "contr": "documents/professional/contracts",
                    "cert": "documents/professional/certifications",
                    "corr": "documents/professional/correspondence",
                    "upw": "documents/professional/upwork",
                    "strat": "documents/professional/strategicAgent",
                    "pol": "documents/professional/StrategyPolitics",
                    "fin": "documents/personal/financial",
                    "med": "documents/personal/medical",
                    "id": "documents/personal/identity"
                }
            },

            # Code/Software mappings
            "code": {
                "primary_path": "software",
                "context_mappings": {
                    "exp": "software/development/experiments",
                    "lib": "software/development/libraries",
                    "tool": "software/development/tools",
                    "cfg": "software/configurations"
                }
            },

            # Media mappings
            "media": {
                "primary_path": "images",  # Default to images for mixed media
                "context_mappings": {
                    "vid": "video",
                    "img": "images",
                    "chart": "images/charts",
                    "screenshot": "images/screenshots"
                }
            },

            # Archive mappings
            "arch": {
                "primary_path": "archives",
                "context_mappings": {
                    "bkup": "archives/backups",
                    "dump": "archives/dumps",
                    "news": "archives/news",
                    "sci": "archives/scientific",
                    "data": "archives/datasets"
                }
            }
        }

    def determine_optimal_parent_directory(self, directory_name: str, data_home_root: str, source_path: str = None) -> str:
        """Determine the optimal parent directory in DATA-HOME structure."""

        # Special rule: If source is from ~/News/transcripts/, always go to documents/Text Documents
        if source_path:
            normalized_source = str(source_path).replace("\\", "/")
            if "News/transcripts" in normalized_source or "/News/transcripts" in normalized_source:
                print(f"🗞️  Detected News transcript source - routing to Text Documents")
                return os.path.join(data_home_root, "filetree/roots/documents/Text Documents")

        # Extract content type from directory name (first part before any capitals)
        content_type_match = re.match(r'^([a-z]+)', directory_name)
        if not content_type_match:
            return os.path.join(data_home_root, "filetree/roots/documents")  # Default fallback

        content_type = content_type_match.group(1)

        # Get mapping for this content type
        if content_type not in self.data_home_mapping:
            return os.path.join(data_home_root, "filetree/roots/documents")  # Default fallback

        mapping = self.data_home_mapping[content_type]

        # Check for more specific context mappings
        for context_abbrev, context_path in mapping["context_mappings"].items():
            if context_abbrev in directory_name.lower():
                return os.path.join(data_home_root, "filetree/roots", context_path)

        # Use primary path if no specific context found
        return os.path.join(data_home_root, "filetree/roots", mapping["primary_path"])

    def create_naming_prompt(self, analysis_data: Dict) -> str:
        """Create the enhanced prompt for the AI naming agent."""

        taxonomy_info = json.dumps(self.naming_taxonomy, indent=2)

        prompt = f"""You are a specialized directory naming agent that creates highly descriptive, content-specific directory names. Your task is to analyze the provided file structure and content snippets to generate a precise, meaningful directory name that captures the actual subject matter and context.

NAMING REQUIREMENTS:
1. Use camelCase syntax (e.g., transNewsIndPakEscalationAnalysis)
2. Maximum 75 characters (increased from 40 for better specificity)
3. Start with content type abbreviation, then focus on SPECIFIC CONTENT
4. Be highly descriptive about the actual subject matter, topics, or themes
5. Prioritize clarity and searchability over brevity
6. Include actual topics, names, concepts, or themes found in the content

ENHANCED TAXONOMICAL STRUCTURE:
{taxonomy_info}

NAMING PATTERN GUIDELINES:
- Start with primary content type abbreviation (e.g., "trans", "aud", "doc")
- Follow with SPECIFIC CONTENT DESCRIPTORS rather than generic context
- Include actual subject matter: topics, themes, people, organizations, concepts
- Add temporal markers only when they add meaningful context
- Avoid overly generic abbreviations - be specific about what the content actually discusses

EXAMPLES OF PREFERRED NAMING PATTERNS:
✅ GOOD (Specific and descriptive):
- transNewsIndPakEscalationAnalysis (transcription about India-Pakistan escalation)
- audPodClimateChangePolicy2024 (audio podcast about climate change policy)
- docContractAcmeCorpServiceAgreement (contract document with Acme Corp)
- transInterviewAIEthicsResearch (interview transcription about AI ethics research)
- audMtgQuarterlyBudgetReview (audio meeting about quarterly budget review)

❌ AVOID (Too generic or abbreviated):
- audTransNewsRecPod (unclear what news topic)
- audTransMtgStrategy2024 (unclear what strategy)
- docProfessionalStuff (no specific content)
- transGenericMeeting (no topic specified)

CONTENT ANALYSIS FOCUS:
Look for and prioritize these specific elements in the content:
- Actual topics, subjects, or themes discussed
- Names of people, organizations, or entities mentioned
- Specific concepts, policies, or issues addressed
- Technical terms or domain-specific language
- Geographic locations or regions mentioned
- Project names or initiative titles

ANALYSIS DATA:
Directory Path: {analysis_data['directory_path']}

File Tree Structure:
{json.dumps(analysis_data['file_tree'], indent=2)}

Text Snippets from Files:
{json.dumps(analysis_data['text_snippets'], indent=2)}

Analysis Metadata:
{json.dumps(analysis_data['analysis_metadata'], indent=2)}

Based on this comprehensive analysis, generate ONLY the directory name (no explanation, no additional text). The name should:
1. Start with the appropriate content type abbreviation
2. Capture the SPECIFIC subject matter, topics, or themes from the actual content
3. Be descriptive enough that someone could understand what the directory contains
4. Use meaningful words rather than generic abbreviations
5. Follow camelCase with clear, searchable terminology

Focus on what the content is actually ABOUT, not just generic categories.

Directory Name:"""

        return prompt

    def create_naming_prompt_with_feedback(self, analysis_data: Dict, feedback: str = None) -> str:
        """Create the enhanced prompt with optional user feedback."""

        taxonomy_info = json.dumps(self.naming_taxonomy, indent=2)

        # Base prompt
        prompt = f"""You are a specialized directory naming agent that creates highly descriptive, content-specific directory names. Your task is to analyze the provided file structure and content snippets to generate a precise, meaningful directory name that captures the actual subject matter and context.

NAMING REQUIREMENTS:
1. Use camelCase syntax (e.g., transNewsIndPakEscalationAnalysis)
2. Maximum 75 characters (increased from 40 for better specificity)
3. Start with content type abbreviation, then focus on SPECIFIC CONTENT
4. Be highly descriptive about the actual subject matter, topics, or themes
5. Prioritize clarity and searchability over brevity
6. Include actual topics, names, concepts, or themes found in the content

ENHANCED TAXONOMICAL STRUCTURE:
{taxonomy_info}

NAMING PATTERN GUIDELINES:
- Start with primary content type abbreviation (e.g., "trans", "aud", "doc")
- Follow with SPECIFIC CONTENT DESCRIPTORS rather than generic context
- Include actual subject matter: topics, themes, people, organizations, concepts
- Add temporal markers only when they add meaningful context
- Avoid overly generic abbreviations - be specific about what the content actually discusses

EXAMPLES OF PREFERRED NAMING PATTERNS:
✅ GOOD (Specific and descriptive):
- transNewsIndPakEscalationAnalysis (transcription about India-Pakistan escalation)
- audPodClimateChangePolicy2024 (audio podcast about climate change policy)
- docContractAcmeCorpServiceAgreement (contract document with Acme Corp)
- transInterviewAIEthicsResearch (interview transcription about AI ethics research)
- audMtgQuarterlyBudgetReview (audio meeting about quarterly budget review)

❌ AVOID (Too generic or abbreviated):
- audTransNewsRecPod (unclear what news topic)
- audTransMtgStrategy2024 (unclear what strategy)
- docProfessionalStuff (no specific content)
- transGenericMeeting (no topic specified)

CONTENT ANALYSIS FOCUS:
Look for and prioritize these specific elements in the content:
- Actual topics, subjects, or themes discussed
- Names of people, organizations, or entities mentioned
- Specific concepts, policies, or issues addressed
- Technical terms or domain-specific language
- Geographic locations or regions mentioned
- Project names or initiative titles"""

        # Add user feedback section if provided
        if feedback:
            prompt += f"""

🔄 USER FEEDBACK FROM PREVIOUS ATTEMPT:
{feedback}

IMPORTANT: Take this feedback seriously and adjust your naming approach accordingly. If the user didn't like something specific about the previous name or directory placement, make sure to address their concerns in this new attempt."""

        prompt += f"""

ANALYSIS DATA:
Directory Path: {analysis_data['directory_path']}

File Tree Structure:
{json.dumps(analysis_data['file_tree'], indent=2)}

Text Snippets from Files:
{json.dumps(analysis_data['text_snippets'], indent=2)}

Analysis Metadata:
{json.dumps(analysis_data['analysis_metadata'], indent=2)}

Based on this comprehensive analysis{"" if not feedback else " and the user feedback above"}, generate ONLY the directory name (no explanation, no additional text). The name should:
1. Start with the appropriate content type abbreviation
2. Capture the SPECIFIC subject matter, topics, or themes from the actual content
3. Be descriptive enough that someone could understand what the directory contains
4. Use meaningful words rather than generic abbreviations
5. Follow camelCase with clear, searchable terminology
{"6. Address the user's feedback and concerns from the previous attempt" if feedback else ""}

Focus on what the content is actually ABOUT, not just generic categories.

Directory Name:"""

        return prompt

    def generate_directory_name(self, analysis_data: Dict, model: str = "claude-3-haiku-20240307") -> Optional[str]:
        """Generate directory name using AI analysis."""
        try:
            if not self.client:
                print("No Anthropic API client available. Using fallback naming.")
                return self.create_fallback_name(analysis_data)

            prompt = self.create_naming_prompt(analysis_data)

            response = self.client.messages.create(
                model=model,
                max_tokens=75,
                temperature=0.3,
                system="You are a specialized directory naming agent. Respond only with the requested directory name, nothing else.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            generated_name = response.content[0].text.strip()

            # Validate the generated name
            if self.validate_directory_name(generated_name):
                return generated_name
            else:
                return self.create_fallback_name(analysis_data)

        except Exception as e:
            print(f"Error generating directory name: {e}")
            return self.create_fallback_name(analysis_data)

    def generate_directory_name_with_feedback(self, analysis_data: Dict, feedback: str = None, model: str = "claude-3-haiku-20240307") -> Optional[str]:
        """Generate directory name using AI analysis with optional user feedback."""
        try:
            if not self.client:
                print("No Anthropic API client available. Using fallback naming.")
                return self.create_fallback_name(analysis_data)

            prompt = self.create_naming_prompt_with_feedback(analysis_data, feedback)

            response = self.client.messages.create(
                model=model,
                max_tokens=75,
                temperature=0.3,
                system="You are a specialized directory naming agent. Respond only with the requested directory name, nothing else.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            generated_name = response.content[0].text.strip()

            # Validate the generated name
            if self.validate_directory_name(generated_name):
                return generated_name
            else:
                return self.create_fallback_name(analysis_data)

        except Exception as e:
            print(f"Error generating directory name: {e}")
            return self.create_fallback_name(analysis_data)

    def generate_directory_name_and_path(self, analysis_data: Dict, data_home_root: str, source_path: str = None, model: str = "claude-3-haiku-20240307") -> tuple[Optional[str], Optional[str]]:
        """Generate directory name and determine optimal parent path."""
        return self.generate_directory_name_and_path_with_feedback(analysis_data, data_home_root, source_path, feedback=None, model=model)

    def generate_directory_name_and_path_with_feedback(self, analysis_data: Dict, data_home_root: str, source_path: str = None, feedback: str = None, model: str = "claude-3-haiku-20240307") -> tuple[Optional[str], Optional[str]]:
        """Generate directory name and determine optimal parent path with optional feedback."""
        directory_name = self.generate_directory_name_with_feedback(analysis_data, feedback, model)
        if not directory_name:
            return None, None

        optimal_parent = self.determine_optimal_parent_directory(directory_name, data_home_root, source_path)
        return directory_name, optimal_parent

    def validate_directory_name(self, name: str) -> bool:
        """Validate that the generated name meets requirements."""
        # Check length (increased to 75 characters)
        if len(name) > 75:
            return False

        # Check camelCase pattern (starts with lowercase, contains only alphanumeric)
        if not re.match(r'^[a-z][a-zA-Z0-9]*$', name):
            return False

        return True

    def create_fallback_name(self, analysis_data: Dict) -> str:
        """Create a fallback name if AI generation fails."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"processedAudio{timestamp}"
