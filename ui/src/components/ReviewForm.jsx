import "./ReviewForm.css";

const QUESTION_SUGGESTIONS = [
  { label: "General review", question: "Review this pull request for bugs, logic errors, unhandled edge cases and regressions. Flag anything that should block the merge and suggest concrete fixes." },
  { label: "Security issues", question: "Check this pull request for security issues: injection, exposed secrets or credentials, missing authentication or authorization checks, and unsafe handling of user input." },
  { label: "Breaking changes", question: "What could this pull request break? Identify changed public APIs, function signatures or behaviours, and list the callers and modules that depend on them." },
];

function ReviewForm({ form, loading, onChange, onSubmit }) {
  function applySuggestion(suggestion) {
    onChange({ target: { name: "question", value: suggestion } });
  }

  return (
    <form className="form term" onSubmit={onSubmit}>
      <div className="term-titlebar">
        <div className="term-lights" aria-hidden="true"><span /><span /><span /></div>
        <span className="term-title">new review</span>
      </div>

      <div className="form-body">
        <div className="form-grid">
          <div className="field">
            <label htmlFor="owner">--owner</label>
            <input id="owner" name="owner" type="text" placeholder="octocat" value={form.owner} onChange={onChange} required autoComplete="off" spellCheck="false" />
          </div>
          <div className="field">
            <label htmlFor="repo">--repo</label>
            <input id="repo" name="repo" type="text" placeholder="Hello-World" value={form.repo} onChange={onChange} required autoComplete="off" spellCheck="false" />
          </div>
          <div className="field">
            <label htmlFor="prNumber">--pr</label>
            <input id="prNumber" name="prNumber" type="number" min="1" placeholder="123" value={form.prNumber} onChange={onChange} required />
          </div>
        </div>

        <div className="field">
          <label htmlFor="question">--focus</label>
          <textarea id="question" name="question" placeholder="e.g. Check error handling in the new endpoint" value={form.question} onChange={onChange} rows="3" required />
          <div className="suggestions">
            {QUESTION_SUGGESTIONS.map((suggestion) => (
              <button type="button" className="suggestion" key={suggestion.label} onClick={() => applySuggestion(suggestion.question)}>
                {suggestion.label}
              </button>
            ))}
          </div>
        </div>

        <div className="field">
          <label htmlFor="token">--token <span className="optional">optional, for private repos</span></label>
          <input id="token" name="token" type="password" placeholder="ghp_…" value={form.token} onChange={onChange} autoComplete="off" />
        </div>

        <button type="submit" className="submit-button" disabled={loading}>
          {loading ? <><span className="loader" aria-hidden="true" />reviewing…</> : <><span className="dim">$</span> run review<kbd>↵</kbd></>}
        </button>
      </div>
    </form>
  );
}

export default ReviewForm;
