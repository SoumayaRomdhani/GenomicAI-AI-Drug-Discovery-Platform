const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

async function post<T>(path: string, payload: Record<string, unknown>): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload),
    cache: "no-store"
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export const api = {
  admet: (smiles: string) => post("/predict/admet", { smiles }),
  protein: (sequence: string) => post("/analyze/protein", { sequence }),
  dti: (smiles: string, sequence: string) => post("/predict/dti", { smiles, sequence }),
  rag: (query: string, top_k = 3) => post("/rag/query", { query, top_k }),
  assistant: (query: string) => post("/assistant/query", { query })
};
