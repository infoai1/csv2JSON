import streamlit as st
import pandas as pd
import json
import re

st.title("Verse Group → Nested JSON Converter")

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
                "text": verse_text
            })
        return verses

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
                "section_number": chunk['SectionNumber'],
                "theme_text": chunk['ThemeText'],
                "theme_title": chunk.get('ThemeTitle', None),
                "theme_summary": chunk.get('ThemeSummary', None),
                "contextual_question": json.loads(chunk['ContextualQuestion']) if pd.notna(chunk['ContextualQuestion']) else [],
                "keywords": chunk.get('Keywords', None),
                "outline": chunk.get('Outline', None),
                "embedding": json.loads(chunk['Embedding']) if pd.notna(chunk['Embedding']) else []
            })

        result.append({
            "verse_group": verse_group,
            "chapter": chapter,
            "verses": verses,
            "english_commentary": row['English Commentary'],
            "macro_analysis": {
                "themes": json.loads(row['themes']),
                "wisdom_points": json.loads(row['wisdom_points']),
                "real_life_reflections": json.loads(row['real_life_reflections']),
                "revelation_context": json.loads(row['revelation_context']),
                "outline_of_commentary": json.loads(row['outline_of_commentary']),
                "contextual_questions": json.loads(row['contextual_questions'])
            },
            "chunks": chunks
        })

    # Display and download
    st.success("✅ JSON successfully generated!")
    json_output = json.dumps(result, indent=2)
    st.download_button("📥 Download JSON", json_output, file_name="nested_verse_data.json", mime="application/json")

    with st.expander("🔍 Preview JSON"):
        st.code(json_output, language="json")
