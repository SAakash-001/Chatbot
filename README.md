# SciPris Chatbot

A conversational AI assistant for the SciPris platform, handling invoice queries, payment issues, and general platform questions.

## Features

- Natural language understanding for common user inquiries
- DOI and article title extraction from various text formats
- Context-aware conversations with multi-turn capabilities
- Automatic handling of invoice and payment queries
- Frustration detection for improved user experience

## System Requirements

- Python 3.8+
- FastAPI
- SQLite3
- Internet connection for web queries

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ChatBotEx.git
   cd ChatBotEx
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install fastapi uvicorn sqlite3 jinja2
   ```

## Configuration

1. Create a `responses.json` file in the root directory (sample provided).

2. For production deployment, update any hardcoded values like session timeouts in `main.py`.

## Running the Application

### Development Mode

```
python ChatBotEx/main.py
```

Or with uvicorn directly:
```
uvicorn ChatBotEx.main:app --reload --host 127.0.0.1 --port 8000
```

### Production Deployment

For production, we recommend using Gunicorn with Uvicorn workers:

```
pip install gunicorn
gunicorn ChatBotEx.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Testing

Run the unit tests to verify functionality:

```
python -m unittest discover tests
```

## Deployment Checklist

Before deploying to production, ensure you:

1. ✅ Set appropriate session timeouts for your usage patterns
2. ✅ Secure the API with proper authentication if needed
3. ✅ Set up regular database backups
4. ✅ Configure logging to a persistent storage
5. ✅ Set up monitoring for the health check endpoint
6. ✅ Use a production-ready web server (Gunicorn, etc.)
7. ✅ Set up SSL/TLS for secure communication

## API Endpoints

- `GET /` - Web interface for the chatbot
- `POST /ask` - JSON API for chatbot queries
- `GET /healthcheck` - System health status
- `GET /session/{session_id}/history` - Retrieve conversation history
- `POST /feedback` - Submit user feedback

## Troubleshooting

If you encounter issues:

1. Check the logs for error messages
2. Verify the database connection is working
3. Ensure responses.json is properly formatted
4. Check for any path issues on your system

## License

This project is licensed under the MIT License - see the LICENSE file for details. 