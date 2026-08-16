"use client";

import { useState } from "react";

const initialForm = {
  pclass: "3",
  sex: "male",
  age: "29",
  fare: "14",
  sibsp: "0",
  parch: "0",
  embarked: "S",
};

export default function Home() {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pclass: Number(form.pclass),
          sex: form.sex,
          age: Number(form.age),
          fare: Number(form.fare),
          sibsp: Number(form.sibsp),
          parch: Number(form.parch),
          embarked: form.embarked,
          title: form.sex === "male" ? "Mr" : "Mrs",
        }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.error || `Request failed (${res.status})`);
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Something went wrong calling the model.");
    } finally {
      setLoading(false);
    }
  }

  const pct = result ? Math.round(result.survival_probability * 100) : 0;

  return (
    <main className="max-w-xl mx-auto px-5 py-12">
      <p className="text-center text-xs tracking-[0.24em] uppercase text-brass font-mono mb-2">
        White Star Line · Passenger Manifest
      </p>
      <h1 className="text-center font-display font-black text-3xl md:text-4xl mb-2">
        Would You Have Survived?
      </h1>
      <p className="text-center text-sm text-ivory/60 mb-10 leading-relaxed">
        This form calls a real trained model running on the server — not a
        client-side guess.
      </p>

      <form
        onSubmit={handleSubmit}
        className="bg-navy2 border border-white/10 rounded-2xl p-7"
      >
        <div className="grid grid-cols-2 gap-4 mb-4">
          <Field label="Class of travel">
            <select
              value={form.pclass}
              onChange={(e) => update("pclass", e.target.value)}
              className="input"
            >
              <option value="1">1st class</option>
              <option value="2">2nd class</option>
              <option value="3">3rd class</option>
            </select>
          </Field>
          <Field label="Sex">
            <select
              value={form.sex}
              onChange={(e) => update("sex", e.target.value)}
              className="input"
            >
              <option value="female">Female</option>
              <option value="male">Male</option>
            </select>
          </Field>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <Field label="Age (years)">
            <input
              type="number"
              min="0"
              max="100"
              value={form.age}
              onChange={(e) => update("age", e.target.value)}
              className="input"
            />
          </Field>
          <Field label="Fare paid (£)">
            <input
              type="number"
              min="0"
              max="600"
              value={form.fare}
              onChange={(e) => update("fare", e.target.value)}
              className="input"
            />
          </Field>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <Field label="Siblings / spouse aboard">
            <input
              type="number"
              min="0"
              max="10"
              value={form.sibsp}
              onChange={(e) => update("sibsp", e.target.value)}
              className="input"
            />
          </Field>
          <Field label="Parents / children aboard">
            <input
              type="number"
              min="0"
              max="10"
              value={form.parch}
              onChange={(e) => update("parch", e.target.value)}
              className="input"
            />
          </Field>
        </div>

        <div className="mb-2">
          <Field label="Port of embarkation">
            <select
              value={form.embarked}
              onChange={(e) => update("embarked", e.target.value)}
              className="input"
            >
              <option value="S">Southampton</option>
              <option value="C">Cherbourg</option>
              <option value="Q">Queenstown</option>
            </select>
          </Field>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full mt-4 py-3.5 rounded bg-brass text-navy font-mono font-bold text-xs tracking-[0.16em] uppercase disabled:opacity-60 hover:brightness-110 active:scale-[0.98] transition"
        >
          {loading ? "Consulting the model…" : "Submit to model →"}
        </button>

        {error ? (
          <p className="mt-4 text-sm text-ember font-mono">{error}</p>
        ) : null}

        {result ? (
          <div className="mt-6 pt-6 border-t border-dashed border-white/15">
            <div className="flex items-center justify-between gap-4">
              <span
                className={`font-display font-black text-xl uppercase px-4 py-2 border-[3px] rounded-md -rotate-3 inline-block ${
                  result.survived
                    ? "text-sea border-sea"
                    : "text-ember border-ember"
                }`}
              >
                {result.survived ? "Survived" : "Lost"}
              </span>
              <div className="text-right">
                <p
                  className={`font-mono text-2xl font-bold ${
                    result.survived ? "text-sea" : "text-ember"
                  }`}
                >
                  {pct}%
                </p>
                <p className="font-mono text-[10px] uppercase tracking-wider text-ivory/50">
                  survival odds
                </p>
              </div>
            </div>
            <p className="mt-4 font-mono text-[11px] text-ivory/40 text-center">
              Prediction from the trained model, served live via /api/predict.
            </p>
          </div>
        ) : null}
      </form>

      <footer className="text-center mt-8 font-mono text-[10px] text-ivory/30 tracking-wider">
        RMS TITANIC · SOUTHAMPTON → NEW YORK · APRIL 1912
      </footer>

      <style jsx global>{`
        .input {
          appearance: none;
          background: rgba(11, 30, 51, 0.55);
          border: none;
          border-bottom: 1.5px solid rgba(243, 236, 217, 0.14);
          color: #f3ecd9;
          font-size: 14.5px;
          padding: 9px 4px;
          outline: none;
          width: 100%;
          transition: border-color 0.2s ease;
        }
        .input:focus {
          border-color: #c9a227;
        }
        .input option {
          background: #13294b;
          color: #f3ecd9;
        }
      `}</style>
    </main>
  );
}

function Field({ label, children }) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="font-mono text-[10.5px] tracking-wider uppercase text-ivory/50">
        {label}
      </label>
      {children}
    </div>
  );
}
