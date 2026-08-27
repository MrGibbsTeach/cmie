import type { Metadata } from "next";
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
  title: "FocusLab Digital",
  description: "Free Digital Technologies teaching resources and lesson plans.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-slate-50 text-slate-900">
        <header className="border-b border-slate-200 bg-white">
          <div className="max-w-3xl mx-auto px-6 py-4 flex items-center justify-between">
            <a href="/" className="font-semibold text-slate-900">
              FocusLab Digital
            </a>
            <a href="/blog" className="text-sm text-slate-600 hover:text-slate-900">
              Blog
            </a>
          </div>
        </header>
        <main className="flex-1">{children}</main>
        <footer className="border-t border-slate-200 py-8 text-center text-sm text-slate-500">
          FocusLab Digital — Digital Technologies teaching resources
        </footer>
      </body>
    </html>
  );
}
