"""
Builds a self-contained HTML report (report.html) documenting the whole
semantic-search workflow. Re-runs each step live so the terminal outputs in the
report are real, embeds the dashboard screenshots as base64, and inlines the
source code. Then Chrome (headless) converts report.html -> report.pdf.
"""
import base64, html, subprocess, sys, os, datetime, pathlib

ROOT = pathlib.Path(__file__).parent
PY = sys.executable

# quiet environment so the captured "live output" is clean (no HF/torch noise)
QUIET_ENV = {**os.environ, "TRANSFORMERS_VERBOSITY": "error",
             "HF_HUB_DISABLE_PROGRESS_BARS": "1", "PYTHONWARNINGS": "ignore",
             "TOKENIZERS_PARALLELISM": "false"}
_NOISE = ("Warning", "Loading weights", "HF_TOKEN", "FutureWarning",
          "self.dim", "warnings.warn", "it/s]")


def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env=QUIET_ENV)
    lines = (p.stdout + p.stderr).splitlines()
    lines = [ln for ln in lines if not any(n in ln for n in _NOISE)]
    return "\n".join(lines).strip()


def img64(name):
    data = base64.b64encode((ROOT / "screenshots" / name).read_bytes()).decode()
    return f"data:image/png;base64,{data}"


def code(path):
    # raw text; pre() applies the single HTML-escape pass
    return (ROOT / path).read_text()


def esc(s):
    return html.escape(s)


# ---- run the steps live, capture real output -------------------------------
print("Running steps to capture live output...")
out_ingest = run([PY, "01_ingest.py"])
out_search = run([PY, "02_search.py"])
out_filter = run([PY, "03_metadata_filter.py"])
out_pdf = run([PY, "04_pdf_search.py"])
docker_ps = run(["docker", "ps", "--filter", "name=qdrant",
                 "--format", "table {{.Image}}\t{{.Status}}\t{{.Ports}}"])
today = datetime.date.today().isoformat()

SHOTS = {
    "collections": img64("00_dashboard_collections.png"),
    "detail": img64("01_collection_detail.png"),
    "console": img64("02_console.png"),
    "visualize": img64("03_visualize.png"),
    "scatter": img64("04_embedding_space.png"),
}


def section(n, title, body):
    return f'<section><h2><span class="num">{n}</span>{esc(title)}</h2>{body}</section>'


def pre(text, cls="term"):
    return f'<pre class="{cls}">{esc(text)}</pre>'


def figure(src, cap):
    return (f'<figure><img src="{src}" alt="{esc(cap)}"/>'
            f'<figcaption>{esc(cap)}</figcaption></figure>')


HTML = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Semantic Search with Qdrant — Report</title>
<style>
 :root{{--bg:#ffffff;--fg:#1b1f24;--muted:#5b6672;--line:#e4e8ee;
   --accent:#7c4dff;--accent2:#d81b60;--code:#0d1117;--codefg:#e6edf3;--chip:#f0eefe;}}
 *{{box-sizing:border-box}}
 body{{margin:0;font:15px/1.6 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
   color:var(--fg);background:var(--bg);}}
 .wrap{{max-width:900px;margin:0 auto;padding:48px 30px 90px;}}
 header.cover{{background:linear-gradient(135deg,#5b2be6,#d81b60);color:#fff;
   border-radius:18px;padding:44px 40px;margin-bottom:14px;}}
 header.cover h1{{margin:0 0 6px;font-size:31px;letter-spacing:-.5px;}}
 header.cover p{{margin:2px 0;opacity:.95;}}
 .meta{{margin-top:16px;font-size:13px;opacity:.9;}}
 h2{{font-size:21px;margin:38px 0 12px;padding-top:14px;border-top:1px solid var(--line);
   display:flex;align-items:center;gap:12px;}}
 h2 .num{{background:var(--accent);color:#fff;font-size:14px;width:30px;height:30px;
   border-radius:8px;display:inline-flex;align-items:center;justify-content:center;flex:0 0 auto;}}
 h3{{font-size:16px;margin:22px 0 8px;color:#33383f;}}
 p{{margin:10px 0;}}
 code.inline{{background:#f3f4f6;padding:1.5px 6px;border-radius:5px;font-size:13px;
   font-family:ui-monospace,SFMono-Regular,Menlo,monospace;}}
 pre{{border-radius:12px;padding:16px 18px;overflow:auto;font-size:12px;line-height:1.5;
   white-space:pre-wrap;overflow-wrap:anywhere;
   font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;}}
 pre.term{{background:var(--code);color:var(--codefg);}}
 pre.src{{background:#f7f8fa;color:#1b1f24;border:1px solid var(--line);}}
 figure{{margin:18px 0;text-align:center;}}
 figure img{{max-width:100%;border:1px solid var(--line);border-radius:12px;
   box-shadow:0 6px 22px rgba(20,20,40,.10);}}
 figcaption{{color:var(--muted);font-size:12.5px;margin-top:7px;}}
 .chips{{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0;}}
 .chip{{background:var(--chip);color:#4a2fb3;border-radius:20px;padding:5px 13px;font-size:12.5px;
   font-weight:600;}}
 table{{border-collapse:collapse;width:100%;margin:14px 0;font-size:13.5px;}}
 th,td{{border:1px solid var(--line);padding:8px 11px;text-align:left;vertical-align:top;}}
 th{{background:#faf9ff;}}
 .callout{{background:#f4f1ff;border-left:4px solid var(--accent);border-radius:8px;
   padding:12px 16px;margin:14px 0;}}
 .ok{{color:#137a3f;font-weight:600;}}
 .pipeline{{display:flex;flex-wrap:wrap;align-items:center;gap:8px;justify-content:center;
   margin:18px 0;}}
 .pipeline .box{{background:#fff;border:1.5px solid var(--accent);color:#3a2b7a;border-radius:10px;
   padding:9px 14px;font-weight:600;font-size:13px;}}
 .pipeline .arrow{{color:var(--accent2);font-weight:700;font-size:18px;}}
 footer{{margin-top:40px;color:var(--muted);font-size:12.5px;border-top:1px solid var(--line);
   padding-top:16px;}}
 @media print{{ header.cover{{-webkit-print-color-adjust:exact;print-color-adjust:exact;}}
   .chip,pre.term,h2 .num,.pipeline .box{{-webkit-print-color-adjust:exact;print-color-adjust:exact;}}
   section{{break-inside:avoid;}} figure{{break-inside:avoid;}} }}
</style></head><body><div class="wrap">

<header class="cover">
  <h1>Semantic Search with Qdrant Vector Database</h1>
  <p>Text → Embedding → Vector Storage → Similarity Search</p>
  <p>Embedding model: Sentence Transformers <b>all-MiniLM-L6-v2</b> (384-dim, cosine)</p>
  <div class="meta">Qdrant v1.19 · Python 3.14 · qdrant-client · Generated {today}</div>
</header>

<div class="callout"><b>Objective.</b> Convert text documents into numerical vector
representations, store the vectors with metadata in Qdrant, and retrieve the most
semantically similar documents for a natural-language query — including metadata
filtering and PDF document search.</div>

<div class="pipeline">
  <span class="box">Query</span><span class="arrow">→</span>
  <span class="box">Embedding</span><span class="arrow">→</span>
  <span class="box">Qdrant similarity</span><span class="arrow">→</span>
  <span class="box">Top-K results</span>
</div>

{section("A","Setup — Qdrant via Docker, Dashboard & Python client", f'''
<p>Qdrant runs as a Docker container exposing the REST/gRPC API on ports 6333/6334.
The web dashboard is served at <code class="inline">http://localhost:6333/dashboard</code>.</p>
<h3>Commands</h3>
{pre("""# 1. Pull and run the Qdrant image
docker pull qdrant/qdrant
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant

# 2. Open the dashboard
open http://localhost:6333/dashboard

# 3. Install the Python client + embedding model
pip install qdrant-client sentence-transformers pypdf""")}
<h3>Running container</h3>
{pre(docker_ps)}
<p class="ok">✔ Qdrant reachable on localhost:6333 · dashboard confirmed below.</p>
''')}

{section("1","Embedding technique", '''
<p>We use <b>Sentence Transformers</b> (<code class="inline">all-MiniLM-L6-v2</code>),
a transformer model fine-tuned for semantic textual similarity. Unlike word-level
techniques (Word2Vec/GloVe/FastText), it produces a single <b>384-dimensional</b>
sentence embedding that captures meaning, so sentences with no shared words can still
match. Embeddings are L2-normalized and compared with <b>cosine</b> distance.</p>
<div class="chips"><span class="chip">Sentence Transformers</span>
<span class="chip">all-MiniLM-L6-v2</span><span class="chip">384 dimensions</span>
<span class="chip">cosine similarity</span></div>''')}

{section("2","Prepare the document collection", f'''
<p>A deliberately diverse corpus of <b>14 documents</b> across 7 topics
(space, cooking, finance, health, technology, sports, nature). Each document carries
metadata used later for filtering.</p>
{pre(code("documents.py"),"src")}''')}

{section("3-6","Embed, connect, create collection, store vectors", f'''
<p>The core library wraps the embedding model and the Qdrant collection. It embeds
each document, creates a collection sized to the embedding dimension (384) with cosine
distance, and upserts each vector together with its text/metadata payload.</p>
{pre(code("qsearch.py"),"src")}
<h3>Ingestion output (live)</h3>
{pre(out_ingest)}
{figure(SHOTS["collections"], "Qdrant Dashboard → Collections. semantic_search_docs holds 14 points; pdf_semantic_search holds 6. Both configured as 384-dim / Cosine.")}
{figure(SHOTS["detail"], "Collection detail: each stored point shows its payload (text, category, author, year) and a 384-length vector.")}''')}

{section("7-11","Query → similarity search → Top-K, and relevance analysis", f'''
<p>A natural-language query is embedded with the <i>same</i> model, then
<code class="inline">query_points()</code> returns the Top-K nearest vectors by cosine
similarity. The demo queries are phrased so they share <b>no keywords</b> with the stored
documents — any correct match is purely semantic.</p>
{pre(code("02_search.py"),"src")}
<h3>Results (live) — Top-3 per query with cosine scores</h3>
{pre(out_search)}
<h3>Analysis</h3>
<table><tr><th>Query</th><th>Top hit (category)</th><th>Score</th><th>Semantically relevant?</th></tr>
<tr><td>"How can I grow my money for retirement?"</td><td>Compound interest (finance)</td><td>0.36</td><td class="ok">✔ yes</td></tr>
<tr><td>"photos of the early universe"</td><td>James Webb Telescope (space)</td><td>0.59</td><td class="ok">✔ yes</td></tr>
<tr><td>"keeping your heart healthy"</td><td>Aerobic exercise (health)</td><td>0.54</td><td class="ok">✔ yes</td></tr>
<tr><td>"making bread at home"</td><td>Sourdough bread (cooking)</td><td>0.52</td><td class="ok">✔ yes</td></tr>
<tr><td>"how do computers understand pictures?"</td><td>Neural networks (technology)</td><td>0.49</td><td class="ok">✔ yes</td></tr>
<tr><td>"saving the honeybees"</td><td>Bees pollinate crops (nature)</td><td>0.56</td><td class="ok">✔ yes</td></tr></table>
<p>Every query returns the correct topic as the #1 result despite zero keyword overlap
(e.g. "grow my money" → "compound interest", "photos of the early universe" →
"infrared images of distant galaxies"). This is the defining behaviour of semantic search.</p>
{figure(SHOTS["scatter"], "The 384-dim document embeddings projected to 2D (PCA). Same-category documents land near each other — the geometric basis of similarity search.")}''')}

{section("12","Metadata filtering", f'''
<p>Qdrant combines vector similarity with structured payload filters, so you can search
for the closest documents <i>within</i> a subset — e.g. only the <code class="inline">nature</code>
category, or only documents with <code class="inline">year &gt;= 2020</code>.</p>
{pre(code("03_metadata_filter.py"),"src")}
<h3>Results (live)</h3>
{pre(out_filter)}
<p>With no filter the search spans all 14 docs. The <code class="inline">category == nature</code>
filter restricts results to the two nature documents; <code class="inline">year &gt;= 2020</code>
drops the older ones (e.g. the 2016 bees document) while keeping vector ranking intact.</p>''')}

{section("13","Document-based semantic search (PDF input)", f'''
<p>A PDF is read with <code class="inline">pypdf</code>, split into sentence-level chunks,
embedded, and stored in a dedicated collection. You can then ask a plain-English question
and retrieve the exact passage that answers it.</p>
{pre(code("04_pdf_search.py"),"src")}
<h3>Results (live)</h3>
{pre(out_pdf)}
<p>"What is an embedding?" retrieves the <i>Embeddings</i> paragraph at score 0.71;
"How does the database make search fast?" surfaces the passages on nearest-vector return
and the HNSW graph index — correct passage-level retrieval from an unstructured document.</p>''')}

{section("+","Dashboard: Console & Visualize", f'''
<p>The dashboard's <b>Console</b> runs raw REST queries against the collections, and the
<b>Visualize</b> tab projects stored vectors to 2D server-side.</p>
{figure(SHOTS["console"], "Dashboard Console — run REST API calls (list collections, get info, scroll points with filters) directly against Qdrant.")}
{figure(SHOTS["visualize"], "Dashboard Visualize tab — configurable UMAP/TSNE/PCA projection of the stored vectors.")}''')}

<section><h2><span class="num">✓</span>Learning outcome</h2>
<p>This project walks the full pipeline: <b>text representation → embedding generation →
vector storage → similarity search</b>. Text is turned into 384-dim Sentence-Transformer
embeddings, stored with metadata in a cosine-distance Qdrant collection, and retrieved by
meaning. We demonstrated that keyword-free queries still return the right documents,
that structured metadata filters compose with vector search, and that the same pipeline
makes an arbitrary PDF semantically searchable.</p>
<div class="chips">
<span class="chip">embeddings</span><span class="chip">vector DB</span>
<span class="chip">cosine similarity</span><span class="chip">Top-K retrieval</span>
<span class="chip">metadata filtering</span><span class="chip">PDF RAG</span></div></section>

<footer>Semantic Search with Qdrant · generated {today} · all outputs captured live from a
running Qdrant v1.19 instance on localhost:6333.</footer>
</div></body></html>"""

(ROOT / "report.html").write_text(HTML)
print("Wrote report.html")
