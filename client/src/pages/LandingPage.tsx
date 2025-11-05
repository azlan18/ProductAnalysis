import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Search, 
  BarChart3, 
  TrendingUp, 
  ArrowRight, 
  Sparkles,
  Zap,
  Shield
} from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg">
              <BarChart3 className="w-6 h-6 text-primary-foreground" />
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Product Intelligence
            </span>
          </div>
          <div className="flex items-center gap-8">
            <a href="#features" className="text-sm font-medium text-muted-foreground hover:text-foreground transition">
              Features
            </a>
            <a href="#how-it-works" className="text-sm font-medium text-muted-foreground hover:text-foreground transition">
              How it Works
            </a>
            <Link to="/products">
              <Button variant="ghost" className="text-sm font-medium">
                Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 md:py-40">
        <div className="absolute inset-0 bg-gradient-to-b from-accent/5 to-transparent pointer-events-none" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
          <div className="text-center space-y-8">
            <div className="inline-block">
              <span className="text-sm font-semibold text-accent px-4 py-2 rounded-full bg-accent/10 border border-accent/20">
                ✨ AI-Powered Product Analysis
              </span>
            </div>
            <h1 className="text-5xl md:text-7xl font-bold text-foreground leading-tight text-balance">
              Make Informed Decisions with <span className="text-accent">Smart Product Analysis</span>
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto text-balance leading-relaxed">
              Analyze product reviews, compare competitors, and get AI-powered insights to make smarter purchasing decisions.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
              <Link to="/products">
                <Button size="lg" className="bg-primary hover:bg-primary/90 text-primary-foreground gap-2 h-12 px-8">
                  Get Started <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
              <Button size="lg" variant="outline" className="gap-2 h-12 px-8 bg-transparent">
                <Sparkles className="w-4 h-4" /> Learn More
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 md:py-32 bg-muted/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">Powerful Features</h2>
            <p className="text-lg text-muted-foreground">
              Everything you need for comprehensive product analysis
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Search,
                title: 'Smart Review Analysis',
                description: 'Automatically scrape and analyze product reviews from multiple sources using AI-powered sentiment analysis.',
              },
              {
                icon: BarChart3,
                title: 'Detailed Insights',
                description: 'Get comprehensive analysis including pros, cons, feature breakdowns, and user sentiment scores.',
              },
              {
                icon: TrendingUp,
                title: 'Price Comparison',
                description: 'Compare prices across different platforms and sources with direct links to purchase.',
              },
              {
                icon: Zap,
                title: 'Product Comparison',
                description: 'Compare 2-4 products side-by-side with AI-generated recommendations and feature matrices.',
              },
              {
                icon: Shield,
                title: 'Quality Detection',
                description: 'Identify quality issues, defects, and common complaints mentioned in reviews.',
              },
              {
                icon: Sparkles,
                title: 'User Segments',
                description: 'Understand which user types (gamers, photographers, etc.) rate products highest.',
              },
            ].map((feature, idx) => (
              <Card
                key={idx}
                className="border border-border hover:border-accent/50 transition-all duration-300 cursor-pointer group"
              >
                <CardHeader>
                  <div className="flex justify-center mb-4">
                    <div className="p-3 rounded-lg bg-primary/10 text-primary group-hover:bg-accent/20 group-hover:text-accent transition-all">
                      <feature.icon className="w-8 h-8" />
                    </div>
                  </div>
                  <CardTitle className="text-center">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-center">{feature.description}</CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 md:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">How It Works</h2>
            <p className="text-lg text-muted-foreground">Three simple steps to analyze any product</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: '01',
                title: 'Add Product',
                description:
                  'Enter a product name and our system searches the web for reviews from trusted sources.',
              },
              {
                step: '02',
                title: 'AI Analysis',
                description:
                  'Our AI analyzes reviews, extracts sentiment, identifies pros/cons, and compiles comprehensive insights.',
              },
              {
                step: '03',
                title: 'Compare & Decide',
                description:
                  'Compare multiple products side-by-side with AI-generated recommendations based on your needs.',
              },
            ].map((item, idx) => (
              <div key={idx} className="relative">
                <div className="text-6xl font-bold text-accent/20 mb-4">{item.step}</div>
                <h3 className="text-2xl font-semibold text-foreground mb-3">{item.title}</h3>
                <p className="text-muted-foreground">{item.description}</p>
                {idx < 2 && (
                  <div className="hidden md:block absolute top-1/2 -right-4 w-8 h-0.5 bg-gradient-to-r from-accent to-transparent" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 md:py-32 bg-primary text-primary-foreground">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-8">
          <h2 className="text-4xl md:text-5xl font-bold">Ready to Analyze Products?</h2>
          <p className="text-lg opacity-90">Start making smarter purchasing decisions today</p>
          <Link to="/products">
            <Button size="lg" className="bg-primary-foreground hover:bg-primary-foreground/90 text-primary gap-2">
              Start Analyzing <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-muted/30 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-6 h-6 rounded-lg bg-primary flex items-center justify-center">
                  <BarChart3 className="w-4 h-4 text-primary-foreground" />
                </div>
                <span className="font-semibold text-foreground">Product Intelligence</span>
              </div>
              <p className="text-sm text-muted-foreground">AI-powered product analysis and comparison platform</p>
            </div>
            <div>
              <h4 className="font-semibold text-foreground mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>
                  <a href="#features" className="hover:text-foreground transition">
                    Features
                  </a>
                </li>
                <li>
                  <a href="#how-it-works" className="hover:text-foreground transition">
                    How it Works
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-foreground mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>
                  <a href="#" className="hover:text-foreground transition">
                    About
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-foreground transition">
                    Contact
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-foreground mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>
                  <a href="#" className="hover:text-foreground transition">
                    Privacy
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-foreground transition">
                    Terms
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-border pt-8 flex flex-col md:flex-row justify-between items-center text-sm text-muted-foreground">
            <p>&copy; 2025 Product Intelligence. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

