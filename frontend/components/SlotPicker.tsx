"use client";

import { useState, useEffect } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Slot {
    start: string;
    label: string;
}

interface Props {
    onClose: () => void;
    onBooked: (details: string) => void;
}

type Step = "slots" | "form" | "confirming";

export default function SlotPicker({ onClose, onBooked }: Props) {
    const [slots, setSlots] = useState<Slot[]>([]);
    const [selected, setSelected] = useState<Slot | null>(null);
    const [step, setStep] = useState<Step>("slots");
    const [loading, setLoading] = useState(true);
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [error, setError] = useState("");

    useEffect(() => {
        fetch(`${API_URL}/slots`)
            .then((r) => r.json())
            .then((d) => { setSlots(d.slots ?? []); setLoading(false); })
            .catch(() => { setError("Could not fetch slots."); setLoading(false); });
    }, []);

    const handleSelectSlot = (slot: Slot) => {
        setSelected(slot);
        setStep("form");
    };

    const handleBook = async () => {
        if (!name || !email || !selected) return;
        setStep("confirming");
        try {
            const resp = await fetch(`${API_URL}/book`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name, email, start_time: selected.start }),
            });
            const data = await resp.json();
            const booking = data.booking;
            onBooked(
                `${selected.label}${booking.meetingUrl ? ` — Join: ${booking.meetingUrl}` : ""}`
            );
        } catch {
            setError("Booking failed. Please try again.");
            setStep("form");
        }
    };

    return (
        <div className="glass rounded-2xl p-4 border border-violet-500/20">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-white/90">📅 Book an Interview</h3>
                <button
                    onClick={onClose}
                    className="text-white/30 hover:text-white/60 text-lg leading-none"
                >
                    ×
                </button>
            </div>

            {loading && (
                <p className="text-sm text-white/40 text-center py-4">Loading available slots…</p>
            )}

            {error && (
                <p className="text-sm text-red-400 text-center py-2">{error}</p>
            )}

            {/* Step 1: Choose slot */}
            {!loading && step === "slots" && slots.length > 0 && (
                <div className="space-y-2">
                    <p className="text-xs text-white/40 mb-3">Choose a time that works for you:</p>
                    {slots.slice(0, 6).map((slot, i) => (
                        <button
                            key={i}
                            id={`slot-${i}`}
                            onClick={() => handleSelectSlot(slot)}
                            className="w-full text-left px-4 py-2.5 rounded-xl bg-white/5 hover:bg-violet-600/20 border border-white/10 hover:border-violet-500/40 text-sm text-white/80 transition-all"
                        >
                            {slot.label}
                        </button>
                    ))}
                </div>
            )}

            {!loading && step === "slots" && slots.length === 0 && !error && (
                <p className="text-sm text-white/40 text-center py-4">No slots available right now. Please try again later.</p>
            )}

            {/* Step 2: Enter details */}
            {step === "form" && selected && (
                <div className="space-y-3">
                    <p className="text-xs text-white/50">
                        Selected: <span className="text-violet-400">{selected.label}</span>
                    </p>
                    <input
                        id="booking-name"
                        type="text"
                        placeholder="Your Name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-white/30 outline-none focus:border-violet-500/50 transition-colors"
                    />
                    <input
                        id="booking-email"
                        type="email"
                        placeholder="Your Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-white/30 outline-none focus:border-violet-500/50 transition-colors"
                    />
                    <div className="flex gap-2">
                        <button
                            onClick={() => setStep("slots")}
                            className="flex-1 py-2 rounded-xl text-sm text-white/50 border border-white/10 hover:border-white/20 transition-colors"
                        >
                            Back
                        </button>
                        <button
                            id="confirm-booking-btn"
                            onClick={handleBook}
                            disabled={!name || !email}
                            className="flex-1 py-2 rounded-xl text-sm bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed text-white transition-colors"
                        >
                            Confirm Booking
                        </button>
                    </div>
                </div>
            )}

            {/* Step 3: Confirming */}
            {step === "confirming" && (
                <div className="flex items-center justify-center gap-2 py-6">
                    <div className="w-4 h-4 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
                    <span className="text-sm text-white/50">Booking your interview…</span>
                </div>
            )}
        </div>
    );
}
