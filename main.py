# import os
# import json
# import datetime
# import fitz  # PyMuPDF
# from keybert import KeyBERT
# from sentence_transformers import SentenceTransformer

# # Initialize models
# model = SentenceTransformer("all-MiniLM-L6-v2")  # <400MB model
# kw_model = KeyBERT(model)

# # Base paths
# BASE_DIR = os.getcwd()
# OUTPUT_DIR = os.path.join(BASE_DIR, "output")


# def extract_text_by_page(pdf_path):
#     """Extract text from each page of a PDF."""
#     doc = fitz.open(pdf_path)
#     return [(i + 1, page.get_text()) for i, page in enumerate(doc) if page.get_text().strip()]


# def rank_relevance(text_pages, query, top_n=3):
#     """Rank pages by keyword relevance to the query."""
#     results = []
#     for page_num, text in text_pages:
#         keywords = kw_model.extract_keywords(
#             text,
#             keyphrase_ngram_range=(1, 3),
#             stop_words="english",
#             top_n=5
#         )
#         score = sum(1 for kw in keywords if kw[0].lower() in query.lower())
#         if score > 0:
#             results.append({"page": page_num, "text": text, "score": score})
#     return sorted(results, key=lambda x: -x["score"])[:top_n]


# def process_collection(collection_path, collection_name):
#     """Process a single collection folder."""
#     input_json = os.path.join(collection_path, "challenge1b_input.json")
#     pdf_dir = os.path.join(collection_path, "PDFs")
#     output_path = os.path.join(OUTPUT_DIR, collection_name)
#     os.makedirs(output_path, exist_ok=True)

#     with open(input_json, "r", encoding="utf-8") as f:
#         spec = json.load(f)

#     persona = spec.get("persona", "")
#     job_field = spec.get("job_to_be_done", "")
#     job = job_field if isinstance(job_field, str) else json.dumps(job_field)

#     pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")]

#     result = {
#         "metadata": {
#             "documents": pdf_files,
#             "persona": persona,
#             "job_to_be_done": job,
#             "processing_timestamp": datetime.datetime.now().isoformat()
#         },
#         "extracted_sections": [],
#         "subsection_analysis": []
#     }

#     rank = 1
#     for pdf in pdf_files:
#         pdf_path = os.path.join(pdf_dir, pdf)
#         pages = extract_text_by_page(pdf_path)
#         top_sections = rank_relevance(pages, job)

#         for section in top_sections:
#             result["extracted_sections"].append({
#                 "document": pdf,
#                 "page": section["page"],
#                 "section_title": f"Section {rank}",
#                 "importance_rank": rank
#             })
#             result["subsection_analysis"].append({
#                 "document": pdf,
#                 "page": section["page"],
#                 "refined_text": section["text"][:700]
#             })
#             rank += 1

#     # Save output JSON
#     output_json_path = os.path.join(output_path, "challenge1b_output.json")
#     with open(output_json_path, "w", encoding="utf-8") as f:
#         json.dump(result, f, indent=2)


# if __name__ == "__main__":
#     os.makedirs(OUTPUT_DIR, exist_ok=True)

#     for folder in os.listdir(BASE_DIR):
#         collection_path = os.path.join(BASE_DIR, folder)
#         if os.path.isdir(collection_path) and folder.lower().startswith("collection"):
#             process_collection(collection_path, folder)


# import os
# import json
# from datetime import datetime
# import fitz  # PyMuPDF

# # Automatically detect all collection folders
# all_collections = [d for d in os.listdir() if os.path.isdir(d) and d.startswith("Collection_")]

# BASE_OUTPUT_DIR = "./output"
# os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

# for collection in all_collections:
#     pdf_dir = os.path.join(collection, "PDFs")
#     input_json_path = os.path.join(collection, "challenge1b_input.json")
#     output_path = os.path.join(collection, "challenge1b_output.json")
#     os.makedirs(os.path.join(BASE_OUTPUT_DIR, collection), exist_ok=True)

#     # Load challenge1b_input.json
#     with open(input_json_path, "r") as f:
#         spec = json.load(f)

#     persona_data = spec.get("persona")
#     job_data = spec.get("job_to_be_done")

#     # Ensure persona and job are strings
#     persona = persona_data["role"] if isinstance(persona_data, dict) else persona_data
#     job = job_data["task"] if isinstance(job_data, dict) else job_data

#     # Read PDFs
#     pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")]

#     # Extract all text pages from PDFs and score based on presence of job-related terms
#     page_candidates = []
#     for pdf in pdf_files:
#         path = os.path.join(pdf_dir, pdf)
#         with fitz.open(path) as doc:
#             for i, page in enumerate(doc):
#                 text = page.get_text().strip().replace("\n", " ")
#                 if text:
#                     score = sum(1 for word in job.lower().split() if word in text.lower())
#                     if score > 0:
#                         page_candidates.append({
#                             "document": pdf,
#                             "page_number": i + 1,
#                             "section_title": text.split(".")[0][:100].strip(),
#                             "refined_text": text[:1000].strip(),
#                             "score": score
#                         })

#     # Sort by score and select top 5
#     sorted_pages = sorted(page_candidates, key=lambda x: -x["score"])[:5]

#     extracted_sections = []
#     subsection_analysis = []
#     for rank, page in enumerate(sorted_pages, 1):
#         extracted_sections.append({
#             "document": page["document"],
#             "section_title": page["section_title"],
#             "importance_rank": rank,
#             "page_number": page["page_number"]
#         })
#         subsection_analysis.append({
#             "document": page["document"],
#             "refined_text": page["refined_text"],
#             "page_number": page["page_number"]
#         })

#     output_json = {
#         "metadata": {
#             "input_documents": pdf_files,
#             "persona": persona,
#             "job_to_be_done": job,
#             "processing_timestamp": datetime.now().isoformat()
#         },
#         "extracted_sections": extracted_sections,
#         "subsection_analysis": subsection_analysis
#     }

#     with open(output_path, "w", encoding="utf-8") as out_f:
#         json.dump(output_json, out_f, indent=2, ensure_ascii=False)

#     print(f"✅ Processed {collection} → {len(extracted_sections)} sections written.")


# import os
# import json
# from datetime import datetime
# import fitz  # PyMuPDF

# # Configuration
# BASE_OUTPUT_DIR = "./output"
# os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

# # Helper to parse nested persona/job fields
# def parse_field(field, key):
#     if isinstance(field, dict):
#         return field.get(key, "")
#     return str(field) if field else ""

# # Process a single Collection_X folder
# def process_collection(collection_path):
#     print(f"\n-- Processing: {collection_path} --")
#     pdf_dir = os.path.join(collection_path, "PDFs")
#     input_json_path = os.path.join(collection_path, "challenge1b_input.json")
#     output_file = os.path.join(collection_path, "challenge1b_output.json")

#     if not os.path.exists(input_json_path):
#         print(f"ERROR: Input JSON not found: {input_json_path}")
#         return

#     try:
#         with open(input_json_path, 'r', encoding='utf-8') as f:
#             spec = json.load(f)
#     except Exception as e:
#         print(f"ERROR loading JSON: {e}")
#         return

#     # Parse persona and job
#     persona_field = spec.get("persona")
#     job_field = spec.get("job_to_be_done")
#     persona = parse_field(persona_field, "role")
#     job = parse_field(job_field, "task")
#     try:
#         parsed = json.loads(job)
#         if isinstance(parsed, dict) and 'task' in parsed:
#             job = parsed['task']
#     except:
#         pass

#     print(f" Persona: {persona}")
#     print(f" Job: {job}")

#     try:
#         pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
#     except Exception as e:
#         print(f"ERROR listing PDFs: {e}")
#         return

#     print(f" Found PDFs: {pdf_files}")

#     candidates = []
#     for pdf in pdf_files:
#         pdf_path = os.path.join(pdf_dir, pdf)
#         print(f"  Reading PDF: {pdf_path}")
#         try:
#             doc = fitz.open(pdf_path)
#         except Exception as e:
#             print(f"   ERROR opening PDF {pdf}: {e}")
#             continue
#         for i, page in enumerate(doc):
#             text = page.get_text().strip().replace("\n", " ")
#             if not text:
#                 continue
#             score = sum(text.lower().count(w.lower()) for w in job.lower().split())
#             candidates.append({
#                 'document': pdf,
#                 'page': i + 1,
#                 'text': text,
#                 'score': score
#             })

#     print(f" Total pages scanned: {len(candidates)}")
#     ranked = sorted(candidates, key=lambda x: -x['score'])
#     top = ranked[:5] if ranked else []

#     result = {
#         'metadata': {
#             'input_documents': pdf_files,
#             'persona': persona,
#             'job_to_be_done': job,
#             'processing_timestamp': datetime.now().isoformat()
#         },
#         'extracted_sections': [],
#         'subsection_analysis': []
#     }

#     seen = set()
#     rank = 1
#     for c in top:
#         key = (c['document'], c['page'])
#         if key in seen:
#             continue
#         seen.add(key)
#         title = c['text'].split('. ')[0]
#         result['extracted_sections'].append({
#             'document': c['document'],
#             'section_title': title[:120],
#             'importance_rank': rank,
#             'page_number': c['page']
#         })
#         result['subsection_analysis'].append({
#             'document': c['document'],
#             'refined_text': c['text'][:800],
#             'page_number': c['page']
#         })
#         rank += 1

#     try:
#         with open(output_file, 'w', encoding='utf-8') as f:
#             json.dump(result, f, indent=2)
#         print(f"✅ Output saved to: {output_file}")
#     except Exception as e:
#         print(f"ERROR writing output JSON: {e}")


# if __name__ == '__main__':
#     cwd = os.getcwd()
#     found = False
#     for folder in os.listdir(cwd):
#         collection_path = os.path.join(cwd, folder)
#         if os.path.isdir(collection_path) and folder.lower().startswith("collection"):
#             found = True
#             process_collection(collection_path)
#     if not found:
#         # fallback: process current directory as a collection folder
#         print("No Collection_ folders found; processing current directory as collection.")
#         process_collection(cwd)













# import os
# import json
# from datetime import datetime
# import fitz  # PyMuPDF

# # Configuration
# BASE_OUTPUT_DIR = "./output"
# os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

# # Helper to parse nested persona/job fields
# def parse_field(field, key):
#     if isinstance(field, dict):
#         return field.get(key, "")
#     return str(field) if field else ""

# # Process a single Collection_X folder
# def process_collection(collection_path):
#     print(f"\n-- Processing: {collection_path} --")
#     pdf_dir = os.path.join(collection_path, "PDFs")
#     input_json_path = os.path.join(collection_path, "challenge1b_input.json")

#     if not os.path.exists(input_json_path):
#         print(f"ERROR: Input JSON not found: {input_json_path}")
#         return

#     try:
#         with open(input_json_path, 'r', encoding='utf-8') as f:
#             spec = json.load(f)
#     except Exception as e:
#         print(f"ERROR loading JSON: {e}")
#         return

#     # Parse persona and job
#     persona_field = spec.get("persona")
#     job_field = spec.get("job_to_be_done")
#     persona = parse_field(persona_field, "role")
#     job = parse_field(job_field, "task")
#     try:
#         parsed = json.loads(job)
#         if isinstance(parsed, dict) and 'task' in parsed:
#             job = parsed['task']
#     except:
#         pass

#     print(f" Persona: {persona}")
#     print(f" Job: {job}")

#     try:
#         pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
#     except Exception as e:
#         print(f"ERROR listing PDFs: {e}")
#         return

#     print(f" Found PDFs: {pdf_files}")

#     candidates = []
#     for pdf in pdf_files:
#         pdf_path = os.path.join(pdf_dir, pdf)
#         print(f"  Reading PDF: {pdf_path}")
#         try:
#             doc = fitz.open(pdf_path)
#         except Exception as e:
#             print(f"   ERROR opening PDF {pdf}: {e}")
#             continue
#         for i, page in enumerate(doc):
#             text = page.get_text().strip().replace("\n", " ")
#             if not text:
#                 continue
#             score = sum(text.lower().count(w.lower()) for w in job.lower().split())
#             candidates.append({
#                 'document': pdf,
#                 'page': i + 1,
#                 'text': text,
#                 'score': score
#             })

#     print(f" Total pages scanned: {len(candidates)}")
#     ranked = sorted(candidates, key=lambda x: -x['score'])
#     top = ranked[:5] if ranked else []

#     result = {
#         'metadata': {
#             'input_documents': pdf_files,
#             'persona': persona,
#             'job_to_be_done': job,
#             'processing_timestamp': datetime.now().isoformat()
#         },
#         'extracted_sections': [],
#         'subsection_analysis': []
#     }

#     seen = set()
#     rank = 1
#     for c in top:
#         key = (c['document'], c['page'])
#         if key in seen:
#             continue
#         seen.add(key)
#         title = c['text'].split('. ')[0]
#         result['extracted_sections'].append({
#             'document': c['document'],
#             'section_title': title[:120],
#             'importance_rank': rank,
#             'page_number': c['page']
#         })
#         result['subsection_analysis'].append({
#             'document': c['document'],
#             'refined_text': c['text'][:800],
#             'page_number': c['page']
#         })
#         rank += 1

#     collection_name = os.path.basename(collection_path)
#     output_collection_dir = os.path.join(BASE_OUTPUT_DIR, collection_name)
#     os.makedirs(output_collection_dir, exist_ok=True)
#     output_file = os.path.join(output_collection_dir, "challenge1b_output.json")

#     try:
#         with open(output_file, 'w', encoding='utf-8') as f:
#             json.dump(result, f, indent=2)
#         print(f"✅ Output saved to: {output_file}")
#     except Exception as e:
#         print(f"ERROR writing output JSON: {e}")


# if __name__ == '__main__':
#     cwd = os.getcwd()
#     for folder in os.listdir(cwd):
#         collection_path = os.path.join(cwd, folder)
#         if os.path.isdir(collection_path) and folder.lower().startswith("collection"):
#             process_collection(collection_path)






















# import os
# import json
# from datetime import datetime
# import fitz  # PyMuPDF

# # Configuration
# BASE_OUTPUT_DIR = "./output"
# os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

# # Helper to parse nested persona/job fields
# def parse_field(field, key):
#     if isinstance(field, dict):
#         return field.get(key, "")
#     return str(field) if field else ""

# # Process a single Collection_X folder
# def process_collection(collection_path):
#     pdf_dir = os.path.join(collection_path, "PDFs")
#     input_json_path = os.path.join(collection_path, "challenge1b_input.json")
#     collection_name = os.path.basename(collection_path)
#     output_dir = os.path.join(BASE_OUTPUT_DIR, collection_name)
#     os.makedirs(output_dir, exist_ok=True)
#     output_file = os.path.join(output_dir, "challenge1b_output.json")

#     if not os.path.exists(input_json_path):
#         return

#     try:
#         with open(input_json_path, 'r', encoding='utf-8') as f:
#             spec = json.load(f)
#     except Exception:
#         return

#     # Parse persona and job
#     persona_field = spec.get("persona")
#     job_field = spec.get("job_to_be_done")
#     persona = parse_field(persona_field, "role")
#     job = parse_field(job_field, "task")
#     try:
#         parsed = json.loads(job)
#         if isinstance(parsed, dict) and 'task' in parsed:
#             job = parsed['task']
#     except:
#         pass

#     try:
#         pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
#     except Exception:
#         return

#     candidates = []
#     for pdf in pdf_files:
#         pdf_path = os.path.join(pdf_dir, pdf)
#         try:
#             doc = fitz.open(pdf_path)
#         except Exception:
#             continue
#         for i, page in enumerate(doc):
#             text = page.get_text().strip().replace("\n", " ")
#             if not text:
#                 continue
#             score = sum(text.lower().count(w.lower()) for w in job.lower().split())
#             candidates.append({
#                 'document': pdf,
#                 'page': i + 1,
#                 'text': text,
#                 'score': score
#             })

#     ranked = sorted(candidates, key=lambda x: -x['score'])
#     top = ranked[:5] if ranked else []

#     result = {
#         'metadata': {
#             'input_documents': pdf_files,
#             'persona': persona,
#             'job_to_be_done': job,
#             'processing_timestamp': datetime.now().isoformat()
#         },
#         'extracted_sections': [],
#         'subsection_analysis': []
#     }

#     seen = set()
#     rank = 1
#     for c in top:
#         key = (c['document'], c['page'])
#         if key in seen:
#             continue
#         seen.add(key)
#         title = c['text'].split('. ')[0]
#         result['extracted_sections'].append({
#             'document': c['document'],
#             'section_title': title[:120],
#             'importance_rank': rank,
#             'page_number': c['page']
#         })
#         result['subsection_analysis'].append({
#             'document': c['document'],
#             'refined_text': c['text'][:800],
#             'page_number': c['page']
#         })
#         rank += 1

#     try:
#         with open(output_file, 'w', encoding='utf-8') as f:
#             json.dump(result, f, indent=2)
#     except Exception:
#         pass

# if __name__ == '__main__':
#     cwd = os.getcwd()
#     for folder in os.listdir(cwd):
#         collection_path = os.path.join(cwd, folder)
#         if os.path.isdir(collection_path) and folder.lower().startswith("collection"):
#             process_collection(collection_path)






# import os
# import json
# from datetime import datetime
# import fitz  # PyMuPDF

# # Configuration
# BASE_OUTPUT_DIR = "./output"
# os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

# # Helper to parse nested persona/job fields
# def parse_field(field, key):
#     if isinstance(field, dict):
#         return field.get(key, "")
#     return str(field) if field else ""

# # Process a single Collection_X folder
# def process_collection(collection_path):
#     pdf_dir = os.path.join(collection_path, "PDFs")
#     input_json_path = os.path.join(collection_path, "challenge1b_input.json")
#     collection_name = os.path.basename(collection_path)
#     output_file = os.path.join(BASE_OUTPUT_DIR, collection_name, "challenge1b_output.json")
#     os.makedirs(os.path.dirname(output_file), exist_ok=True)

#     if not os.path.exists(input_json_path):
#         return

#     try:
#         with open(input_json_path, 'r', encoding='utf-8') as f:
#             spec = json.load(f)
#     except Exception:
#         return

#     # Parse persona and job
#     persona_field = spec.get("persona")
#     job_field = spec.get("job_to_be_done")
#     persona = parse_field(persona_field, "role")
#     job = parse_field(job_field, "task")
#     try:
#         parsed = json.loads(job)
#         if isinstance(parsed, dict) and 'task' in parsed:
#             job = parsed['task']
#     except:
#         pass

#     try:
#         pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
#     except Exception:
#         return

#     candidates = []
#     for pdf in pdf_files:
#         pdf_path = os.path.join(pdf_dir, pdf)
#         try:
#             doc = fitz.open(pdf_path)
#         except Exception:
#             continue
#         for i, page in enumerate(doc):
#             text = page.get_text().strip().replace("\n", " ")
#             if not text:
#                 continue
#             score = sum(text.lower().count(w.lower()) for w in job.lower().split())
#             candidates.append({
#                 'document': pdf,
#                 'page': i + 1,
#                 'text': text,
#                 'score': score
#             })

#     ranked = sorted(candidates, key=lambda x: -x['score'])
#     top = ranked[:5] if ranked else []

#     result = {
#         'metadata': {
#             'input_documents': pdf_files,
#             'persona': persona,
#             'job_to_be_done': job,
#             'processing_timestamp': datetime.now().isoformat()
#         },
#         'extracted_sections': [],
#         'subsection_analysis': []
#     }

#     seen = set()
#     rank = 1
#     for c in top:
#         key = (c['document'], c['page'])
#         if key in seen:
#             continue
#         seen.add(key)
#         title = c['text'].split('. ')[0]
#         result['extracted_sections'].append({
#             'document': c['document'],
#             'section_title': title[:120],
#             'importance_rank': rank,
#             'page_number': c['page']
#         })
#         result['subsection_analysis'].append({
#             'document': c['document'],
#             'refined_text': c['text'][:800],
#             'page_number': c['page']
#         })
#         rank += 1

#     try:
#         with open(output_file, 'w', encoding='utf-8') as f:
#             json.dump(result, f, indent=2, ensure_ascii=False)
#     except Exception:
#         pass


# if __name__ == '__main__':
#     cwd = os.getcwd()
#     for folder in os.listdir(cwd):
#         collection_path = os.path.join(cwd, folder)
#         if os.path.isdir(collection_path) and folder.lower().startswith("collection"):
#             process_collection(collection_path)






import os
import json
from datetime import datetime
import fitz  # PyMuPDF
import re

BASE_DIR = os.getcwd()

# Any folder starting with this prefix will be treated as a collection.
COLLECTION_PREFIX = "collection"

# Regular expressions to detect bullet characters and stray “o ” markers
BULLET_REGEX   = re.compile(r'[\u2022\u2023\u25E6\u2043\u2219•◦▪–—]+')
O_BULLET_REGEX = re.compile(r'^\s*o\s+', re.IGNORECASE)

def clean_text(text: str) -> str:
    """
    1) Replace any bullet‐like character with a standard dot '.'
    2) Drop leading 'o ' bullet artifacts
    3) Collapse multiple whitespace characters
    """
    # Replace all bullet characters with a dot
    text = BULLET_REGEX.sub('.', text)

    # Split into lines, strip stray 'o ' from each
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        line = O_BULLET_REGEX.sub('', line)
        cleaned_lines.append(line.strip())

    # Join back and collapse whitespace
    joined = ' '.join(cleaned_lines)
    return re.sub(r'\s+', ' ', joined).strip()

def parse_field(field, key: str) -> str:
    """Extract nested 'role' or 'task' if field is a dict, else string‑ify."""
    if isinstance(field, dict):
        return field.get(key, '')
    return str(field) if field else ''

def process_collection(collection_path: str):
    """
    Reads challenge1b_input.json and all PDFs under <collection>/PDFs,
    extracts top‑5 relevant pages, cleans bullet characters, and writes
    challenge1b_output.json under <collection>/output.
    """
    pdf_dir    = os.path.join(collection_path, "PDFs")
    input_json = os.path.join(collection_path, "challenge1b_input.json")
    output_dir = os.path.join(collection_path, "output")
    output_json= os.path.join(output_dir, "challenge1b_output.json")

    if not os.path.isfile(input_json):
        return

    os.makedirs(output_dir, exist_ok=True)

    # Load specification
    with open(input_json, 'r', encoding='utf-8') as f:
        spec = json.load(f)

    # Persona and job
    persona = parse_field(spec.get("persona"), "role")
    job_str = parse_field(spec.get("job_to_be_done"), "task")
    # Unwrap JSON-encoded string if needed
    try:
        decoded = json.loads(job_str)
        if isinstance(decoded, dict) and 'task' in decoded:
            job_str = decoded['task']
    except Exception:
        pass

    # Lowercase tokens for scoring
    job_tokens = [w.lower() for w in job_str.strip().split() if w]

    # List PDFs
    try:
        pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")]
    except Exception:
        pdf_files = []

    # Score pages
    candidates = []
    for pdf in pdf_files:
        path = os.path.join(pdf_dir, pdf)
        try:
            doc = fitz.open(path)
        except:
            continue
        for i, page in enumerate(doc):
            raw = page.get_text().strip()
            if not raw:
                continue
            # simple frequency score
            score = sum(raw.lower().count(tok) for tok in job_tokens)
            cleaned = clean_text(raw)
            candidates.append({
                "document": pdf,
                "page": i+1,
                "text": cleaned,
                "score": score
            })

    # Pick top‑5 pages
    top_pages = sorted(candidates, key=lambda x: -x["score"])[:5]

    # Build result structure
    result = {
        "metadata": {
            "input_documents": pdf_files,
            "persona": persona,
            "job_to_be_done": job_str,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": [],
        "subsection_analysis": []
    }

    seen = set()
    for rank, item in enumerate(top_pages, start=1):
        key = (item["document"], item["page"])
        if key in seen:
            continue
        seen.add(key)

        # Section title = first sentence (cleaned)
        title = item["text"].split(". ")[0]
        # Subsection = up to first 800 chars
        snippet = item["text"][:800]

        result["extracted_sections"].append({
            "document": item["document"],
            "section_title": title[:120],
            "importance_rank": rank,
            "page_number": item["page"]
        })
        result["subsection_analysis"].append({
            "document": item["document"],
            "refined_text": snippet,
            "page_number": item["page"]
        })

    # Write output JSON with ensure_ascii=False
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    # Process every folder named "Collection_*"
    for name in os.listdir(BASE_DIR):
        path = os.path.join(BASE_DIR, name)
        if os.path.isdir(path) and name.lower().startswith(COLLECTION_PREFIX):
            process_collection(path)
