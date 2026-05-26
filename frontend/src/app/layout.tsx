import type { Metadata } from "next";
import { IBM_Plex_Sans, Space_Grotesk } from "next/font/google";

import "./globals.css";

import { AppProviders } from "@/providers/app-providers";
import { themeScript } from "@/providers/theme-provider";
import { cn } from "@/lib/utils";

const bodyFont = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-body"
});

const displayFont = Space_Grotesk({
  subsets: ["latin"],
  weight: ["500", "700"],
  variable: "--font-display"
});

export const metadata: Metadata = {
  title: "StockML Predictor",
  description:
    "A polished local stock prediction workspace powered by FastAPI and Next.js."
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body className={cn(bodyFont.variable, displayFont.variable, "font-body")}>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
