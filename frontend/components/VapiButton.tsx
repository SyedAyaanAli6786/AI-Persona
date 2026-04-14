"use client";

import { useState, useEffect } from "react";
import Vapi from "@vapi-ai/web";

const assistantId = process.env.NEXT_PUBLIC_VAPI_ASSISTANT_ID;

export default function VapiButton() {
    const [vapi, setVapi] = useState<Vapi | null>(null);
    const [isCalling, setIsCalling] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        // Hardcoding for final verification to bypass Next.js env issues
        const publicKey = "94b8c9e0-b7ab-4c31-aae0-375f28056564";
        const vapiInstance = new Vapi(publicKey);
        setVapi(vapiInstance);

        vapiInstance.on("call-start", () => {
            setIsCalling(true);
            setIsLoading(false);
        });

        vapiInstance.on("call-end", () => {
            setIsCalling(false);
            setIsLoading(false);
        });

        vapiInstance.on("error", (error) => {
            console.error("Vapi Error:", error);
            setIsCalling(false);
            setIsLoading(false);
        });

        return () => {
            vapiInstance.stop();
        };
    }, []);

    const toggleCall = async () => {
        const assistantId = "005db3ac-1586-4822-b9fd-3a15c2240ded";

        if (!vapi) return;

        if (isCalling) {
            vapi.stop();
        } else {
            setIsLoading(true);
            try {
                await vapi.start(assistantId);
            } catch (err) {
                console.error("Failed to start call:", err);
                setIsLoading(false);
            }
        }
    };

    return (
        <button
            onClick={toggleCall}
            disabled={isLoading}
            style={{
                display: "block",
                width: "100%",
                textAlign: "center",
                background: isCalling ? "#ef4444" : "var(--accent)",
                color: "white",
                fontSize: 12,
                fontWeight: 600,
                padding: "10px",
                borderRadius: "var(--radius-sm)",
                border: "none",
                cursor: "pointer",
                boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                transition: "all 0.2s ease",
                marginBottom: 8,
            }}
        >
            {isLoading ? "Connecting..." : isCalling ? "⏹ End Call" : "🎙 Start Voice Interview"}
        </button>
    );
}
