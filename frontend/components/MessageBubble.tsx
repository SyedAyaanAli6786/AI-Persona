"use client";

export interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
    timestamp: Date;
    sources?: { source: string; distance: number }[];
}

interface Props {
    message: Message;
}

export default function MessageBubble({ message }: Props) {
    const isAssistant = message.role === "assistant";

    return (
        <div className={`flex items-start gap-3 msg-in ${isAssistant ? "" : "flex-row-reverse"}`}>
            {/* Avatar */}
            <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${isAssistant
                        ? "bg-gradient-to-br from-violet-500 to-blue-500"
                        : "bg-gradient-to-br from-slate-600 to-slate-500"
                    }`}
            >
                {isAssistant ? "A" : "R"}
            </div>

            <div className={`flex flex-col gap-1 max-w-[75%] ${isAssistant ? "" : "items-end"}`}>
                {/* Bubble */}
                <div
                    className={`rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${isAssistant
                            ? "glass rounded-tl-sm text-white/90"
                            : "bg-violet-600 rounded-tr-sm text-white"
                        }`}
                >
                    {message.content}
                </div>

                {/* Sources (collapsed, subtle) */}
                {isAssistant && message.sources && message.sources.length > 0 && (
                    <div className="flex gap-2 flex-wrap">
                        {message.sources.slice(0, 3).map((s, i) => (
                            <span
                                key={i}
                                className="text-[10px] text-white/25 bg-white/5 rounded-full px-2 py-0.5"
                            >
                                {s.source.split(":").pop()?.split("/").pop() ?? s.source}
                            </span>
                        ))}
                    </div>
                )}

                {/* Timestamp */}
                <span className="text-[10px] text-white/25">
                    {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </span>
            </div>
        </div>
    );
}
