import type { Metadata } from "next";
import "./globals.css";
import "./auth.css";

export const metadata: Metadata = {
  title: "Compensation Console",
  description: "Salary management workspace for HR teams",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
