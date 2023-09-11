
# FastAPI Theme Extraction Web Service

This repository contains a FastAPI based web service that performs theme extraction for web pages and persists the data in an SQLite database.

## Deploy to Google Cloud Run

[![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run/?git_repo=https://github.com/pzhang1/nlp_service&project=PROJECT_ID&service=SERVICE_NAME)


## Requirements

- Python 3.8 or higher
- Docker (Optional, for creating a container)

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/pzhang1/nlp_service.git
cd nlp_service
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Run the FastAPI application:

```bash
uvicorn main:app --reload
```

4. Access the API documentation:

To access the automatically generated API documentation, launch your favorite web browser and navigate to:

- http://127.0.0.1:8000/docs (ReDoc)
- http://127.0.0.1:8000/redoc (Swagger UI)

5. Deployment to Google Cloud Run:

Follow the deployment instruction mentioned in the `README.md` file in the repository root.

## API Endpoints

- `POST /themes`: Expects a `url` parameter as JSON in the request body. It will then fetch the webpage content, extract the themes using the `extract_themes` function, and store them in the SQLite database along with their relevance.
- `GET /themes/extracted`: Extracted list of themes in the database.
- `GET /themes/detected`:  Return a list of texts with the detected themes

## Testing

Run the tests for data processing and API using:

```bash
python -m pytest test_main.py
```
