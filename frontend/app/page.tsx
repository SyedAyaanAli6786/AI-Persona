"use client";

import ChatWindow from "@/components/ChatWindow";
import VapiButton from "@/components/VapiButton";

export default function Home() {
  return (
    <div style={{
      display: "flex",
      height: "100dvh",
      background: "var(--bg)",
      padding: "20px",
      gap: "0",
      alignItems: "stretch",
    }}>
      {/* Left sidebar — persona card */}
      <aside style={{
        width: 280,
        flexShrink: 0,
        background: "var(--surface)",
        borderRadius: "var(--radius-lg)",
        padding: "32px 24px",
        display: "flex",
        flexDirection: "column",
        gap: 0,
        boxShadow: "var(--shadow-md)",
        marginRight: 16,
        overflowY: "auto",
      }}>
        {/* Avatar */}
        <div style={{ textAlign: "center", marginBottom: 20 }}>
          <div style={{
            width: 80, height: 80,
            borderRadius: "50%",
            background: "linear-gradient(135deg, #5c6ef8 0%, #8b5cf6 100%)",
            display: "flex", alignItems: "center", justifyContent: "center",
            margin: "0 auto 12px",
            fontSize: 32, color: "white", fontWeight: 700,
            boxShadow: "0 4px 20px rgba(92,110,248,0.35)",
          }}>A</div>
          <h1 style={{ fontSize: 18, fontWeight: 700, color: "var(--text-primary)", marginBottom: 4 }}>
            Syed Ayaan Ali
          </h1>
          <p style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.5, marginBottom: 12 }}>
            CS Student · Developer
          </p>
          <div className="badge" style={{ margin: "0 auto", width: "fit-content" }}>
            <span className="badge-dot" />
            Open to opportunities
          </div>
        </div>

        <hr style={{ border: "none", borderTop: "1px solid var(--border)", marginBottom: 20 }} />

        {/* Education */}
        <Section title="Education">
          <InfoItem icon="🎓" text="Scaler School of Technology" sub="B.S. + M.S. CS · 2023–present" />
          <InfoItem icon="🎓" text="BITS Pilani" sub="B.S. CS · 2023–present" />
        </Section>

        {/* Voice Agent */}
        <Section title="Voice Assistant">
          <div style={{
            background: "linear-gradient(135deg, #f0f4ff 0%, #f5f3ff 100%)",
            borderRadius: "var(--radius-md)",
            padding: "12px",
            border: "1px solid rgba(92,110,248,0.15)",
            marginTop: 4
          }}>
            <p style={{ fontSize: 12, fontWeight: 600, color: "var(--accent)", marginBottom: 4 }}>
              📞 Call Ayaan&apos;s AI Assistant
            </p>
            <p style={{ fontSize: 11, color: "var(--text-secondary)", marginBottom: 10, lineHeight: 1.4 }}>
              Interview the AI version of Ayaan directly from your browser.
            </p>

            <VapiButton />

            <div style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              marginTop: 12,
              paddingTop: 10,
              borderTop: "1px dashed rgba(92,110,248,0.2)"
            }}>
              <p style={{ fontSize: 10, color: "var(--text-muted)", flex: 1 }}>Or call via phone:</p>
              <a href="tel:+19842061807" style={{
                fontSize: 11,
                fontWeight: 600,
                color: "var(--accent)",
                textDecoration: "none"
              }}>
                +1 984 206 1807
              </a>
            </div>
          </div>
        </Section>

        {/* Skills */}
        <Section title="Tech Stack">
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 4 }}>
            {["Python", "JavaScript", "TypeScript", "Node.js", "React", "Next.js", "FastAPI", "PostgreSQL", "ML/NLP", "Docker", "Git"].map(skill => (
              <span key={skill} style={{
                fontSize: 11, fontWeight: 500,
                background: "var(--accent-light)", color: "var(--accent)",
                borderRadius: 999, padding: "3px 10px",
                border: "1px solid rgba(92,110,248,0.2)",
              }}>{skill}</span>
            ))}
          </div>
        </Section>

        {/* Links */}
        <Section title="Links">
          <a href="https://github.com/SyedAyaanAli6786" target="_blank" rel="noreferrer"
            style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--text-secondary)", textDecoration: "none", fontSize: 13, padding: "4px 0" }}
            onMouseEnter={e => (e.currentTarget.style.color = "var(--accent)")}
            onMouseLeave={e => (e.currentTarget.style.color = "var(--text-secondary)")}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" /></svg>
            SyedAyaanAli6786
          </a>
          <a href="mailto:aliaayan6786@gmail.com"
            style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--text-secondary)", textDecoration: "none", fontSize: 13, padding: "4px 0" }}
            onMouseEnter={e => (e.currentTarget.style.color = "var(--accent)")}
            onMouseLeave={e => (e.currentTarget.style.color = "var(--text-secondary)")}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="4" width="20" height="16" rx="2" /><path d="m22 7-10 7L2 7" /></svg>
            aliaayan6786@gmail.com
          </a>
        </Section>

        <div style={{ flex: 1 }} />

        <p style={{ fontSize: 11, color: "var(--text-muted)", textAlign: "center", marginTop: 16, lineHeight: 1.6 }}>
          This AI is grounded on Ayaan&apos;s real resume &amp; GitHub.
        </p>
      </aside>

      {/* Chat panel */}
      <main style={{
        flex: 1,
        background: "var(--surface)",
        borderRadius: "var(--radius-lg)",
        boxShadow: "var(--shadow-md)",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
        minWidth: 0,
      }}>
        {/* Chat header */}
        <div style={{
          padding: "20px 24px",
          borderBottom: "1px solid var(--border)",
          display: "flex",
          alignItems: "center",
          gap: 12,
          flexShrink: 0,
        }}>
          <div style={{
            width: 38, height: 38, borderRadius: "50%",
            background: "linear-gradient(135deg, #5c6ef8, #8b5cf6)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 16, color: "white", fontWeight: 700,
            boxShadow: "0 2px 8px rgba(92,110,248,0.3)",
          }}>A</div>
          <div>
            <p style={{ fontSize: 15, fontWeight: 600, color: "var(--text-primary)" }}>Ayaan&apos;s AI Assistant</p>
            <p style={{ fontSize: 12, color: "var(--text-muted)" }}>Ask about skills, projects, or book an interview</p>
          </div>
          <div style={{ marginLeft: "auto" }}>
            <div className="badge">
              <span className="badge-dot" />
              Online
            </div>
          </div>
        </div>

        <ChatWindow />
      </main>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: 20 }}>
      <p style={{ fontSize: 11, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--text-muted)", marginBottom: 10 }}>{title}</p>
      <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>{children}</div>
    </div>
  );
}

function InfoItem({ icon, text, sub }: { icon: string; text: string; sub?: string }) {
  return (
    <div style={{ display: "flex", gap: 8, alignItems: "flex-start", padding: "3px 0" }}>
      <span style={{ fontSize: 13, flexShrink: 0, marginTop: 1 }}>{icon}</span>
      <div>
        <p style={{ fontSize: 13, color: "var(--text-primary)", fontWeight: 500, lineHeight: 1.4 }}>{text}</p>
        {sub && <p style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 1 }}>{sub}</p>}
      </div>
    </div>
  );
}
