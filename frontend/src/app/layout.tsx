import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Zero-Knowledge Alpha Predator",
  description: "Autonomous DeFi Agent • x402 Payments • Encrypted Execution",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <div className="bg-grid" />
        <div className="bg-glow" />
        {children}
      </body>
    </html>
  );
}
