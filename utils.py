import json
import random
import sqlite3
import re

# === UTILS: Load JSON Responses ===
def load_responses(file_path: str = "responses.json") -> dict:
    """Load chatbot responses from a JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading responses: {e}")
        return {}

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
    query = """
    SELECT doi, title, status FROM articles WHERE doi = ? AND title = ? COLLATE NOCASE
    """
    try:
        conn = sqlite3.connect("articles.db")
        cursor = conn.cursor()
        cursor.execute(query, (doi.strip(), title.strip()))
        row = cursor.fetchone()
        conn.close()
        if row:
            return (
                f"Invoice Details for DOI `{row[0]}`\n\n"
                f"Title: {row[1]}\n\n"
                f"Invoice Status: {row[2]}"
            )
        return "No invoice found for the given DOI and article name. Please verify your details."
    except Exception as e:
        print(f"Database Error: {e}")
        return "There was an error retrieving the invoice details. Please try again later."


# === CHATBOT LOGIC ===
def scipris_chatbot(user_input: str, user_context=None) -> tuple:
    """
    Main chatbot logic: Handles greetings, DOI/article queries, invoice issues, card payment failure,
    menu navigation, and context tracking.
    
    Returns:
        tuple: (response_text, new_context)
               new_context is either:
               - None,
               - a context string for multi-step interactions, or
               - an array of sub-options (for main menu choices).
    """
    user_input = user_input.strip()
    responses_mapping = load_responses_mapping()
    # Create a list of main options (lowercase) from the responses mapping
    main_options = [option.lower() for option in responses_mapping.keys()]
    greetings = ["hi", "hello", "hey", "good morning", "good evening"]

    # Handle Greetings
    if user_input.lower() in greetings:
        return random.choice([
            "Hello! How can I assist you with SciPris today?",
            "Hi there! How can I help?"
        ]), None

    # Handle Card Payment Failure (context-specific)
    if user_context == "card_payment_failure":
        accepted_cards = ["visa", "mastercard"]
        if user_input.lower() not in accepted_cards:
            return (
                "SciPris only accepts Visa and MasterCard for card payments. "
                "If you do not have one of these, please consider using Bank Transfer instead."
            ), None
        return "Your card operator is accepted. Please try again or contact your bank if the issue persists.", None

    if user_input.lower() == "card payment failure":
        return (
            "Your card payment did not go through. Please verify your card details or try a different card.\n\n"
            "Please mention your card operator (e.g., Visa, MasterCard, Amex, Discover)."
        ), "card_payment_failure"

    # Handle Invoice Queries (context-specific)
    if user_context == "awaiting_invoice_doi":
        doi_title = [x.strip() for x in user_input.split(",", 1)]
        if len(doi_title) == 2:
            doi, title = doi_title
            doi_pattern = re.compile(r"^10\.\d{4,9}/\S+$")
            if not doi_pattern.match(doi):
                return "The DOI format is incorrect. Please enter a valid DOI (starting with '10.').", "awaiting_invoice_doi"
            return get_invoice_details(doi, title), None
        return (
            "Please provide both the DOI and article name, separated by a comma.\n\n"
            "Example: 10.1234/exampledoi, My Research Paper"
        ), "awaiting_invoice_doi"

    if user_input.lower() == "invoice not received":
        return (
            "It appears you haven't received your invoice.\n\n"
            "Please provide your DOI and article name, separated by a comma.\n\n"
            "Example: 10.1234/exampledoi, My Research Paper"
        ), "awaiting_invoice_doi"

    if user_input.lower() == "incorrect invoice":
        return (
            "It looks like the invoice is incorrect.\n\n"
            "Kindly provide your DOI and article name, separated by a comma.\n\n"
            "Example: 10.1234/exampledoi, My Research Paper"
        ), "awaiting_invoice_doi"

    # Handle Main Menu Options (Drop-down)
    if user_input.lower() in main_options:
        # Clear any lingering context
        user_context = None
        # Find the matched main option (preserve original casing)
        matched_option = [option for option in responses_mapping if option.lower() == user_input.lower()][0]
        sub_options = responses_mapping[matched_option]
        # Return the list of sub-option keys as the options array
        options_list = list(sub_options.keys())
        return (
            f'You selected "{matched_option}". Please choose one of the following:',
            options_list
        )

    # Handle Submenu Options
    for main_option, sub_options in responses_mapping.items():
        for sub_option, response in sub_options.items():
            if user_input.lower() == sub_option.lower():
                # If the response is stored as a list, pick one randomly.
                if isinstance(response, list):
                    return random.choice(response), None
                else:
                    return response, None

    # Default Response
    return "Sorry, I couldn't find a matching option. Please check your input.", None
