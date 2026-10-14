"use client";

import { FormEvent, useEffect, useState } from "react";

type ChatMessage = { role: "user" | "assistant"; content: string; meta?: string };
type Escalation = { id: string; reason: string; status: string; evidence: Record<string, unknown> };

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: "assistant", content: "Hola, soy AutoAssist. Puedo ayudarte con garantías, órdenes de servicio y citas." },
  ]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState<string>();
  const [loading, setLoading] = useState(false);
  const [queue, setQueue] = useState<Escalation[]>([]);

  async function refreshQueue() {
    const response = await fetch(`${API}/api/escalations`);
    if (response.ok) setQueue(await response.json());
  }

  useEffect(() => { refreshQueue().catch(() => undefined); }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    const message = input.trim();
    if (!message || loading) return;
    setMessages((current) => [...current, { role: "user", content: message }]);
    setInput("");
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, conversation_id: conversationId }),
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail ?? "Error del servicio");
      setConversationId(body.conversation_id);
      setMessages((current) => [...current, {
        role: "assistant",
        content: body.answer,
        meta: `${body.intent} · ${Math.round(body.confidence * 100)}%${body.escalated ? " · Escalado" : ""}`,
      }]);
      if (body.escalated) await refreshQueue();
    } catch (error) {
      setMessages((current) => [...current, { role: "assistant", content: `No pude conectar con el servicio: ${error}` }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <header>
        <div><span className="eyebrow">DINAMEX · PoC</span><h1>AutoAssist</h1></div>
        <span className="status">● Sistema disponible</span>
      </header>
      <section className="grid">
        <article className="panel chat">
          <div className="panel-title"><h2>Atención al cliente</h2><p>Garantías, servicio y citas</p></div>
          <div className="messages">
            {messages.map((message, index) => (
              <div className={`message ${message.role}`} key={index}>
                <p>{message.content}</p>{message.meta && <small>{message.meta}</small>}
              </div>
            ))}
            {loading && <div className="message assistant"><p>Consultando…</p></div>}
          </div>
          <form onSubmit={submit}>
            <input value={input} onChange={(event) => setInput(event.target.value)} placeholder="Escribe tu consulta…" />
            <button disabled={loading}>Enviar</button>
          </form>
        </article>
        <aside className="panel queue">
          <div className="panel-title"><h2>Bandeja humana</h2><p>{queue.length} caso(s) con evidencia</p></div>
          {queue.length === 0 && <div className="empty">No hay escalamientos pendientes.</div>}
          {queue.map((item) => (
            <div className="case" key={item.id}>
              <div><strong>{item.reason}</strong><span>{item.status}</span></div>
              <p>{String(item.evidence.summary ?? "Sin resumen")}</p>
              <details><summary>Ver paquete de evidencia</summary><pre>{JSON.stringify(item.evidence, null, 2)}</pre></details>
            </div>
          ))}
        </aside>
      </section>
    </main>
  );
}
