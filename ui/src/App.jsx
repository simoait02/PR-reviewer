import { useState } from "react";
import "./App.css";
import { streamReview } from "./api/reviewApi";
import ReviewForm from "./components/ReviewForm";
import ReviewOutput from "./components/ReviewOutput";

function App() {
  const [form, setForm] = useState({ owner: "", repo: "", prNumber: "", token: "", question: "" });
  const [status, setStatus] = useState("");
  const [summary, setSummary] = useState("");
  const [findings, setFindings] = useState([]);
  const [limitations, setLimitations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setStatus("");
    setSummary("");
    setFindings([]);
    setLimitations([]);

    try {
      await streamReview({
        form,
        onEvent: (eventName, data) => {
          if (eventName === "status") setStatus(data.status === "completed" ? "" : data.status);
          else if (eventName === "summary") setSummary(data.summary);
          else if (eventName === "findings") setFindings((current) => [...current, data]);
          else if (eventName === "limitations") setLimitations((current) => [...current, data.limitation]);
          else if (eventName === "done") {
            setLoading(false);
            setStatus("");
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
      <ReviewForm form={form} loading={loading} onChange={handleChange} onSubmit={handleSubmit} />
      <hr />
      <ReviewOutput status={status} summary={summary} findings={findings} limitations={limitations} error={error} />
    </div>
  );
}

export default App;
