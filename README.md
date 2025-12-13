# 🏥 SRI Medical Search Engine

**Project:** Medical Information Retrieval System (Indexation & Search)

## 📋 Project Overview
This project implements a complete Information Retrieval pipeline for medical notices. It starts from raw URLs, standardizes the data, and builds an inverted index for search operations.

### 🔗 Data Source
The medical notices used in this corpus are retrieved from the official French government database:
* **Source:** [Base de données publique des médicaments](https://base-donnees-publique.medicaments.gouv.fr/)
* **Usage:** Public data scraped for educational purposes.

**Key Features:**
* **Automated Scraping:** Uses `percollate` to convert HTML notices to clean Markdown.
* **Hybrid Indexing:** Combines Regex (structural) and NLP/SpaCy (semantic) processing.
* **Reproducible Pipeline:** The entire corpus is regenerated from the source metadata.

---

## 🚀 How to Run (The Pipeline)

This project is designed to be **fully reproducible**. You do not need to download the document corpus; the code generates it for you.

### Prerequisite
* Google Colab (Recommended) or a local Python environment with Node.js installed.

### Steps to Reproduce
1.  Open `Medical_Retrieval_and_Indexing.ipynb` in Google Colab.
2.  Upload the `meta_data.json` file to the Colab runtime.
3.  **Run All Cells.**

---

## 📊 Pipeline Stages & Expected Results

When you run the notebook, the system executes the following 3 stages. Here is what you will see generated in your files:

### Stage 1: Preprocessing & ID Assignment
* **Input:** Raw `meta_data.json` (Names + URLs).
* **Process:** The script validates entries and assigns a unique, incremental ID to each document.
* **✅ Result:**
    * `meta_data.json` is **updated in-place**.
    * New field added: `"id": 1`, `"id": 2`, etc.

### Stage 2: Data Retrieval (Corpus Building)
* **Process:** The script iterates through the IDs, fetches the content using `percollate`, and cleans the Markdown.
* **✅ Result:**
    * A new folder **`med_md/`** is created.
    * Contains files named by ID: `1.md`, `2.md`, `3.md`...
    * Each file contains the clean text of the medical notice.

### Stage 3: Indexation
* **Process:**
    * **Structure Extraction:** Extracts Name and Active Substance.
    * **NLP:** Tokenizes descriptions, removes stop-words, and lemmatizes text.
* **✅ Result:**
    * **`index_inverse.json`**: The final search index (Tokens → Document IDs).
    * **`meta_data.json`**: Updated again with snippets and status logs (e.g., `"is_indexed": 1`).

---
📈 Evaluation of the Information Retrieval System (SRI)

After building the corpus and generating the TF-IDF index, the search engine was evaluated using a set of representative queries and a relevance file (qrels) defining, for each query, the documents considered relevant.

Evaluation Steps

The evaluation follows four standard steps commonly used in Information Retrieval:

1. Query Definition

A list of queries was created, covering different medication types, therapeutic classes, and clinical indications.

2. Relevance Judgments (qrels)

For each query, a set of relevant documents was selected to serve as the ground truth for evaluation.

3. Search Engine Execution

The TF-IDF vector model returns, for each query, a ranked list of documents based on cosine similarity.

4. Metrics Calculation

System performance is computed using the following IR metrics:

Precision@5

Recall@5

F1-score

Average Precision (AP)

MAP (Mean Average Precision)

## 📂 Repository Structure

```text
├── Medical_Retrieval_and_Indexing.ipynb  # Main pipeline code
├── meta_data.json                        # Raw seed data (URLs)
└── README.md                             # Documentation
```

---

## 📂 Data Structure

### Enriched Metadata (`meta_data.json`)
After running the pipeline, the `meta_data.json` file is enriched with extracted information. This serves as the **database** for the search interface.

**Example Entry:**
```json
{
  "id": 1,
  "url": "[https://base-donnees-publique.medicaments.gouv.fr/medicament/](https://base-donnees-publique.medicaments.gouv.fr/medicament/)...",
  "nom": "AMOXICILLINE BIOGARAN 1 g",
  "snippet": "Ce médicament est indiqué dans le traitement des infections bactériennes à germes sensibles...",
  "image_url": "[https://placehold.co/600x400/0ea5e9/white?text=A](https://placehold.co/600x400/0ea5e9/white?text=A)",
  "is_indexed": 1,
  "log": "indexed"
}
```
**Field Descriptions:**
* **`id`** *(int)*: The unique primary key for the document. This matches the filename in the corpus (e.g., `id: 1` corresponds to `med_md/1.md`).
* **`url`** *(string)*: The original source URL from *base-donnees-publique.medicaments.gouv.fr*.
* **`nom`** *(string)*: The official medication name extracted via Regex from the notice header.
* **`snippet`** *(string)*: A truncated version (first 200 chars) of the "Description" block, intended for displaying search result previews.
* **`image_url`** *(string)*: A generated placeholder URL (using the first letter of the name) to be used as a thumbnail in the user interface.
* **`is_indexed`** *(int)*: A status flag indicating indexing success (`1` = Success, `0` = Failed/Skipped).
* **`log`** *(string)*: A message detailing the indexing status or any error encountered (e.g., "indexed", "File not found").

## 📂 Backend and Frontend Contribution
## General Description
The backend is a REST API developed with Flask.
It implements an information retrieval search engine based on the TF-IDF model, applied to medication leaflets.
The system allows:
* **loading a pre-trained TF-IDF model**
* **textual search using cosine similarity**
* **returning results ranked by relevance**
* **exposing data through REST endpoints**

## Backend Architecture
* **app.py: entry point of the Flask application**
* **ri_model/: contains the saved model files (.pkl)**
* **med_md/: medical documents in Markdown format**
* **meta_data.json: descriptive information about medications**

**Exposed Endpoints**
**1. API Verification**
```
GET /
```
**Response:**
```
{
  "status": "running",
  "version": "2.0.0"
}
```
**2. Medication Search**
```
POST /api/search
```
**Request body:**
```
{
  "query": "doliprane",
  "top_k": 5
}
```
**Response:**
```
{
  "query": "doliprane",
  "results": [
    {
      "id": "1",
      "nom": "Doliprane",
      "score": 0.87,
      "snippet": "...",
      "url": "https://medicaments.gouv.fr"
    }
  ],
  "total_results": 5,
  "search_time": 0.032
}
```
**3. System Statistics**
```
GET /api/stats
```
**4. Complete Medication List**
```
GET /api/medicaments
```
## Running the Backend
**Prerequisites:**
* **Python 3.9+**
* **pip**

**Installation:**
```
pip install flask flask-cors nltk joblib
```
**Launch:**
```
python app.py
```
**The server starts on:**
```
http://localhost:5000
```
## 🎨 Frontend – React Application (User Interface)
## General Description
The frontend is a React application that consumes the Flask API.
It provides a modern interface allowing users to search for medications in an intuitive way.
**Features:**
dynamic query input**
* **REST API calls**
* **display of results with relevance score**
* **highlighting of searched terms**
* **error handling and loading states**

**Frontend / Backend Communication**
**Called URL:**
```
POST http://127.0.0.1:5000/api/search
```
**Data is exchanged in JSON format.**

**Running the Frontend**
**Prerequisites:**
* **Node.js 18+**
* **npm or yarn**

**Installation:**
```
npm install
```
**Launch:**
```
npm run dev
```

## Result
The complete system enables efficient and relevant search within a medication database by combining an information retrieval search engine on the backend and a modern user interface on the frontend.
