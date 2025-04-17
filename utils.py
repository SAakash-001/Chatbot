import json
import random
import sqlite3
import re
import time
import os
from datetime import datetime
from typing import Tuple, Optional, Dict, List, Any

# === UTILS: Load JSON Responses ===
def load_responses(file_path: str = "responses.json") -> dict:
    """Load chatbot responses from a JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Response file '{file_path}' not found. Using fallback responses.")
        # Provide minimal fallback responses
        return {
            "General Queries": {
                "No answer found": [
                    "I'm sorry, but I'm experiencing configuration issues. Please contact support for assistance.",
                    "It seems my response database is unavailable. Please try again later or contact support."
                ]
            }
        }
    except json.JSONDecodeError:
        print(f"ERROR: Response file '{file_path}' is malformed. Using fallback responses.")
        return {
            "General Queries": {
                "No answer found": [
                    "I'm having trouble processing my knowledge base. Please contact support for assistance.",
                    "My response database appears to be corrupted. Please try again later or contact support."
                ]
            }
        }
    except Exception as e:
        print(f"Error loading responses: {e}")
        return {
            "General Queries": {
                "No answer found": [
                    "I'm currently unable to access my knowledge base. Please try again later or contact support.",
                    "I'm experiencing technical difficulties. Please try again later or contact support."
                ]
            }
        }

# Load responses once to avoid reloading repeatedly
responses_data = load_responses()

def get_random_response(category: str, sub_category: str) -> str:
    """
    Returns a randomized response for a given category and sub-category.
    
    Args:
        category (str): The main category (e.g., "Invoice Requests").
        sub_category (str): The sub-category (e.g., "Invoice not received").
        
    Returns:
        str: A random response from the list, or an error message if not found.
    """
    try:
        responses = responses_data[category][sub_category]
        return random.choice(responses)
    except KeyError:
        return "Response category not found."

def load_responses_mapping(file_path: str = "responses.json") -> dict:
    """Alias for load_responses to maintain compatibility with chatbot logic."""
    return load_responses(file_path)


# === DATABASE OPERATIONS ===
def get_invoice_details(doi: str, title: str) -> str:
    """
    Retrieve invoice details from the database using DOI and title.
    Ensures correct column names, case-insensitive matching, and strips input.
    """
    # Clean input parameters
    doi = doi.strip()
    title = title.strip()
    
    # Debug info
    print(f"Searching for invoice with DOI: '{doi}', Title: '{title}'")
    
    try:
        # Flexible search to improve matching chances
        conn = sqlite3.connect("articles.db")
        cursor = conn.cursor()
        
        # First try exact match
        query = """
        SELECT doi, title, status FROM articles WHERE doi = ? AND title = ? COLLATE NOCASE
        """
        cursor.execute(query, (doi, title))
        row = cursor.fetchone()
        
        # If no exact match, try partial title match
        if not row:
            print(f"No exact match found, trying partial match")
            query = """
            SELECT doi, title, status FROM articles 
            WHERE doi = ? AND title LIKE ? COLLATE NOCASE
            """
            cursor.execute(query, (doi, f"%{title}%"))
            row = cursor.fetchone()
        
        # If still no match, try just the DOI
        if not row:
            print(f"No partial match found, trying DOI-only match")
            query = """
            SELECT doi, title, status FROM articles WHERE doi = ?
            """
            cursor.execute(query, (doi,))
            row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return (
                f"Invoice Details for DOI `{row[0]}`\n\n"
                f"Title: {row[1]}\n\n"
                f"Invoice Status: {row[2]}"
            )
        
        return (
            f"No invoice found for the given DOI '{doi}' and article title '{title}'. "
            f"Please verify your details or contact our support team for assistance."
        )
    
    except Exception as e:
        print(f"Database Error: {e}")
        return (
            "There was an error retrieving the invoice details. "
            "This might be due to a technical issue. Please try again later or contact support."
        )


# === CHATBOT LOGIC ===
def extract_doi_and_title(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract DOI and article title from text using regex and pattern matching.
    
    Args:
        text (str): Input text containing DOI and article title
        
    Returns:
        Tuple[Optional[str], Optional[str]]: (doi, title) if found, (None, None) otherwise
    """
    # Clean input text by removing extra spaces
    text = text.strip()
    
    # Handle direct format: 'DOI', 'Title' or "DOI", "Title"
    direct_format = re.match(r'[\'\"]?(10\.\d{4,9}/[-._;()/:\w]+)[\'\"]?\s*,\s*[\'\"]?([^\'\"]+)[\'\"]?', text)
    if direct_format:
        doi = direct_format.group(1).strip()
        title = direct_format.group(2).strip()
        return doi, title
    
    # DOI pattern: matches DOI format 10.xxxx/xxxxx
    doi_pattern = r'10\.\d{4,9}/[-._;()/:\w]+'
    
    # Try to find DOI first
    doi_match = re.search(doi_pattern, text)
    if not doi_match:
        return None, None
        
    doi = doi_match.group(0)
    
    # Remove the DOI from text to focus on title
    remaining_text = text.replace(doi, '').strip()
    
    # Try to find quoted title first - highest priority as it's most reliable
    quoted_title_match = re.search(r'[\'\"](.*?)[\'\"]', remaining_text)
    if quoted_title_match:
        title = quoted_title_match.group(1).strip()
        if title:  # Ensure we don't return empty titles
            return doi, title
    
    # If no quoted title, try common patterns with careful extraction
    patterns = [
        # "titled X with DOI" pattern
        (r'titled\s+(.*?)(?:\s+with\s+DOI|\s*$)', 1),
        
        # "article/paper/publication X with DOI" pattern
        (r'(?:article|paper|publication|manuscript)\s+(.*?)(?:\s+with\s+DOI|\s*$)', 1),
        
        # "about X with DOI" pattern
        (r'about\s+(.*?)(?:\s+with\s+DOI|\s*$)', 1),
        
        # "looking for X with DOI" pattern
        (r'looking\s+for\s+(?:the\s+)?(?:article|paper|publication|manuscript)\s+(.*?)(?:\s+with\s+DOI|\s*$)', 1),
        
        # General pattern for text before "with DOI"
        (r'(.*?)\s+with\s+DOI', 1)
    ]
    
    for pattern, group in patterns:
        match = re.search(pattern, remaining_text, re.IGNORECASE)
        if match:
            title = match.group(group).strip()
            # Remove quotes if they're present
            title = re.sub(r'^[\'"]|[\'"]$', '', title)
            # Clean up title
            title = re.sub(r'\s+', ' ', title)
            if title:  # Ensure we have a non-empty title
                return doi, title
    
    # If nothing else worked, use the remaining text
    if remaining_text:
        # Clean up and remove common words/phrases
        # Remove common intro phrases
        cleaned_text = re.sub(r'^.*?(?:titled|article|paper|publication|manuscript|about)\s+', '', remaining_text, flags=re.IGNORECASE)
        # Remove "with DOI" and anything after
        cleaned_text = re.sub(r'\s+with\s+DOI.*$', '', cleaned_text, flags=re.IGNORECASE)
        # Remove quotes
        cleaned_text = re.sub(r'[\'"]', '', cleaned_text)
        # Final cleanup
        cleaned_text = cleaned_text.strip()
        
        if cleaned_text:
            return doi, cleaned_text
    
    return doi, None

# Context management for users to provide personalized responses
user_contexts: Dict[str, Dict[str, Any]] = {}

# Add satisfaction options for user feedback
SATISFACTION_OPTIONS = ["Yes, I'm satisfied", "No, I need human support"]

def initialize_user_context(user_id: str) -> None:
    """Initialize or reset a user's context with default values."""
    user_contexts[user_id] = {
        "conversation_state": None,  # Current conversation state
        "history": [],               # Previous messages
        "frustration_level": 0,      # Track frustration (0-5)
        "last_interaction": time.time(),  # Last interaction timestamp
        "doi_attempts": 0,           # Number of failed DOI extraction attempts
        "user_name": None,           # Store user name if provided
        "previous_queries": [],      # Track previous queries
        "session_start": datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Session start time
    }

def update_user_context(user_id: str, key: str, value: Any) -> None:
    """Update a specific field in the user's context."""
    if user_id not in user_contexts:
        initialize_user_context(user_id)
    user_contexts[user_id][key] = value

def get_user_context_value(user_id: str, key: str, default=None) -> Any:
    """Get a value from the user's context."""
    if user_id not in user_contexts:
        initialize_user_context(user_id)
    return user_contexts[user_id].get(key, default)

def track_user_message(user_id: str, message: str) -> None:
    """Track user message in history."""
    if user_id not in user_contexts:
        initialize_user_context(user_id)
        
    # Update last interaction time
    update_user_context(user_id, "last_interaction", time.time())
    
    # Add message to history (keep last 10 messages)
    history = get_user_context_value(user_id, "history", [])
    history.append({"role": "user", "content": message, "timestamp": time.time()})
    if len(history) > 10:
        history = history[-10:]
    update_user_context(user_id, "history", history)
    
    # Check for frustration indicators
    if has_frustration_indicators(message):
        current_frustration = get_user_context_value(user_id, "frustration_level", 0)
        update_user_context(user_id, "frustration_level", min(5, current_frustration + 1))
    
    # Check for name mentions
    extract_user_name(user_id, message)
    
    # Track query for analytics
    queries = get_user_context_value(user_id, "previous_queries", [])
    queries.append(message)
    update_user_context(user_id, "previous_queries", queries[-5:])  # Keep last 5 queries

def has_frustration_indicators(message: str) -> bool:
    """Check if message contains indicators of user frustration."""
    frustration_patterns = [
        r'(?:!{2,})',  # Multiple exclamation marks
        r'(?:\?{2,})',  # Multiple question marks
        r'(?:[A-Z\s]{4,})',  # ALL CAPS (at least 4 chars)
        r'(?:wtf|omg|what the|are you serious|come on|really\?|stupid)',  # Explicit frustration
        r'(?:still|again|repeat|already told you)',  # Repetition frustration
    ]
    
    message_lower = message.lower()
    for pattern in frustration_patterns:
        if re.search(pattern, message):
            return True
    
    return False

def extract_user_name(user_id: str, message: str) -> None:
    """Try to extract user's name from message for personalization."""
    name_patterns = [
        r"(?:my name is|I am|I'm|call me) (\w+)",
        r"(?:this is) (\w+)"
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            name = match.group(1)
            # Clean up the name (capitalize first letter)
            if name and len(name) > 2:  # Avoid very short names
                update_user_context(user_id, "user_name", name.capitalize())
                break

# Small talk capabilities
def handle_small_talk(message: str, user_id: str) -> Optional[str]:
    """Handle casual conversation not related to the main functionality."""
    message_lower = message.lower()
    
    # Check for greetings with name if we know the user's name
    user_name = get_user_context_value(user_id, "user_name")
    if user_name and any(greeting in message_lower for greeting in ["hi", "hello", "hey", "good morning", "good evening"]):
        return f"Hello, {user_name}! How can I help you with SciPris today?"
    
    # Handle thank you messages
    if any(phrase in message_lower for phrase in ["thank you", "thanks", "thx", "ty"]):
        return random.choice([
            "You're welcome! Is there anything else I can help you with?",
            "Happy to help! Let me know if you need anything else.",
            "My pleasure! Is there something else you'd like to know about SciPris?"
        ])
    
    # Handle goodbyes
    if any(phrase in message_lower for phrase in ["bye", "goodbye", "see you", "talk to you later", "have a good day"]):
        return random.choice([
            "Goodbye! Feel free to come back if you have more questions.",
            "Take care! I'm here if you need any more assistance with SciPris.",
            "Until next time! Have a great day."
        ])
    
    # Handle how are you
    if any(phrase in message_lower for phrase in ["how are you", "how's it going", "how are things"]):
        return random.choice([
            "I'm doing well, thank you for asking! How can I assist you with SciPris today?",
            "I'm here and ready to help! What can I do for you?",
            "I'm great! I appreciate you asking. What SciPris-related questions do you have?"
        ])
    
    # Handle who are you
    if any(phrase in message_lower for phrase in ["who are you", "what are you", "what's your name"]):
        return "I'm the SciPris assistant, designed to help you with invoice-related queries, payment issues, and other SciPris-related questions. How can I assist you today?"
    
    return None  # No small talk detected

def get_frustration_response(user_id: str) -> Optional[str]:
    """Generate empathetic responses when user seems frustrated."""
    frustration_level = get_user_context_value(user_id, "frustration_level", 0)
    
    if frustration_level >= 4:
        return random.choice([
            "I understand this might be frustrating. Would you like to speak with a human representative? I can help arrange that.",
            "I apologize for the difficulty. If you prefer, we can escalate this to our support team who can help resolve your issue more effectively.",
            "I'm sorry you're having trouble. Would it help if I connected you with our customer support team?"
        ])
    elif frustration_level >= 2:
        return random.choice([
            "I apologize for any confusion. Let's try a different approach to resolve your issue.",
            "I understand this can be frustrating. Let me try to help you another way.",
            "I'm sorry if I misunderstood. Could you please help me understand your request differently?"
        ])
        
    return None  # Not frustrated enough for special response

# Add a function to map common questions to response categories
def match_query_to_response(query: str, responses_mapping: dict) -> Tuple[Optional[str], Optional[str]]:
    """
    Match a user query to the appropriate response category and sub-category.
    
    Args:
        query (str): The user's query
        responses_mapping (dict): The loaded responses from JSON
    
    Returns:
        Tuple[Optional[str], Optional[str]]: (category, sub_category) if found, (None, None) otherwise
    """
    query_lower = query.lower().strip()
    
    # Handle both old and new format responses.json
    is_new_format = "payment_methods" in responses_mapping
    
    # Define mappings from common questions/phrases to response categories
    if is_new_format:
        # New format patterns
        common_questions = {
            # Payment methods/options
            r"(?:what|which)?\s*(?:payment methods?|payment options|how (?:to|can i|do i) pay|ways to pay|accepted payments?)": 
                ("payment_methods", "general"),
            
            # Credit cards
            r"(?:credit|debit)\s*cards?|visa|mastercard|amex|american express": 
                ("payment_methods", "credit_cards"),
            
            # Bank transfers
            r"(?:bank|wire|ach|swift)\s*(?:transfer|payment)|bank details": 
                ("payment_methods", "bank_transfer"),
            
            # Invoices
            r"(?:invoice|bill|billing|receipt)": 
                ("payment_methods", "invoice"),
            
            # Purchase orders
            r"(?:purchase order|po|institutional purchase)": 
                ("payment_methods", "purchase_orders"),
            
            # Login issues
            r"(?:login|log in|signin|sign in|account access|password)\s*(?:issues?|problems?|difficulties?|troubles?|help)": 
                ("login_issues", "general"),
            
            # Password reset
            r"(?:password|pw|pwd)\s*(?:reset|change|forgot|recover|update)": 
                ("login_issues", "password_reset"),
            
            # Account locked
            r"(?:account|profile|user)\s*(?:locked|disabled|blocked)": 
                ("login_issues", "account_locked"),
            
            # Email verification
            r"(?:email|mail|e-mail)\s*(?:verification|verify|confirmed|confirming|validate)": 
                ("login_issues", "email_verification"),
            
            # Article access
            r"(?:article|paper|access|view|download)\s*(?:access|viewing|reading|get|obtain)": 
                ("article_access", "general"),
            
            # Download issues
            r"(?:download|pdf|file)\s*(?:issues?|problems?|error|not working)": 
                ("article_access", "download_issues"),
            
            # Institutional access
            r"(?:institution|university|campus|organizational)\s*(?:access|subscription)": 
                ("article_access", "institutional_access"),
            
            # Article sharing
            r"(?:share|sharing|redistribute|send)\s*(?:article|paper|pdf|content)": 
                ("article_access", "sharing"),
            
            # Browser compatibility
            r"(?:which|what|recommended)\s*(?:browsers?|browser compatibility)": 
                ("technical_issues", "browser_compatibility"),
            
            # Mobile access
            r"(?:mobile|phone|tablet|android|ios|iphone|ipad)\s*(?:access|version|app)": 
                ("technical_issues", "mobile_access"),
            
            # Cookies
            r"(?:cookies?|site data|browser data)": 
                ("technical_issues", "cookies"),
            
            # PDF viewer
            r"(?:pdf viewer|reader|adobe|viewing pdf)": 
                ("technical_issues", "pdf_viewer"),
            
            # Contact
            r"(?:contact|reach|email|phone|call)\s*(?:support|help|team|service)": 
                ("contact", "general"),
            
            # Technical support
            r"(?:technical|tech)\s*(?:support|help|assistance)": 
                ("contact", "technical_support"),
            
            # Billing contact
            r"(?:billing|payment|invoice)\s*(?:support|contact|questions|department)": 
                ("contact", "billing"),
            
            # Feedback
            r"(?:feedback|suggestion|improve|review)": 
                ("contact", "feedback"),
        }
    else:
        # Original format patterns
        common_questions = {
            # Payment methods/options
            r"(?:what|which)?\s*(?:payment methods?|payment options|how (?:to|can i|do i) pay|ways to pay|accepted payments?)": 
                ("General Queries", "Available payment options"),
            
            # Browser compatibility
            r"(?:which|what|recommended)\s*(?:browsers?|browser compatibility)": 
                ("General Queries", "Recommended browsers"),
            
            # Login issues
            r"(?:login|log in|signin|sign in|account access|password)\s*(?:issues?|problems?|difficulties?|troubles?|help)": 
                ("General Queries", "Login issues"),
            
            # Split payment
            r"(?:split|divide|share)\s*(?:the|a|article|publication)?\s*(?:fee|payment|cost)": 
                ("General Queries", "Split Article Publication fee"),
            
            # Change payer
            r"(?:change|modify|update|different|another)\s*(?:payer|who pays|payment maker)": 
                ("General Queries", "Change payer"),
            
            # Need account for payment
            r"(?:need|require|must have|do i need)?\s*(?:a|an|user)?\s*account\s*(?:to|for)?\s*(?:pay|payment|making payment)": 
                ("General Queries", "Need a user account for payments?"),
            
            # Institution payment
            r"(?:institution|university|company|organization|employer)\s*(?:pay|paying|payment|cover|covering)": 
                ("General Queries", "Institution making payment"),
            
            # Payment without confirmation
            r"(?:payment|money)\s*(?:deducted|taken|charged|withdrawn)\s*(?:but|yet|no)\s*(?:confirmation|receipt|email|notification)": 
                ("General Queries", "Payment deducted but no confirmation"),
            
            # License issues
            r"(?:license|licence)\s*(?:link|email|mail)\s*(?:not|haven't|didn't|never)\s*(?:received|got|obtained)": 
                ("License & Access Issues", "License Link Not Received"),
            
            # Email update
            r"(?:update|change|modify|new)\s*(?:email|e-mail|email address)": 
                ("License & Access Issues", "Email Update Request"),
            
            # Password reset
            r"(?:password|pw|pwd)\s*(?:reset|change|forgot|recover|update)": 
                ("License & Access Issues", "Password Reset Issues"),
            
            # Waiver
            r"(?:partial|fee)?\s*(?:waiver|reduction|discount|reduced fee)": 
                ("Waiver & Deadline Issues", "Partial Waiver Request"),
            
            # Deadline extension
            r"(?:deadline|due date|submission date|timeline)\s*(?:extension|extend|postpone|delay)": 
                ("Waiver & Deadline Issues", "Deadline Extension Request"),
        }
    
    # Check each pattern to see if it matches the query
    for pattern, (category, sub_category) in common_questions.items():
        if re.search(pattern, query_lower):
            return category, sub_category
    
    # No match found
    return None, None

# Log unmatched queries for future improvements
def log_unmatched_query(user_id: str, query: str) -> None:
    """
    Log queries that the chatbot couldn't match to a response category.
    This helps improve the chatbot over time.
    """
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file = os.path.join(log_dir, "unmatched_queries.jsonl")
    
    try:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "query": query
        }
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"Error logging unmatched query: {e}")

def scipris_chatbot(user_input: str, user_context=None, user_id: str = "default") -> tuple:
    """
    Enhanced chatbot logic with context awareness and small talk.
    """
    # Debug logging
    print(f"DEBUG: User input: '{user_input}', Current context: '{user_context}', User ID: '{user_id}'")
    
    # Track user message for context
    track_user_message(user_id, user_input)
    
    user_input = user_input.strip()
    
    try:
        responses_mapping = load_responses_mapping()
    except Exception as e:
        print(f"Error loading responses mapping: {e}")
        # Fallback to empty responses if loading fails
        responses_mapping = {
            "General Queries": {
                "No answer found": [
                    "I'm experiencing technical difficulties. Please try again later."
                ]
            }
        }
    
    # Check if using new or old response format
    is_new_format = "payment_methods" in responses_mapping
    
    if is_new_format:
        # For new format, there's no sub-options list
        main_options = list(responses_mapping.keys())
    else:
        # For old format, lowercase for case-insensitive matching
        main_options = [option.lower() for option in responses_mapping.keys()]
        
    greetings = ["hi", "hello", "hey", "good morning", "good evening"]

    # Check if user selected a satisfaction option
    if user_input in SATISFACTION_OPTIONS:
        if user_input == "Yes, I'm satisfied":
            return "Great! I'm glad I could help. Is there anything else you'd like to know?", None
        else:  # User needs human support
            return "I understand you need additional help. I'll connect you with our support team who will contact you soon. Thank you for your patience.", None

    # Try semantic matching for common questions
    category, sub_category = match_query_to_response(user_input, responses_mapping)
    if category and sub_category:
        # If we found a match, return a response from that category
        try:
            if category in responses_mapping and sub_category in responses_mapping[category]:
                responses = responses_mapping[category][sub_category]
                # Handle both formats (list of responses or single string)
                if isinstance(responses, list):
                    response = random.choice(responses)
                    return response, SATISFACTION_OPTIONS
                else:
                    return responses, SATISFACTION_OPTIONS
        except Exception as e:
            print(f"Error retrieving response for {category}/{sub_category}: {e}")
            # Continue with other response methods if retrieval fails
    
    # Check if input contains a DOI pattern - this helps detect invoice queries
    doi_pattern = r'10\.\d{4,9}/[-._;()/:\w]+'
    has_doi = re.search(doi_pattern, user_input)
    
    # Auto-detect DOI and title inquiries even without explicit context
    if has_doi and user_context is None:
        doi, title = extract_doi_and_title(user_input)
        if doi and title:
            # If both DOI and title were found, treat as invoice query
            response = get_invoice_details(doi, title)
            return response, SATISFACTION_OPTIONS
        elif doi:
            # If only DOI was found, ask for title
            return (
                "I see you've provided a DOI. Could you please also provide the article title? "
                "You can say something like 'The article titled [Your Article Title]'"
            ), "awaiting_invoice_doi"
    
    # Check for small talk first
    small_talk_response = handle_small_talk(user_input, user_id)
    if small_talk_response:
        return small_talk_response, None
    
    # Check if user is frustrated and provide empathetic response
    frustration_response = get_frustration_response(user_id)
    if frustration_response:
        update_user_context(user_id, "frustration_level", 0)  # Reset frustration after addressing it
        return frustration_response, SATISFACTION_OPTIONS
    
    # Add personalization if we know the user's name
    user_name = get_user_context_value(user_id, "user_name")
    greeting_prefix = f"Hi {user_name}! " if user_name else ""
    
    # Add more natural responses
    greeting_responses = [
        f"{greeting_prefix}I'm here to help you with SciPris. How can I assist you today?",
        f"{greeting_prefix}I'm your SciPris assistant. What can I do for you?",
        f"{greeting_prefix}Good to see you! How may I help you with SciPris today?",
        f"{greeting_prefix}I'm ready to help you with any SciPris-related questions."
    ]
    
    # Handle Greetings with more natural responses
    if user_input.lower() in greetings:
        return random.choice(greeting_responses), None

    # Handle Card Payment Failure (context-specific)
    if user_context == "card_payment_failure":
        print(f"DEBUG: In card_payment_failure context. User input: '{user_input}'")
        
        # Very simple detection - just look for basic card keywords anywhere in input
        user_input_lower = user_input.lower().strip()
        
        # Direct equality test first (for inputs like just "visa" or "mastercard")
        if user_input_lower == "visa" or user_input_lower == "v":
            print(f"DEBUG: Visa card detected via equality: '{user_input_lower}'")
            response = (
                "Great! Your Visa card is supported. Let's try the payment again. "
                "If the issue persists, I recommend contacting your bank or trying a different card."
            )
            return response, SATISFACTION_OPTIONS  # Add satisfaction check
            
        if user_input_lower in ["mastercard", "master card", "master", "mc", "m"]:
            print(f"DEBUG: MasterCard detected via equality: '{user_input_lower}'")
            response = (
                "Great! Your MasterCard is supported. Let's try the payment again. "
                "If the issue persists, I recommend contacting your bank or trying a different card."
            )
            return response, SATISFACTION_OPTIONS  # Add satisfaction check
            
        # Then check for card names within text
        if "visa" in user_input_lower:
            print(f"DEBUG: Visa card detected in: '{user_input_lower}'")
            response = (
                "Great! Your Visa card is supported. Let's try the payment again. "
                "If the issue persists, I recommend contacting your bank or trying a different card."
            )
            return response, SATISFACTION_OPTIONS  # Add satisfaction check
            
        if any(card in user_input_lower for card in ["master", "mc", "mastercard"]):
            print(f"DEBUG: MasterCard detected in: '{user_input_lower}'")
            response = (
                "Great! Your MasterCard is supported. Let's try the payment again. "
                "If the issue persists, I recommend contacting your bank or trying a different card."
            )
            return response, SATISFACTION_OPTIONS  # Add satisfaction check
            
        # Fallback for unsupported cards
        print(f"DEBUG: Unsupported card type in: '{user_input_lower}'")
        response = (
            "I understand you're having issues with your card. "
            "SciPris currently only accepts Visa and MasterCard for card payments. "
            "Would you like to try using Bank Transfer instead? It's a reliable alternative."
        )
        return response, SATISFACTION_OPTIONS  # Add satisfaction check

    # Trigger card payment failure context
    if user_input.lower() == "card payment failure":
        print(f"DEBUG: Setting context to card_payment_failure")
        return (
            "I see you're experiencing issues with your card payment. "
            "Let me help you resolve this. Could you please tell me which card operator you're using? "
            "(e.g., Visa, MasterCard, Amex, Discover)"
        ), "card_payment_failure"

    # Enhanced Invoice Query Handling with context awareness
    if user_context == "awaiting_invoice_doi":
        doi, title = extract_doi_and_title(user_input)
        
        # Increment failed attempts if DOI not found
        if not doi:
            doi_attempts = get_user_context_value(user_id, "doi_attempts", 0) + 1
            update_user_context(user_id, "doi_attempts", doi_attempts)
            
            # After 2 failed attempts, provide more examples or offer alternative
            if doi_attempts >= 2:
                update_user_context(user_id, "doi_attempts", 0)  # Reset counter
                response = (
                    "I notice we're having difficulty finding your DOI. "
                    "You can also try one of these options:\n\n"
                    "1. Send us your article title only, and we'll try to locate it\n"
                    "2. Check your email for communication from SciPris containing the DOI\n"
                    "3. Contact support@scipris.com with your article details"
                )
                return response, SATISFACTION_OPTIONS
                
            return (
                "I'm having trouble finding the DOI and article title in your message. "
                "Could you please provide them in one of these formats:\n\n"
                "1. 'DOI: 10.1234/exampledoi, Article: My Research Paper'\n"
                "2. 'The article titled My Research Paper with DOI 10.1234/exampledoi'\n"
                "3. '10.1234/exampledoi, My Research Paper'"
            ), "awaiting_invoice_doi"
            
        if not title:
            return (
                "I found the DOI, but I couldn't identify the article title. "
                "Could you please provide the article title as well? "
                "You can say something like 'The article titled [Your Article Title]'"
            ), "awaiting_invoice_doi"
            
        # Reset attempts counter on success
        update_user_context(user_id, "doi_attempts", 0)
        response = get_invoice_details(doi, title)
        return response, SATISFACTION_OPTIONS  # Add satisfaction check

    if user_input.lower() == "invoice not received":
        return (
            "I understand you haven't received your invoice. "
            "To help you better, I'll need your article's DOI and title. "
            "Could you please provide them? You can share them in any format you prefer."
        ), "awaiting_invoice_doi"

    if user_input.lower() == "incorrect invoice":
        return (
            "I'm sorry to hear that the invoice is incorrect. "
            "To help you resolve this, I'll need your article's DOI and title. "
            "Could you please provide them?"
        ), "awaiting_invoice_doi"

    # Handle Main Menu Options with more natural responses
    if user_input.lower() in main_options:
        user_context = None
        matched_option = [option for option in responses_mapping if option.lower() == user_input.lower()][0]
        sub_options = responses_mapping[matched_option]
        options_list = list(sub_options.keys())
        return (
            f'I understand you\'re interested in "{matched_option}". '
            f'Here are the options I can help you with:',
            options_list
        )

    # Handle Submenu Options with more natural responses
    for main_option, sub_options in responses_mapping.items():
        for sub_option, response in sub_options.items():
            if user_input.lower() == sub_option.lower():
                if isinstance(response, list):
                    final_response = random.choice(response)
                    return final_response, SATISFACTION_OPTIONS  # Add satisfaction check
                else:
                    return response, SATISFACTION_OPTIONS  # Add satisfaction check

    # Log unmatched queries for improving the chatbot
    log_unmatched_query(user_id, user_input)
    
    # If no match found in responses.json, try to provide a related response
    # based on keywords in the user's query
    query_keywords = set(user_input.lower().split())
    best_category = None
    best_sub_category = None
    best_score = 0
    
    # Try to find the best match based on keyword overlap
    for category, subcategories in responses_mapping.items():
        category_keywords = set(category.lower().split())
        for sub_category in subcategories:
            sub_keywords = set(sub_category.lower().split())
            combined_keywords = category_keywords.union(sub_keywords)
            score = len(query_keywords.intersection(combined_keywords))
            
            if score > best_score:
                best_score = score
                best_category = category
                best_sub_category = sub_category
    
    # If we found a reasonable match (at least one keyword overlap)
    if best_score > 0 and best_category and best_sub_category:
        responses = responses_mapping[best_category][best_sub_category]
        if isinstance(responses, list):
            final_response = (
                f"I think you're asking about {best_sub_category}. "
                f"{random.choice(responses)}"
            )
            return final_response, SATISFACTION_OPTIONS  # Add satisfaction check
        else:
            final_response = (
                f"I think you're asking about {best_sub_category}. "
                f"{responses}"
            )
            return final_response, SATISFACTION_OPTIONS  # Add satisfaction check
    
    # More natural default response with suggestions
    return (
        "I'm not sure I understand that request. "
        "Could you please rephrase it or choose from one of our main topics: "
        "Payment Failure, Refund Issues, Invoice Requests, or Other Payment Queries?"
    ), None