import { useEffect, useRef, useState } from "react";
import "./ReviewOutput.css";

const SEVERITY_ORDER = ["blocker", "critical", "high", "medium", "low", "info"];

function cleanPatchText(patch) {
  return patch.replace(/^```diff\s*/i, "").replace(/```\s*$/, "");
}

function describeActivity({ type, name }) {
  const readableName = (name ?? "review agent").replaceAll("_", " ");
  if (type === "agent_started") return `${readableName} started`;
  if (type === "agent_finished") return `${readableName} finished`;
  if (type === "tool_started") return `Calling ${readableName}`;
  if (type === "tool_finished") return `${readableName} finished`;
  return readableName;
}

function DiffBlock({ patch }) {
  const [copied, setCopied] = useState(false);
  const cleanPatch = cleanPatchText(patch);

  async function copyPatch() {
    try {
      await navigator.clipboard.writeText(cleanPatch);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      setCopied(false);
    }
  }

  return (
    <div className="diff-wrap">
      <div className="diff-toolbar">
        <span>suggested patch</span>
        <button type="button" className="copy-button" onClick={copyPatch}>{copied ? "copied" : "copy"}</button>
      </div>
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
    </div>
  );
}

function useElapsedSeconds(running) {
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  useEffect(() => {
    if (!running) return;
    const startedAt = Date.now();
    const timer = setInterval(() => setElapsedSeconds(Math.floor((Date.now() - startedAt) / 1000)), 1000);
    return () => {
      clearInterval(timer);
      setElapsedSeconds(0);
    };
  }, [running]);
  return elapsedSeconds;
}

function FindingEntry({ finding }) {
  const severity = String(finding.severity ?? "info").toLowerCase();
  return (
    <article className={`finding sev-${severity}`}>
      <header className="finding-header">
        <span className="severity-tag">[{severity}]</span>
        <h3 className="finding-title">{finding.title}</h3>
      </header>
      {finding.filename && (
        <p className="finding-location">{finding.filename}{finding.line != null && <span className="line-number">:{finding.line}</span>}</p>
      )}
      {finding.explanation && <p className="finding-text">{finding.explanation}</p>}
      {finding.recommendation && (
        <p className="recommendation"><span className="recommendation-label">fix →</span> {finding.recommendation}</p>
      )}
      {finding.suggested_patch && <DiffBlock patch={finding.suggested_patch} />}
    </article>
  );
}

function ReviewOutput({ loading, summary, findings, limitations, activityEvents, error, pullRequestLabel }) {
  const [severityFilter, setSeverityFilter] = useState("all");
  const elapsedSeconds = useElapsedSeconds(loading);
  const resultsRef = useRef(null);

  useEffect(() => {
    if (loading) resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [loading]);

  const severityCounts = findings.reduce((counts, finding) => {
    const severity = String(finding.severity ?? "info").toLowerCase();
    counts[severity] = (counts[severity] ?? 0) + 1;
    return counts;
  }, {});
  const presentSeverities = Object.keys(severityCounts).sort((a, b) => SEVERITY_ORDER.indexOf(a) - SEVERITY_ORDER.indexOf(b));
  const visibleFindings = findings
    .filter((finding) => severityFilter === "all" || String(finding.severity ?? "info").toLowerCase() === severityFilter)
    .sort((a, b) => SEVERITY_ORDER.indexOf(String(a.severity ?? "info").toLowerCase()) - SEVERITY_ORDER.indexOf(String(b.severity ?? "info").toLowerCase()));
  const recentActivity = activityEvents.slice(-4);
  const finishedClean = !loading && !error && findings.length === 0 && summary;

  return (
    <section ref={resultsRef} className="results term" aria-live="polite">
      <div className="term-titlebar">
        <div className="term-lights" aria-hidden="true"><span /><span /><span /></div>
        <span className="term-title">review — {pullRequestLabel}</span>
      </div>

      <div className="results-body">
        <div className="results-header">
          <p className="command-line"><span className="dim">$</span> pr-reviewer {pullRequestLabel}</p>
          {loading ? (
            <span className="status-line"><span className="loader" aria-hidden="true" />running {elapsedSeconds}s</span>
          ) : !error && (
            <span className="status-line ok">✓ done</span>
          )}
        </div>

        {error && <p className="error-line"><span className="error-label">error:</span> {error}</p>}

        {loading && (
          <div className="progress-panel" aria-live="polite">
            <p className="progress-text">
              <span className="spinner-dots" aria-hidden="true" />
              <span>
                {recentActivity.length
                  ? describeActivity(recentActivity[recentActivity.length - 1])
                  : "Starting review agents"}…
              </span>
            </p>
            {recentActivity.length > 0 && (
              <ol className="activity-list">
                {recentActivity.map((activity, index) => (
                  <li key={`${activity.type}-${activity.name}-${activityEvents.length - recentActivity.length + index}`}>
                    {describeActivity(activity)}
                  </li>
                ))}
              </ol>
            )}
          </div>
        )}

        {summary && (
          <div className="summary-block">
            <span className="section-heading"># summary</span>
            <p>{summary}{loading && <span className="typing-cursor" aria-hidden="true" />}</p>
          </div>
        )}

        {findings.length > 0 && (
          <div className="severity-tabs" role="toolbar" aria-label="Filter findings by severity">
            <button type="button" className={`severity-tab ${severityFilter === "all" ? "active" : ""}`} aria-pressed={severityFilter === "all"} onClick={() => setSeverityFilter("all")}>
              all <span className="tab-count">{findings.length}</span>
            </button>
            {presentSeverities.map((severity) => (
              <button type="button" key={severity} className={`severity-tab sev-${severity} ${severityFilter === severity ? "active" : ""}`} aria-pressed={severityFilter === severity} onClick={() => setSeverityFilter(severity)}>
                {severity} <span className="tab-count">{severityCounts[severity]}</span>
              </button>
            ))}
          </div>
        )}

        <div className="findings">
          {visibleFindings.map((finding, index) => <FindingEntry finding={finding} key={`${finding.title}-${index}`} />)}
        </div>

        {finishedClean && <p className="clean-line ok">✓ no issues found in this pull request</p>}

        {limitations.length > 0 && (
          <div className="limitations">
            <span className="section-heading"># limitations</span>
            <ul>{limitations.map((limitation, index) => <li key={index}>{limitation}</li>)}</ul>
          </div>
        )}
      </div>
    </section>
  );
}

export default ReviewOutput;
