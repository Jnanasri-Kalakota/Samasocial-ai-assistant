import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'SamaSocial — Multi-Source AI Learning Assistant',
  description: 'Evidence-first multi-source AI chatbot supporting PDF, PPTX, DOCX, YouTube, and Web with fine-grained citations and session memory.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
        {children}
      </body>
    </html>
  );
}
