import json
import requests
from google import genai
from config import Config


def extract_invention_fingerprint(data):
    fallback = {
        "core_terms": [],
        "mechanism_terms": [],
        "problem_terms": [],
        "application_terms": [],
        "query_phrases": []
    }

    if not Config.GEMINI_API_KEY:
        return fallback

    prompt = f"""
You are helping with patent prior-art retrieval.

From the invention description below, extract compact technical search phrases.

Return ONLY valid JSON in this format:
{{
  "core_terms": ["...", "..."],
  "mechanism_terms": ["...", "..."],
  "problem_terms": ["...", "..."],
  "application_terms": ["...", "..."],
  "query_phrases": ["...", "...", "...", "..."]
}}

Rules:
- Each phrase should be short: 2 to 5 words.
- Prefer concrete technical phrases.
- Avoid long sentences.
- Avoid generic terms unless important.
- Focus on invention concept, mechanism, problem, and applications.

Invention details:
Title: {data.get("title", "")}
Field: {data.get("field", "")}
Problem: {data.get("problem", "")}
Existing Solution: {data.get("existing_solution", "")}
Proposed Solution: {data.get("proposed_solution", "")}
Working: {data.get("working", "")}
Advantages: {data.get("advantages", "")}
Components: {data.get("components", "")}
Applications: {data.get("applications", "")}
"""

    try:
        client = genai.Client(api_key=Config.GEMINI_API_KEY)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text if getattr(response, "text", None) else ""
        text = text.strip()

        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            text = text[start:end + 1]

        parsed = json.loads(text)

        return {
            "core_terms": parsed.get("core_terms", []),
            "mechanism_terms": parsed.get("mechanism_terms", []),
            "problem_terms": parsed.get("problem_terms", []),
            "application_terms": parsed.get("application_terms", []),
            "query_phrases": parsed.get("query_phrases", [])
        }

    except Exception:
        return fallback


def build_candidate_queries(data, fingerprint):
    title = (data.get("title", "") or "").strip()

    queries = []

    if title:
        queries.append(f'title:"{title}"')

    for phrase in fingerprint.get("query_phrases", [])[:5]:
        phrase = phrase.strip()
        if phrase:
            queries.append(phrase)

    core_terms = fingerprint.get("core_terms", [])[:3]
    if core_terms:
        queries.append(" ".join(core_terms))

    mechanism_terms = fingerprint.get("mechanism_terms", [])[:3]
    if mechanism_terms:
        queries.append(" ".join(mechanism_terms))

    problem_terms = fingerprint.get("problem_terms", [])[:2]
    application_terms = fingerprint.get("application_terms", [])[:2]
    if problem_terms or application_terms:
        queries.append(" ".join(problem_terms + application_terms))

    final_queries = []
    seen = set()
    for q in queries:
        q = q.strip()
        if q and q not in seen:
            seen.add(q)
            final_queries.append(q)

    return final_queries[:8] if final_queries else ["patent technology"]


def build_lens_payload(query_text, size=25):
    return {
        "query": query_text,
        "size": size,
        "sort": [
            {"relevance": "desc"}
        ],
        "include": [
            "lens_id",
            "jurisdiction",
            "doc_number",
            "kind",
            "biblio",
            "abstract",
            "publication_type"
        ]
    }


def extract_title(item):
    title_list = item.get("biblio", {}).get("invention_title", [])
    if isinstance(title_list, list) and title_list:
        first = title_list[0]
        if isinstance(first, dict):
            return first.get("text", "").strip()
    return "Untitled Patent"


def extract_abstract(item):
    abstract_list = item.get("abstract", [])
    if isinstance(abstract_list, list) and abstract_list:
        first = abstract_list[0]
        if isinstance(first, dict):
            return first.get("text", "").strip()
    return "No abstract available."


def extract_patent_number(item):
    jurisdiction = item.get("jurisdiction", "") or ""
    doc_number = item.get("doc_number", "") or ""
    kind = item.get("kind", "") or ""

    patent_number = f"{jurisdiction}{doc_number}{kind}".strip()
    if patent_number:
        return patent_number

    pub_ref = item.get("biblio", {}).get("publication_reference", {})
    jurisdiction = pub_ref.get("jurisdiction", "") or ""
    doc_number = pub_ref.get("doc_number", "") or ""
    kind = pub_ref.get("kind", "") or ""
    return f"{jurisdiction}{doc_number}{kind}".strip()


def search_lens_patents(data):
    if not Config.LENS_API_KEY:
        return {
            "results": [],
            "error": "LENS_API_KEY is missing in .env",
            "payload": {},
            "query_text": "",
            "attempted_queries": [],
            "debug_info": [],
            "fingerprint": {}
        }

    fingerprint = extract_invention_fingerprint(data)
    candidate_queries = build_candidate_queries(data, fingerprint)

    url = "https://api.lens.org/patent/search"
    headers = {
        "Authorization": f"Bearer {Config.LENS_API_KEY}",
        "Content-Type": "application/json"
    }

    all_results = []
    debug_info = []
    payloads = []

    for query_text in candidate_queries:
        payload = build_lens_payload(query_text, size=25)
        payloads.append(payload)

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)

            debug_entry = {
                "query": query_text,
                "status_code": response.status_code,
                "response_preview": response.text[:500]
            }

            if response.status_code != 200:
                debug_info.append(debug_entry)
                continue

            api_data = response.json()
            hit_count = len(api_data.get("data", []))
            debug_entry["hit_count"] = hit_count
            debug_info.append(debug_entry)

            for item in api_data.get("data", []):
                lens_id = item.get("lens_id", "")
                all_results.append({
                    "patent_title": extract_title(item),
                    "patent_number": extract_patent_number(item),
                    "abstract_text": extract_abstract(item),
                    "patent_url": f"https://lens.org/{lens_id}" if lens_id else "",
                    "similarity_percent": 0,
                    "raw_lens_score": 0,
                    "matched_query": query_text
                })

            if len(all_results) >= 30:
                break

        except Exception as e:
            debug_info.append({
                "query": query_text,
                "status_code": "EXCEPTION",
                "response_preview": str(e)
            })

    dedup = {}
    for item in all_results:
        key = item.get("patent_number") or item.get("patent_url") or item.get("patent_title")
        if key not in dedup:
            dedup[key] = item

    final_results = list(dedup.values())[:20]

    error_message = ""
    if not final_results:
        error_message = "Lens returned no candidate patents for the generated search queries."

    return {
        "results": final_results,
        "error": error_message,
        "payload": payloads[-1] if payloads else {},
        "query_text": candidate_queries[0] if candidate_queries else "",
        "attempted_queries": candidate_queries,
        "debug_info": debug_info,
        "fingerprint": fingerprint
    }