import streamlit as st
import pandas as pd
import json
import re
import ast
import html

st.title("📜 Verse Group → Structured JSON Generator (Cleaned Lists & Text)")

# File upload
enriched_file = st.file_uploader("Upload enriched_combined.csv", type="csv")
embedding_file = st.file_uploader("Upload csv_with_embeddings.csv", type="csv")

if enriched_file and embedding_file:
    df1 = pd.read_csv(enriched_file)
    df2 = pd.read_csv(embedding_file)

    def extract_chapter(verse_group):
        match = re.search(r'(\d+)\.\d+-\d+', verse_group)
        return int(match.group(1)) if match else None

    def split_translation(text, chapter):
        verses = []
        matches = list(re.finditer(r"(\d+)\s", text))
        for i, match in enumerate(matches):
            verse_number = int(match.group(1))
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            verse_text = text[start:end].strip().replace('\n', ' ')
            verses.append({
                "verse_number": verse_number,
                "verse_id": f"{chapter}:{verse_number}",
                "text": html.unescape(verse_text)
            })
        return verses

    def safe_parse_list(cell):
        try:
            value = ast.literal_eval(cell) if pd.notna(cell) else []
            return value if isinstance(value, list) else [str(value)]
        except Exception:
            return [str(cell)] if pd.notna(cell) else []

    result = []

    for _, row in df1.iterrows():
        verse_group = row['Verse Group']
        chapter = extract_chapter(verse_group)
        verses = split_translation(row['translation'], chapter)

        # Match chunks
        matching_chunks = df2[df2['Commentary Group'] == verse_group]
        chunks = []

        for _, chunk in matching_chunks.iterrows():
            chunks.append({
                "section_number": chunk.get('SectionNumber'),
                "theme_text": html.unescape(str(chunk.get('ThemeText')).strip()),
                "theme_title": chunk.get('ThemeTitle'),
                "theme_summary": chunk.get('ThemeSummary'),
                "contextual_question": safe_parse_list(chunk.get('ContextualQuestion')),
                "keywords": chunk.get('Keywords'),
                "outline": chunk.get('Outline'),
                "embedding": safe_parse_list(chunk.get('Embedding'))
            })

        result.append({
            "verse_group": verse_group,
            "chapter": chapter,
            "verses": verses,
            "english_commentary": html.unescape(str(row.get('English Commentary')).strip()),
            "macro_analysis": {
                "themes": safe_parse_list(row.get('themes')),
                "wisdom_points": safe_parse_list(row.get('wisdom_points')),
                "real_life_reflections": safe_parse_list(row.get('real_life_reflections')),
                "revelation_context": safe_parse_list(row.get('revelation_context')),
                "outline_of_commentary": safe_parse_list(row.get('outline_of_commentary')),
                "contextual_questions": safe_parse_list(row.get('contextual_questions')),
            },
            "chunks": chunks
        })

    json_output = json.dumps(result, indent=2)
    st.success("✅ Cleaned JSON structure created!")

    st.download_button("📥 Download Cleaned JSON", json_output, file_name="nested_output_cleaned.json", mime="application/json")

    with st.expander("🔍 Preview Cleaned JSON Output"):
        st.code(json_output, language="json")
