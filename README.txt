Yelp Agent – Auto-Responder (Semi-Automatic Version)

Usage:
1. gmail_reader.py – fetches Yelp emails (resilient, with deduping and logging)
2. yelp_parser.py – extracts client and move details (multiple formats)
3. template_engine.py – generates reply (handles missing data gracefully)
4. yelp_auto_replier.py – placeholder for future auto-send (not used)
5. main.py – runs the pipeline and prints suggested reply

To run:
$ python3 main.py

Setup:
- Create a .env file (see .env.example) with Gmail IMAP credentials
- pip install -r requirements.txt
- Run: python3 main.py

Environment variables (.env):
- EMAIL_ADDRESS
- EMAIL_APP_PASSWORD
- EMAIL_IMAP_SERVER (default imap.gmail.com)
- EMAIL_IMAP_PORT (default 993)
- PROCESSED_FILE (default processed_emails.txt)
- LOG_LEVEL (default INFO)
