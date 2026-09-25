import type { Metadata } from "next";
import { AppShell } from "@/components/ui";
import "./globals.css";

export const metadata: Metadata = {
  title: "UPIShield — Proactive Cybercrime Intelligence",
  description: "Financial cybercrime intelligence, network investigation and predictive cash-out surveillance.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body><AppShell>{children}</AppShell></body></html>;
}
