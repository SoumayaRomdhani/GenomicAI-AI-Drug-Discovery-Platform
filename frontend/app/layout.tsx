import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "GenomicAI — Drug Discovery Platform",
  description: "Portfolio-grade AI platform for drug discovery and genomic analysis"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
