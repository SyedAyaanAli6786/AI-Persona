"use client";

interface QuickPromptChipProps {
    text: string;
}

export default function QuickPromptChip({ text }: QuickPromptChipProps) {
    const handleClick = () => {
        const input = document.getElementById("chat-input") as HTMLTextAreaElement | null;
        if (!input) return;
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
            window.HTMLTextAreaElement.prototype,
            "value"
        )?.set;
        nativeInputValueSetter?.call(input, text);
        input.dispatchEvent(new Event("input", { bubbles: true }));
        input.focus();
    };

    return (
        <button
            className="whitespace-nowrap text-xs px-3 py-1.5 rounded-full glass border border-white/10 hover:border-violet-500/40 hover:text-violet-300 text-white/50 transition-all shrink-0"
            onClick={handleClick}
        >
            {text}
        </button>
    );
}
