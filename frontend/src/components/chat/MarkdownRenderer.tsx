'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownRendererProps {
  content: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  return (
    <div className="prose prose-invert prose-sm max-w-none prose-p:leading-relaxed prose-pre:bg-slate-900 prose-pre:border prose-pre:border-slate-800">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ node, className, children, ...props }) {
            return (
              <code className="bg-slate-800/80 text-blue-300 px-1.5 py-0.5 rounded font-mono text-xs" {...props}>
                {children}
              </code>
            );
          },
          pre({ node, children, ...props }) {
            return (
              <pre className="p-3 my-2 rounded-lg bg-slate-950/90 border border-slate-800 overflow-x-auto text-xs font-mono text-slate-200" {...props}>
                {children}
              </pre>
            );
          },
          ul({ node, children, ...props }) {
            return <ul className="list-disc pl-5 space-y-1 my-2" {...props}>{children}</ul>;
          },
          ol({ node, children, ...props }) {
            return <ol className="list-decimal pl-5 space-y-1 my-2" {...props}>{children}</ol>;
          },
          a({ node, href, children, ...props }) {
            return (
              <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline font-medium" {...props}>
                {children}
              </a>
            );
          }
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};
