import re
from google import genai
from config import Config
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def clean_text(text):
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_invention_text(data):
    return " ".join([
        data.get("title", ""),
        data.get("field", ""),
        data.get("problem", ""),
        data.get("existing_solution", ""),
        data.get("proposed_solution", ""),
        data.get("working", ""),
        data.get("advantages", ""),
        data.get("components", ""),
        data.get("applications", "")
    ]).strip()


def classify_similarity(score):
    if score >= 70:
        return "Similar"
    elif score >= 40:
        return "Partially Similar"
    else:
        return "Likely Novel (Preliminary)"


def rank_patents_tfidf(data, related_patents):
    invention_title = clean_text(data.get("title", ""))
    invention_text = clean_text(build_invention_text(data))

    ranked = []

    # Compile global title and abstract corpora
    title_docs = [invention_title] + [clean_text(p.get("patent_title", "")) for p in related_patents]
    abstract_docs = [invention_text] + [clean_text(p.get("abstract_text", "")) for p in related_patents]

    try:
        # Fit vectorizers globally once over the entire retrieved corpus
        vectorizer_title = TfidfVectorizer(stop_words="english")
        tfidf_titles = vectorizer_title.fit_transform(title_docs)

        vectorizer_abstract = TfidfVectorizer(stop_words="english")
        tfidf_abstracts = vectorizer_abstract.fit_transform(abstract_docs)

        user_title_vec = tfidf_titles[0:1]
        user_abstract_vec = tfidf_abstracts[0:1]

        for i, patent in enumerate(related_patents, start=1):
            title_sim = cosine_similarity(user_title_vec, tfidf_titles[i:i+1])[0][0]
            abstract_sim = cosine_similarity(user_abstract_vec, tfidf_abstracts[i:i+1])[0][0]

            final_score = (0.45 * title_sim) + (0.55 * abstract_sim)

            item = dict(patent)
            item["title_component_percent"] = round(title_sim * 100, 2)
            item["abstract_component_percent"] = round(abstract_sim * 100, 2)
            item["lens_component_percent"] = 0
            item["similarity_percent"] = round(final_score * 100, 2)

            ranked.append(item)
    except Exception:
        # Graceful fallback in case of processing errors
        for patent in related_patents:
            item = dict(patent)
            item["title_component_percent"] = 0.0
            item["abstract_component_percent"] = 0.0
            item["lens_component_percent"] = 0
            item["similarity_percent"] = 0.0
            ranked.append(item)

    ranked.sort(key=lambda x: x["similarity_percent"], reverse=True)
    return ranked[:5]


def analyze_prior_art(data, related_patents):
    if not related_patents:
        return {
            "status": "Retrieval Inconclusive",
            "similarity_score": 0,
            "analysis_text": (
                "No candidate patents were retrieved from Lens. Therefore, the system could not perform a meaningful similarity comparison."
            ),
            "ranked_patents": [],
            "formatted_text": (
                "STATUS: Retrieval Inconclusive\n"
                "SIMILARITY_SCORE: 0%\n"
                "EXPLANATION: No candidate patents were retrieved from Lens. Therefore, the system could not perform a meaningful similarity comparison."
            )
        }

    ranked_patents = rank_patents_tfidf(data, related_patents)
    top_patents = ranked_patents[:3]

    overall_similarity = round(
        sum(p["similarity_percent"] for p in top_patents) / len(top_patents),
        2
    ) if top_patents else 0

    status = classify_similarity(overall_similarity)

    patents_text = ""
    for i, p in enumerate(top_patents, start=1):
        patents_text += (
            f"{i}. Title: {p.get('patent_title', '')}\n"
            f"   Number: {p.get('patent_number', '')}\n"
            f"   Final Similarity: {p.get('similarity_percent', 0)}%\n"
            f"   Title Similarity: {p.get('title_component_percent', 0)}%\n"
            f"   Abstract Similarity: {p.get('abstract_component_percent', 0)}%\n"
            f"   Abstract: {p.get('abstract_text', '')}\n\n"
        )

    fallback_explanation = (
        f"The invention was compared against candidate patents retrieved from Lens. "
        f"The top matches show an overall preliminary similarity of {overall_similarity}%. "
        f"This score was computed using TF-IDF and cosine similarity over patent titles and abstracts."
    )

    prompt = f"""
You are a patent prior-art analysis assistant.

Analyze the user's invention against the related patents below.

User invention:
Title: {data.get('title', '')}
Field: {data.get('field', '')}
Problem: {data.get('problem', '')}
Existing Solution: {data.get('existing_solution', '')}
Proposed Solution: {data.get('proposed_solution', '')}
Working: {data.get('working', '')}
Advantages: {data.get('advantages', '')}
Components: {data.get('components', '')}
Applications: {data.get('applications', '')}

Retrieved related patents:
{patents_text}

Instructions:
1. Choose ONLY one status:
   - Similar
   - Partially Similar
   - Likely Novel (Preliminary)
2. Give a single percentage.
3. Explain the overlap professionally.
4. Do not provide legal advice.

Return EXACTLY in this format:

STATUS:
...

SIMILARITY_SCORE:
...

EXPLANATION:
...
"""

    final_status = status
    final_similarity = overall_similarity
    explanation = fallback_explanation

    try:
        if Config.GEMINI_API_KEY:
            client = genai.Client(api_key=Config.GEMINI_API_KEY)

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            text = response.text if getattr(response, "text", None) else ""

            if "STATUS:" in text and "SIMILARITY_SCORE:" in text and "EXPLANATION:" in text:
                part1 = text.split("SIMILARITY_SCORE:", 1)
                parsed_status = part1[0].replace("STATUS:", "").strip()

                part2 = part1[1].split("EXPLANATION:", 1)
                parsed_score = part2[0].strip().replace("%", "")
                parsed_explanation = part2[1].strip()

                if parsed_status:
                    final_status = parsed_status

                try:
                    final_similarity = float(parsed_score)
                except Exception:
                    final_similarity = overall_similarity

                if parsed_explanation:
                    explanation = parsed_explanation
    except Exception:
        pass

    formatted_text = (
        f"STATUS: {final_status}\n"
        f"SIMILARITY_SCORE: {final_similarity}%\n"
        f"EXPLANATION: {explanation}"
    )

    return {
        "status": final_status,
        "similarity_score": final_similarity,
        "analysis_text": explanation,
        "ranked_patents": ranked_patents,
        "formatted_text": formatted_text
    }