"use client";

import { useState, useRef, useEffect } from "react";

interface Message {
    role: "user" | "assistant";
    content: string;
    sources?: { source: string; distance: number }[];
}

const QUICK_PROMPTS = [
    "Why should I hire Ayaan?",
    "What projects has he built?",
    "What's his tech stack?",
    "Tell me about his GitHub repos",
    "Book an interview",
];

function TypingIndicator() {
    return (
        <div className="fade-in" style={{ display: "flex", gap: "12px", alignItems: "flex-start", padding: "4px 0" }}>
            <div style={{
                width: 32, height: 32, borderRadius: "50%",
                background: "linear-gradient(135deg, #5c6ef8, #8b5cf6)",
                display: "flex", alignItems: "center", justifyContent: "center",
                flexShrink: 0, fontSize: 14, color: "white", fontWeight: 600
            }}>A</div>
            <div style={{
                background: "var(--ai-bubble)", borderRadius: "4px 16px 16px 16px",
                padding: "12px 16px", display: "flex", gap: 5, alignItems: "center"
            }}>
                <div className="typing-dot" />
                <div className="typing-dot" />
                <div className="typing-dot" />
            </div>
        </div>
    );
}

function MessageBubble({ message }: { message: Message }) {
    const isUser = message.role === "user";
    return (
        <div
            className="fade-in"
            style={{
                display: "flex",
                flexDirection: isUser ? "row-reverse" : "row",
                gap: 12,
                alignItems: "flex-start",
                padding: "2px 0",
            }}
        >
            {/* Avatar */}
            {!isUser && (
                <div style={{
                    width: 32, height: 32, borderRadius: "50%",
                    background: "linear-gradient(135deg, #5c6ef8, #8b5cf6)",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    flexShrink: 0, fontSize: 14, color: "white", fontWeight: 600,
                    boxShadow: "0 2px 8px rgba(92,110,248,0.25)"
                }}>A</div>
            )}

            <div style={{ maxWidth: "72%", display: "flex", flexDirection: "column", gap: 4 }}>
                <div style={{
                    padding: "11px 16px",
                    borderRadius: isUser ? "16px 4px 16px 16px" : "4px 16px 16px 16px",
                    background: isUser ? "var(--user-bubble)" : "var(--ai-bubble)",
                    color: isUser ? "var(--user-bubble-text)" : "var(--text-primary)",
                    fontSize: 14,
                    lineHeight: 1.65,
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                    boxShadow: isUser ? "0 2px 8px rgba(92,110,248,0.2)" : "var(--shadow-sm)",
                }}>
                    {message.content}
                </div>

                {/* Sources */}
                {!isUser && message.sources && message.sources.length > 0 && (
                    <div style={{ display: "flex", gap: 6, flexWrap: "wrap", paddingLeft: 4 }}>
                        {message.sources.slice(0, 3).map((s, i) => (
                            <span key={i} style={{
                                fontSize: 11, color: "var(--text-muted)",
                                background: "var(--surface-2)", border: "1px solid var(--border)",
                                borderRadius: 999, padding: "2px 8px",
                            }}>
                                {s.source.replace("github:", "").replace("resume.txt", "Resume")}
                            </span>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

export default function ChatWindow() {
    const [messages, setMessages] = useState<Message[]>([
        {
            role: "assistant",
            content: "Hi! I'm Ayaan's AI assistant. Ask me anything about his background, projects, or skills — or book an interview if you're interested. 👋",
        },
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [usedPrompts, setUsedPrompts] = useState<Set<string>>(new Set());
    const bottomRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, loading]);

    const sendMessage = async (text: string) => {
        const trimmed = text.trim();
        if (!trimmed || loading) return;

        const userMsg: Message = { role: "user", content: trimmed };
        setMessages((prev) => [...prev, userMsg]);
        setInput("");
        setLoading(true);

        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: trimmed,
                    history: messages.map((m) => ({ role: m.role, content: m.content })),
                }),
            });

            if (!res.ok) throw new Error(`Error ${res.status}`);
            const data = await res.json();

            setMessages((prev) => [
                ...prev,
                { role: "assistant", content: data.reply, sources: data.sources },
            ]);
        } catch (err) {
            setMessages((prev) => [
                ...prev,
                { role: "assistant", content: "Sorry, I ran into an issue. Please try again in a moment." },
            ]);
        } finally {
            setLoading(false);
            setTimeout(() => inputRef.current?.focus(), 50);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage(input);
        }
    };

    const handleChip = (prompt: string) => {
        setUsedPrompts((prev) => new Set(prev).add(prompt));
        sendMessage(prompt);
    };

    const availableChips = QUICK_PROMPTS.filter((p) => !usedPrompts.has(p));

    return (
        <div style={{
            display: "flex",
            flexDirection: "column",
            height: "100%",
            background: "var(--surface)",
            overflow: "hidden",
        }}>
            {/* Messages area */}
            <div style={{
                flex: 1,
                overflowY: "auto",
                padding: "24px 24px 8px",
                display: "flex",
                flexDirection: "column",
                gap: 16,
            }}>
                {messages.map((msg, i) => (
                    <MessageBubble key={i} message={msg} />
                ))}
                {loading && <TypingIndicator />}
                <div ref={bottomRef} />
            </div>

            {/* Quick prompts */}
            {availableChips.length > 0 && messages.length < 3 && (
                <div style={{
                    padding: "8px 24px",
                    display: "flex",
                    gap: 8,
                    overflowX: "auto",
                    scrollbarWidth: "none",
                    borderTop: "1px solid var(--border)",
                    background: "var(--surface)",
                }}>
                    {availableChips.map((prompt) => (
                        <button
                            key={prompt}
                            className="chip"
                            onClick={() => handleChip(prompt)}
                            disabled={loading}
                        >
                            {prompt}
                        </button>
                    ))}
                </div>
            )}

            {/* Input area */}
            <div style={{
                padding: "16px 24px 20px",
                borderTop: "1px solid var(--border)",
                background: "var(--surface)",
            }}>
                <div style={{
                    display: "flex",
                    gap: 10,
                    alignItems: "flex-end",
                    background: "var(--surface-2)",
                    border: "1.5px solid var(--border)",
                    borderRadius: 14,
                    padding: "10px 10px 10px 16px",
                    transition: "border-color 0.15s",
                }}
                    onFocusCapture={(e) => (e.currentTarget.style.borderColor = "var(--accent)")}
                    onBlurCapture={(e) => (e.currentTarget.style.borderColor = "var(--border)")}
                >
                    <textarea
                        ref={inputRef}
                        value={input}
                        onChange={(e) => {
                            setInput(e.target.value);
                            e.target.style.height = "auto";
                            e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px";
                        }}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask about Ayaan's background, projects, or book an interview..."
                        rows={1}
                        disabled={loading}
                        style={{
                            flex: 1,
                            border: "none",
                            outline: "none",
                            background: "transparent",
                            fontSize: 14,
                            color: "var(--text-primary)",
                            resize: "none",
                            lineHeight: 1.5,
                            fontFamily: "inherit",
                            maxHeight: 120,
                            minHeight: 22,
                            overflowY: "auto",
                        }}
                    />
                    <button
                        className="btn-primary"
                        onClick={() => sendMessage(input)}
                        disabled={loading || !input.trim()}
                        style={{ borderRadius: 10, padding: "8px 14px", flexShrink: 0, minWidth: 40 }}
                    >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                            <line x1="22" y1="2" x2="11" y2="13" />
                            <polygon points="22 2 15 22 11 13 2 9 22 2" />
                        </svg>
                    </button>
                </div>
                <p style={{ fontSize: 11, color: "var(--text-muted)", textAlign: "center", marginTop: 8 }}>
                    Powered by Gemini · RAG-grounded on real resume &amp; GitHub
                </p>
            </div>
        </div>
    );
}
