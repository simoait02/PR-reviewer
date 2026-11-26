import { useState } from "react";
import "./App.css";
import { streamReview } from "./api/reviewApi";
import ReviewForm from "./components/ReviewForm";
import ReviewOutput from "./components/ReviewOutput";

const REVIEW_CHECKS = [
  { command: "correctness", description: "Logic errors, edge cases and regressions, read in the context of the full diff." },
  { command: "security", description: "Injection, exposed secrets and missing auth checks before they reach production." },
  { command: "impact", description: "Callers and modules affected by the change, traced through the code graph." },
  { command: "synthesize", description: "One prioritized report with explanations and patches you can apply." },
];

function App() {
  const [form, setForm] = useState({ owner: "", repo: "", prNumber: "", token: "", question: "" });
  const [summary, setSummary] = useState("");
  const [findings, setFindings] = useState([]);
  const [limitations, setLimitations] = useState([]);
  const [activityEvents, setActivityEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasRun, setHasRun] = useState(false);
  const [error, setError] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setHasRun(true);
    setError("");
    setSummary("");
    setFindings([]);
    setLimitations([]);
    setActivityEvents([]);

    try {
      await streamReview({
        form,
        onEvent: (eventName, data) => {
          if (eventName === "stream_event") {
            setActivityEvents((current) => [...current, data].slice(-8));
          } else if (eventName === "token") {
            setSummary((current) => current + data.token);
          } else if (eventName === "summary") {
            setSummary(data.summary);
          } else if (eventName === "findings") {
            setFindings((current) => [...current, data]);
          } else if (eventName === "limitations") {
            setLimitations((current) => [...current, data.limitation]);
          }
        },
      });
    } catch (requestError) {
      setError(requestError.message || "The review request failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div id="App">
      <nav className="topbar">
        <span className="logo-mark" aria-hidden="true">&gt;_</span>
        <span className="product-name">pr-reviewer</span>
      </nav>

      <section className="hero">
        <div className="hero-copy">
          <h1>
            Every pull request,<br />reviewed in depth<span className="cursor" aria-hidden="true" />
          </h1>
          <p>Point it at any GitHub pull request. Specialised agents check correctness, security and impact, then hand you one prioritized report with patches.</p>
          <pre className="hero-snippet" aria-hidden="true">
            <span className="dim">$</span> pr-reviewer octocat/Hello-World#42{"\n"}
            <span className="ok">✓</span> correctness <span className="dim">·</span> security <span className="dim">·</span> impact{"\n"}
            <span className="warn">!</span> findings ranked by severity{"\n"}
            <span className="ok">✓</span> patches ready to apply
          </pre>
        </div>
        <ReviewForm form={form} loading={loading} onChange={handleChange} onSubmit={handleSubmit} />
      </section>

      <main className="shell">
        {hasRun && (
          <ReviewOutput
            loading={loading}
            summary={summary}
            findings={findings}
            limitations={limitations}
            activityEvents={activityEvents}
            error={error}
            pullRequestLabel={`${form.owner}/${form.repo}#${form.prNumber}`}
          />
        )}

        <section className="features">
          <h2><span className="dim">#</span> how it works</h2>
          <div className="feature-grid">
            {REVIEW_CHECKS.map((check, index) => (
              <article className="feature" key={check.command}>
                <span className="feature-index">0{index + 1}</span>
                <h3>{check.command}</h3>
                <p>{check.description}</p>
              </article>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
