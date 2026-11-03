import "./ReviewForm.css";

function ReviewForm({ form, loading, onChange, onSubmit }) {
  return (
    <>
      <form className="form" onSubmit={onSubmit}>
        <div className="form-group">
          <div className="field">
            <label>Repository Owner</label>
            <input name="owner" type="text" placeholder="e.g. octocat" value={form.owner} onChange={onChange} />
          </div>
          <div className="field">
            <label>Repository Name</label>
            <input name="repo" type="text" placeholder="e.g. Hello-World" value={form.repo} onChange={onChange} />
          </div>
          <div className="field">
            <label>Pull Request Number</label>
            <input name="prNumber" type="number" placeholder="e.g. 123" value={form.prNumber} onChange={onChange} />
          </div>
        </div>
        <div className="form-group">
          <div className="field">
            <label>User Question</label>
            <textarea name="question" placeholder="What would you like me to review?" value={form.question} onChange={onChange} rows="4" />
          </div>
        </div>
        <div className="form-group">
          <div className="field">
            <label>Token (Optional)</label>
            <input name="token" type="password" placeholder="GitHub token (optional)" value={form.token} onChange={onChange} />
          </div>
          <div />
          <input type="submit" value={loading ? "Reviewing..." : "Submit"} disabled={loading} />
        </div>
      </form>
      {loading && (
        <div className="processing-indicator" role="status" aria-live="polite">
          <span className="loader" aria-hidden="true" />
          <span>Reviewing pull request...</span>
        </div>
      )}
    </>
  );
}

export default ReviewForm;
