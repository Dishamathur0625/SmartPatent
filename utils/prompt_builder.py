def build_patent_prompt(data: dict, related_patents_text: str, drawing_description: str, prior_art_analysis: str) -> str:
    if not related_patents_text.strip():
        related_patents_text = (
            "No related patents were retrieved from Lens. "
            "Do not state that no prior art exists. "
            "Instead, write that no closely related patents were retrieved in this preliminary search."
        )

    if not drawing_description.strip():
        drawing_description = (
            "FIG. 1 schematically illustrates one embodiment of the invention and its principal components."
        )

    return f"""
You are a professional patent drafting assistant.

Write a full patent draft in formal technical and legal style.

Use these exact sections:
1. Title of the Invention
2. Cross-Reference to Related Applications
3. Field of the Invention
4. Background of the Invention (Related Art)
5. Summary of the Invention
6. Brief Description of the Drawings
7. Detailed Description of the Invention
8. Claims
9. Abstract of the Disclosure

Rules:
- Do not claim definite novelty or patentability.
- Do not overstate prior-art conclusions.
- If no earlier filing is given, write:
  "This application does not claim priority to any earlier filed application."
- Use retrieved Lens patents only in the Background / Related Art section.
- Use the supplied drawing description in the Drawings and Detailed Description sections.
- Make the claims broad but technically supported by the invention details.
- Keep the language professional and exam-ready.

Invention details:
Title: {data.get('title', '')}
Field of Technology: {data.get('field', '')}
Problem Being Solved: {data.get('problem', '')}
Existing Solutions: {data.get('existing_solution', '')}
Proposed Solution: {data.get('proposed_solution', '')}
Working of the Invention: {data.get('working', '')}
Advantages: {data.get('advantages', '')}
Components Used: {data.get('components', '')}
Possible Applications: {data.get('applications', '')}

Retrieved related patents:
{related_patents_text}

Preliminary prior-art analysis:
{prior_art_analysis}

Drawing description:
{drawing_description}
"""