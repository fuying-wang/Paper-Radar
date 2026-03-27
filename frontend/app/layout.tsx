import type { Metadata } from "next";
import "./globals.css";
import TopNav from "./_components/top-nav";

export const metadata: Metadata = {
  title: "Research Radar",
  description: "Discover research papers by field or keywords",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900">
        <TopNav />
        {children}
      </body>
    </html>
  );
}
