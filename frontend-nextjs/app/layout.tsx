import type { Metadata } from "next";
import "./globals.css";
import Header from "@/components/Header";

export const metadata: Metadata = {
  title: "Penn State Degree Optimizer",
  description: "Find your fastest path to a Minor or Certificate at Penn State. Analyze your completed courses and discover personalized degree recommendations.",
  keywords: ["Penn State", "degree optimizer", "minor", "certificate", "course planner", "academic planning"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <div className="min-h-screen flex flex-col">
          <Header />
          
          <main className="flex-1">
            {children}
          </main>

          <footer className="bg-penn-navy text-white py-8 mt-20">
            <div className="container mx-auto px-4 text-center">
              <p className="text-penn-light">
                Penn State Degree Optimizer • Built with Next.js + Tailwind CSS
              </p>
              <p className="text-sm text-penn-slate mt-2">
                Helping students find their optimal path to graduation
              </p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
