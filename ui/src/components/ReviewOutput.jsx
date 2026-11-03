import "./ReviewOutput.css";

function DiffBlock({ patch }) {
  const cleanPatch = patch.replace(/^```diff\s*/i, "").replace(/```\s*$/, "");

  return (
    <pre className="diff-block">
      <code>
        {cleanPatch.split("\n").filter((line) => !line.startsWith("--- ") && !line.startsWith("+++ ")).map((line, index) => {
          let lineClass = "diff-context";
          if (line.startsWith("@@")) lineClass = "diff-hunk";
          else if (line.startsWith("+")) lineClass = "diff-added";
          else if (line.startsWith("-")) lineClass = "diff-removed";
          return <span className={lineClass} key={index}>{line}{"\n"}</span>;
        })}
      </code>
    </pre>
  );
}

function ReviewOutput({ status, summary, findings, limitations, error }) {
  return (
    <div className="body review-body">
      <div className="review-content">
        {status && <p className="review-status">{status}</p>}
        {error && <p className="review-error">{error}</p>}
        {summary && <p className="review-summary">{summary}</p>}
        {findings.map((finding, index) => {
          const severity = String(finding.severity ?? "info").toLowerCase();
          return (
            <article className="finding-item" key={index}>
              <h4 className={`finding-title finding-${severity}`}>
                <span className="finding-severity">{severity}</span>{" "}{finding.title}
              </h4>
              {finding.filename && <p className="finding-location">{finding.filename}{finding.line != null && `:${finding.line}`}</p>}
              <p>{finding.explanation}</p>
              <p>{finding.recommendation}</p>
              {finding.suggested_patch && <DiffBlock patch={finding.suggested_patch} />}
            </article>
          );
        })}
        {limitations.map((limitation, index) => (
          <p className="limitation" key={index}><strong>Limitation:</strong> {limitation}</p>
        ))}
      </div>
    </div>
  );
}

export default ReviewOutput;
