import type { Metadata } from "next";
import "./globals.css";

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
      <body>{children}</body>
    </html>
  );
}
