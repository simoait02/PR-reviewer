const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";
const CORRELATION_ID_KEY = "review-correlation-id";

function getCorrelationId() {
  const storedId = sessionStorage.getItem(CORRELATION_ID_KEY);
  if (storedId) return storedId;

  const correlationId = crypto.randomUUID();
  sessionStorage.setItem(CORRELATION_ID_KEY, correlationId);
  return correlationId;
}

function parseSseEvent(eventText) {
  let eventName = "message";
  const dataLines = [];

  for (const line of eventText.split(/\r?\n/)) {
    if (line.startsWith(":")) continue;
    if (line.startsWith("event:")) eventName = line.slice(6).trim();
    if (line.startsWith("data:")) dataLines.push(line.slice(5).trim());
  }

  if (dataLines.length === 0) return null;
  return { eventName, data: JSON.parse(dataLines.join("\n")) };
}

export async function streamReview({ form, onEvent }) {
  const baseUrl = API_BASE_URL.replace(/\/+$/, "");
  const correlationId = getCorrelationId();
  const response = await fetch(`${baseUrl}/api/v1/review`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${form.token}`,
      "Content-Type": "application/json",
      Accept: "text/event-stream",
      "X-Correlation-ID": correlationId,
    },
    body: JSON.stringify({
      question: form.question,
      pull_request: {
        repository_owner: form.owner,
        repository_name: form.repo,
        pull_number: Number(form.prNumber),
      },
    }),
  });

  if (!response.ok || !response.body) {
    throw new Error(`Request failed: ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
    const events = buffer.split(/\r?\n\r?\n/);
    buffer = events.pop();

    for (const eventText of events) {
      const parsed = parseSseEvent(eventText);
      if (parsed) onEvent(parsed.eventName, parsed.data);
    }

    if (done) {
      if (buffer.trim()) {
        const parsed = parseSseEvent(buffer);
        if (parsed) onEvent(parsed.eventName, parsed.data);
      }
      break;
    }
  }
}
