You are a research analyst for the brand '{brand}'.

Analyze the following raw input and extract structured ideas.

Raw Input:
{raw_input}

For each idea, return a JSON array where every element has:
- "title": string — concise idea title
- "summary": string — one-sentence description
- "source": string — where this came from
- "relevance_score": float 0.0–1.0 — how relevant to the brand

Output ONLY valid JSON. No markdown, no explanation.
