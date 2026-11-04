
import { useState } from "react";

function Chatbot() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hi! I'm your Wardrobe AI fashion assistant. Ask me about outfit colours, clothing combinations, or what to wear for an occasion.",
    },
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSend(event) {
    event.preventDefault();

    const question = message.trim();

    if (!question || loading) return;

    setMessages((previous) => [
      ...previous,
      { role: "user", text: question },
    ]);
    setMessage("");
    setError("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: question }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "The assistant could not answer your question."
        );
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          text: data.reply,
        },
      ]);
    } catch (err) {
      setError(
        err.message ||
          "Could not connect to the backend. Check that FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl p-6">
      <h1 className="mb-2 text-3xl font-bold">
        AI Fashion Assistant
      </h1>

      <p className="mb-6 text-gray-600">
        Ask me about outfit colours, clothing combinations, and occasions.
      </p>

      <div className="mb-4 space-y-4 rounded-xl border p-4">
        {messages.map((item, index) => (
          <div
            key={index}
            className={
              item.role === "user"
                ? "ml-8 rounded-xl bg-blue-600 p-3 text-white"
                : "mr-8 rounded-xl bg-gray-100 p-3 text-gray-900"
            }
          >
            <p className="mb-1 text-xs font-semibold">
              {item.role === "user" ? "You" : "Wardrobe AI"}
            </p>
            <p className="whitespace-pre-wrap">{item.text}</p>
          </div>
        ))}

        {loading && (
          <p className="text-sm text-gray-500">
            Wardrobe AI is thinking...
          </p>
        )}
      </div>

      {error && (
        <p role="alert" className="mb-3 text-red-600">
          {error}
        </p>
      )}

      <form onSubmit={handleSend} className="flex gap-2">
        <input
          type="text"
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Ask about your outfit..."
          disabled={loading}
          className="min-w-0 flex-1 rounded-lg border px-4 py-3"
        />

        <button
          type="submit"
          disabled={loading || !message.trim()}
          className="rounded-lg bg-blue-600 px-5 py-3 text-white disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  );
}

export default Chatbot;
