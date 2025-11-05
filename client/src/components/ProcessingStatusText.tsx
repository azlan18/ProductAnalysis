import { useEffect, useState, useRef } from 'react';
import { gsap } from 'gsap';
import { SplitText as GSAPSplitText } from 'gsap/SplitText';

interface ProcessingStatusTextProps {
  stage: string;
  currentStep?: string;
  className?: string;
}

export default function ProcessingStatusText({ stage, currentStep, className = '' }: ProcessingStatusTextProps) {
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);
  const [displayText, setDisplayText] = useState('');
  const ref = useRef<HTMLDivElement>(null);
  const splitRef = useRef<any>(null);
  const wrappersRef = useRef<HTMLElement[]>([]);
  const tlRef = useRef<gsap.core.Timeline | null>(null);
  const isAnimatingRef = useRef(false);

  // Get messages based on stage
  const getMessages = () => {
    const baseMessages: Record<string, string[]> = {
      search: [
        'Searching for review URLs...',
        'Finding product reviews...',
        'Querying search engines...',
        'Discovering review sources...'
      ],
      scrape: [
        'Scraping review content...',
        'Parsing URLs...',
        'Extracting data from sources...',
        'Gathering review data...',
        'Downloading content...',
        'Processing web pages...'
      ],
      analyze: [
        'Analyzing with AI...',
        'Processing reviews...',
        'Generating insights...',
        'Extracting sentiment...',
        'Computing analysis...',
        'Creating product summary...'
      ],
      default: [
        'Processing your request...',
        'Analyzing data...',
        'Working on it...',
        'Almost there...'
      ]
    };

    return baseMessages[stage] || baseMessages.default;
  };

  const messages = getMessages();

  // Determine what text to show
  const getTextToShow = () => {
    return currentStep && currentStep.length > 0 
      ? currentStep 
      : messages[currentMessageIndex];
  };

  // Initialize displayText
  useEffect(() => {
    const text = getTextToShow();
    setDisplayText(text);
  }, []);

  // Cycle through messages every 2 seconds when no currentStep
  useEffect(() => {
    if (currentStep && currentStep.length > 0) return;
    
    const interval = setInterval(() => {
      if (!isAnimatingRef.current) {
        setCurrentMessageIndex((prev) => (prev + 1) % messages.length);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [currentStep, messages.length]);

  // Reset when currentStep changes
  useEffect(() => {
    if (currentStep) {
      setCurrentMessageIndex(0);
    }
  }, [currentStep]);

  // Update displayText when index or currentStep changes
  useEffect(() => {
    const newText = getTextToShow();
    if (newText !== displayText) {
      setDisplayText(newText);
    }
  }, [currentStep, currentMessageIndex, messages]);

  // Animate text changes
  useEffect(() => {
    if (!ref.current || !displayText || isAnimatingRef.current) return;

    const el = ref.current;
    const targetText = displayText;
    isAnimatingRef.current = true;
    
    const cleanup = () => {
      if (tlRef.current) {
        tlRef.current.kill();
        tlRef.current = null;
      }
      
      // Remove all wrappers
      wrappersRef.current.forEach(wrap => {
        try {
          const inner = wrap.firstElementChild;
          if (inner) {
            const orig = inner.querySelector('[data-orig="1"]');
            if (orig && wrap.parentNode) {
              wrap.parentNode.replaceChild(orig, wrap);
            }
          }
        } catch {
          wrap.remove();
        }
      });
      wrappersRef.current = [];
      
      try {
        if (splitRef.current) {
          splitRef.current.revert();
        }
      } catch {}
      splitRef.current = null;
    };

    // Ensure element has correct text
    if (el.textContent !== targetText) {
      el.textContent = targetText;
    }

    // Wait for next frame to ensure DOM is ready
    requestAnimationFrame(() => {
      cleanup();

      try {
        splitRef.current = new GSAPSplitText(el, {
          type: 'chars',
          charsClass: 'shuffle-char',
          smartWrap: true,
          reduceWhiteSpace: false
        });

        const chars = splitRef.current?.chars || [];
        if (!chars.length) {
          isAnimatingRef.current = false;
          return;
        }

        chars.forEach(ch => {
          const parent = ch.parentElement;
          if (!parent) return;

          const w = ch.getBoundingClientRect().width;
          if (!w) return;

          const wrap = document.createElement('span');
          wrap.style.cssText = 'display:inline-block;overflow:hidden;width:' + w + 'px;vertical-align:baseline';

          const inner = document.createElement('span');
          inner.style.cssText = 'display:inline-block;white-space:nowrap;will-change:transform';

          parent.insertBefore(wrap, ch);
          wrap.appendChild(inner);

          const firstOrig = ch.cloneNode(true) as HTMLElement;
          firstOrig.style.cssText = 'display:inline-block;width:' + w + 'px;text-align:center';

          ch.setAttribute('data-orig', '1');
          (ch as HTMLElement).style.cssText = 'display:inline-block;width:' + w + 'px;text-align:center';

          inner.appendChild(firstOrig);
          
          // Add shuffle character
          const shuffleChar = ch.cloneNode(true) as HTMLElement;
          const randomChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
          shuffleChar.textContent = randomChars.charAt(Math.floor(Math.random() * randomChars.length));
          shuffleChar.style.cssText = 'display:inline-block;width:' + w + 'px;text-align:center';
          inner.appendChild(shuffleChar);
          inner.appendChild(ch);

          const startX = -2 * w;
          const finalX = 0;

          gsap.set(inner, { x: startX, force3D: true });
          inner.setAttribute('data-final-x', String(finalX));
          inner.setAttribute('data-start-x', String(startX));

          wrappersRef.current.push(wrap);
        });

        const strips = wrappersRef.current.map(w => w.firstElementChild).filter(Boolean) as HTMLElement[];
        
        if (strips.length) {
          const tl = gsap.timeline({
            onComplete: () => {
              // Ensure final text is shown
              wrappersRef.current.forEach(w => {
                const strip = w.firstElementChild;
                if (!strip) return;
                const real = strip.querySelector('[data-orig="1"]');
                if (real) {
                  strip.replaceChildren(real);
                  strip.style.transform = 'none';
                  strip.style.willChange = 'auto';
                }
              });
              
              // Double-check final text
              if (el.textContent !== targetText) {
                el.textContent = targetText;
              }
              
              // Cleanup split text
              setTimeout(() => {
                try {
                  if (splitRef.current) {
                    splitRef.current.revert();
                    splitRef.current = null;
                  }
                } catch {}
              }, 50);
              
              isAnimatingRef.current = false;
            }
          });

          const odd = strips.filter((_, i) => i % 2 === 1);
          const even = strips.filter((_, i) => i % 2 === 0);

          if (odd.length) {
            tl.to(odd, {
              x: (i, t) => parseFloat(t.getAttribute('data-final-x') || '0'),
              duration: 0.2,
              ease: 'power3.out',
              stagger: 0.015,
              force3D: true
            }, 0);
          }

          if (even.length) {
            const oddTotal = 0.2 + Math.max(0, odd.length - 1) * 0.015;
            tl.to(even, {
              x: (i, t) => parseFloat(t.getAttribute('data-final-x') || '0'),
              duration: 0.2,
              ease: 'power3.out',
              stagger: 0.015,
              force3D: true
            }, oddTotal * 0.7);
          }

          tlRef.current = tl;
        } else {
          isAnimatingRef.current = false;
        }
      } catch (e) {
        console.error('Animation error:', e);
        el.textContent = targetText;
        isAnimatingRef.current = false;
      }
    });

    return () => {
      cleanup();
      isAnimatingRef.current = false;
    };
  }, [displayText]);

  return (
    <div className={`flex items-center justify-center min-h-[2rem] ${className}`}>
      <div
        ref={ref}
        className="text-xl font-semibold text-primary"
        style={{
          fontFamily: 'var(--font-sans)',
          lineHeight: '1.5',
          display: 'inline-block'
        }}
      >
        {displayText || getTextToShow()}
      </div>
    </div>
  );
}