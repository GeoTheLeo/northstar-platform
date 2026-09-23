import type { Metadata } from "next";
import Link from "next/link";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "NorthStar Intervention Copilot",
  description:
    "An agentic copilot that investigates at-risk students and proposes interventions for human approval.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-neutral-50 text-neutral-900">
        <nav className="border-b border-neutral-200 bg-white">
          <div className="mx-auto flex max-w-4xl items-center gap-6 px-8 py-3 text-sm font-medium">
            <span className="text-neutral-400">NorthStar</span>
            <Link href="/" className="hover:text-neutral-600">
              Dashboard
            </Link>
            <Link href="/copilot" className="hover:text-neutral-600">
              Copilot
            </Link>
            <Link href="/queue" className="hover:text-neutral-600">
              Approval queue
            </Link>
          </div>
        </nav>
        <div className="flex flex-1 flex-col">{children}</div>
      </body>
    </html>
  );
}
