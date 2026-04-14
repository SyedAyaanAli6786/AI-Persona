import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ayaan Ali — AI Persona",
  description: "Chat with Syed Ayaan Ali's AI persona. Ask about his skills, projects, and book an interview.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body style={{ height: "100dvh", display: "flex", flexDirection: "column" }}>
        {children}
      </body>
    </html>
  );
}
