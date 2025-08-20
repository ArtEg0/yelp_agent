Yelp Agent – Auto-Responder (Semi-Automatic Version)

Usage:
1. gmail_reader.py – fetches Yelp emails
2. yelp_parser.py – extracts client and move details
3. template_engine.py – generates reply (or request for missing info)
4. yelp_auto_replier.py – replicates browser interaction (based on recorded flow)
5. main.py – runs the pipeline

To run:
$ python3 main.py

Make sure to set up your Gmail credentials and manually record Yelp login session in Chrome.
