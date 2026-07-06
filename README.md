# SmartPatent - Premium AI-Powered Patent Architect

SmartPatent is an industry-level, production-ready, full-stack application designed to automate the process of patent drafting and prior-art novelty analysis. It integrates advanced Large Language Models (Gemini 2.5 Flash) with real-time global patent search (Lens.org API) and Natural Language Processing (TF-IDF + Cosine Similarity) to generate legally compliant, structured patent documents.

---

## Key Features

* **AI-Assisted Patent Drafting:** Leverages Gemini 2.5 Flash to automatically extract technical concepts from unstructured details to output structured sections (Title, Claims, Background, Summary, Description).
* **Automated Prior-Art Retrieval:** Integrates the Lens API to query patent databases globally and retrieve overlapping patents.
* **Corpus-Wide TF-IDF Similarity Ranking:** Computes mathematical similarity between your concept and all retrieved patents using a corpus-wide Scikit-learn TF-IDF alignment.
* **Diagram Upload & Vision Understanding:** Upload image diagrams (PNG/JPG/WEBP); the system utilizes multimodal understanding to produce drawing captions and detailed figure descriptions.
* **Production-Grade Security:**
  * Protected against Insecure Direct Object References (IDOR) on all edit, history, and document download routes.
  * Robust, salted password hashing using PBKDF2 (Werkzeug security).
  * Server-side mime-type verification and 5MB size validation for image uploads.
* **Database Connection Pooling:** Implements a thread-safe connection pool using `mysql.connector.pooling` to handle concurrent operations at scale.
* **Multi-Format Exports:** Download generated patent specifications as TXT, Microsoft Word (`.docx`), and beautifully formatted, wrapped PDFs.
* **Version History Tracking:** Track, save, and preview previous versions of drafts.
* **Premium User Interface:** Dark-mode glassmorphic theme designed for readability, fitted with Inter typography, and interactive loading screens.

---

## Technical Stack

* **Backend Framework:** Python Flask
* **Database Layer:** MySQL 8.0 with `mysql.connector.pooling`
* **AI Integration:** Google GenAI SDK (`gemini-2.5-flash`)
* **External Patent API:** Lens.org Search API
* **Natural Language Processing:** Scikit-learn (TF-IDF Vectorization & Cosine Similarity)
* **Document Services:** ReportLab (wrapped PDF flowables), Python-Docx
* **DevOps Configuration:** Docker, Docker Compose, Nginx Reverse Proxy, GitHub Actions

---

## Database Schema Model

The database comprises four core tables with relational constraints and indexing:

1. **`users`:** Holds user profiles with email indexes and salted passwords.
2. **`drafts`:** Stores the primary metadata of drafts, foreign keyed to `users`.
3. **`related_patents`:** Stores patent search results linked to their parent draft.
4. **`draft_versions`:** Keeps historical drafts to support rolling back changes.

For full SQL definitions, view **[database/schema.sql](file:///C:/Users/disha/.gemini/antigravity/scratch/SmartPatent/database/schema.sql)**.

---

## Local Setup & Configuration

### Prerequisites
* Python 3.9+
* MySQL Server (v8.0 recommended)

### 1. Setup Environment
Clone or navigate to the workspace directory. Create a `.env` file in the root directory:
```bash
cp .env.example .env
```
Open `.env` and fill in your API keys and database credentials:
```env
SECRET_KEY=use_a_secure_random_hash
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=smartpatent
GEMINI_API_KEY=your_google_gemini_key
LENS_API_KEY=your_lens_org_api_token
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Database
Create the `smartpatent` database and load the schema:
```sql
CREATE DATABASE smartpatent;
```
```bash
mysql -u root -p smartpatent < database/schema.sql
```

### 4. Run the App
```bash
python app.py
```
Open `http://127.0.0.1:5000/` in your browser.

---

## Docker Deployment (Production)

To launch a production-grade multi-container orchestrations of SmartPatent (Flask running on Gunicorn + MySQL 8.0 database) behind Nginx:

1. Ensure your `.env` file is populated.
2. Launch docker-compose:
   ```bash
   docker-compose up --build -d
   ```
This maps the application to port `80` (or `8000` depending on your compose configuration) and configures volume maps to persist database records and uploads.

---

## Running the Tests

To run the automated suite of unit, integration, and security tests:
```bash
pytest --cov=.
```
Tests are located in the `tests/` folder:
* `tests/test_auth.py`: Verifies signup validations, duplicate checks, and logins.
* `tests/test_patent.py`: Validates IDOR access controls, edits authorization, and TF-IDF math.
