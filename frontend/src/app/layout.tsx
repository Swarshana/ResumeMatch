import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ResumeMatch",
  description: "Semantic resume-to-job matching engine",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-neutral-50 antialiased">
        {children}
      </body>
    </html>
  );
}