"use client";

import { useMemo, useState } from "react";
import StatCard from "../components/StatCard";
import { api } from "../lib/api";

type Tab = "admet" | "protein" | "dti" | "rag" | "assistant";

const tabs: { key: Tab; title: string; subtitle: string }[] = [
  { key: "admet", title: "Molecular Property Predictor", subtitle: "SMILES → ADMET-style profile" },
  { key: "protein", title: "Protein Sequence Analyzer", subtitle: "Sequence → bioinformatics summary" },
  { key: "dti", title: "Drug-Target Interaction", subtitle: "SMILES + protein → interaction score" },
  { key: "rag", title: "Biomedical Literature RAG", subtitle: "Question → grounded evidence retrieval" },
  { key: "assistant", title: "AI Research Assistant", subtitle: "Single prompt → routed tool response" }
];

export default function HomePage() {
  const [tab, setTab] = useState<Tab>("admet");
  const [smiles, setSmiles] = useState("CC(=O)OC1=CC=CC=C1C(=O)O");
  const [sequence, setSequence] = useState("MKWVTFISLLFLFSSAYSRGVFRRDAHKSEVAHRFKDLGE");
  const [ragQuery, setRagQuery] = useState("What do recent papers say about transformers in drug discovery?");
  const [assistantQuery, setAssistantQuery] = useState(
    "Analyze this molecule CCO and tell me whether it looks BBB permeable."
  );
  const [result, setResult] = useState<string>("Run a module to see output here.");
  const [loading, setLoading] = useState(false);

  const currentTab = useMemo(() => tabs.find((t) => t.key === tab), [tab]);

  async function runCurrent() {
    setLoading(true);
    try {
      let res: unknown;
      if (tab === "admet") res = await api.admet(smiles);
      if (tab === "protein") res = await api.protein(sequence);
      if (tab === "dti") res = await api.dti(smiles, sequence);
      if (tab === "rag") res = await api.rag(ragQuery, 3);
      if (tab === "assistant") res = await api.assistant(assistantQuery);
      setResult(JSON.stringify(res, null, 2));
    } catch (error) {
      setResult(error instanceof Error ? error.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page-shell">
      <section className="hero">
        <span className="pill">Portfolio-grade AI x Biotech</span>
        <h1>GenomicAI — Drug Discovery Platform</h1>
        <p className="hero-copy">
          A full-stack MVP that combines molecular analysis, biomedical retrieval, protein intelligence,
          and drug-target scoring in one product.
        </p>

        <div className="stats-grid">
          <StatCard value="5" label="AI modules" />
          <StatCard value="1" label="FastAPI backend" />
          <StatCard value="1" label="Next.js app" />
          <StatCard value="Ready" label="Local execution" />
        </div>
      </section>

      <section className="panel">
        <div className="tab-row">
          {tabs.map((item) => (
            <button
              key={item.key}
              className={tab === item.key ? "tab active" : "tab"}
              onClick={() => setTab(item.key)}
            >
              <strong>{item.title}</strong>
              <span>{item.subtitle}</span>
            </button>
          ))}
        </div>

        <div className="module-card">
          <div className="module-header">
            <div>
              <h2>{currentTab?.title}</h2>
              <p className="muted">{currentTab?.subtitle}</p>
            </div>
            <button className="primary-btn" onClick={runCurrent} disabled={loading}>
              {loading ? "Running..." : "Run module"}
            </button>
          </div>

          {(tab === "admet" || tab === "dti") && (
            <div className="field-block">
              <label>SMILES</label>
              <textarea value={smiles} onChange={(e) => setSmiles(e.target.value)} rows={3} />
            </div>
          )}

          {(tab === "protein" || tab === "dti") && (
            <div className="field-block">
              <label>Protein sequence</label>
              <textarea value={sequence} onChange={(e) => setSequence(e.target.value)} rows={4} />
            </div>
          )}

          {tab === "rag" && (
            <div className="field-block">
              <label>Biomedical question</label>
              <textarea value={ragQuery} onChange={(e) => setRagQuery(e.target.value)} rows={4} />
            </div>
          )}

          {tab === "assistant" && (
            <div className="field-block">
              <label>Assistant prompt</label>
              <textarea
                value={assistantQuery}
                onChange={(e) => setAssistantQuery(e.target.value)}
                rows={4}
              />
            </div>
          )}
        </div>
      </section>

      <section className="output-grid">
        <div className="panel">
          
          <ul className="clean-list">
            <li>Shows product thinking, not only notebooks.</li>
            <li>Combines AI, ML systems, API engineering, and frontend delivery.</li>
            <li>Touches biotech and drug-discovery workflows recruiters recognize immediately.</li>
            <li>Easy to demo live with local execution and structured outputs.</li>
          </ul>
        </div>

        <div className="panel">
          <h3>Live output</h3>
          <pre className="output-box">{result}</pre>
        </div>
      </section>
    </main>
  );
}
