import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownContentProps {
  content: string;
  className?: string;
}

export default function MarkdownContent({ content, className = '' }: MarkdownContentProps) {
  return (
    <div className={`markdown-content ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
        // Paragraphs
        p: ({ children }) => <p className="mb-3 last:mb-0">{children}</p>,
        
        // Headings
        h1: ({ children }) => <h1 className="text-2xl font-bold mb-4 mt-6 first:mt-0">{children}</h1>,
        h2: ({ children }) => <h2 className="text-xl font-bold mb-3 mt-5 first:mt-0">{children}</h2>,
        h3: ({ children }) => <h3 className="text-lg font-semibold mb-2 mt-4 first:mt-0">{children}</h3>,
        h4: ({ children }) => <h4 className="text-base font-semibold mb-2 mt-3 first:mt-0">{children}</h4>,
        
        // Lists
        ul: ({ children }) => <ul className="list-disc list-inside mb-3 space-y-1">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal list-inside mb-3 space-y-1">{children}</ol>,
        li: ({ children }) => <li className="ml-2">{children}</li>,
        
        // Code
        code: ({ inline, children }: any) => 
          inline ? (
            <code className="bg-muted px-1.5 py-0.5 rounded text-sm font-mono">{children}</code>
          ) : (
            <code className="block bg-muted p-3 rounded text-sm font-mono overflow-x-auto mb-3">{children}</code>
          ),
        pre: ({ children }) => <pre className="mb-3">{children}</pre>,
        
        // Blockquote
        blockquote: ({ children }) => (
          <blockquote className="border-l-4 border-primary pl-4 italic my-3 text-muted-foreground">
            {children}
          </blockquote>
        ),
        
        // Links
        a: ({ href, children }) => (
          <a 
            href={href} 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-primary hover:underline"
          >
            {children}
          </a>
        ),
        
        // Horizontal rule
        hr: () => <hr className="my-4 border-border" />,
        
        // Strong/Bold
        strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
        
        // Emphasis/Italic
        em: ({ children }) => <em className="italic">{children}</em>,
      }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

