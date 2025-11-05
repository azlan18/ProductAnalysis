import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { 
  ArrowLeft, 
  BarChart3, 
  Loader2, 
  TrendingUp, 
  TrendingDown,
  CheckCircle2,
  XCircle,
  Sparkles,
  ExternalLink,
  AlertCircle,
  Users,
  ShieldAlert,
  TrendingUp as TrendingUpIcon,
  DollarSign,
  Target
} from 'lucide-react';
import { 
  getProduct, 
  analyzeProduct, 
  getProductStatus, 
  type ProductDetail,
  type AnalysisStatus 
} from '@/lib/api';
import ProcessingStatusText from '@/components/ProcessingStatusText';
import MarkdownContent from '@/components/MarkdownContent';

export default function ProductDetailPage() {
  const { productId } = useParams<{ productId: string }>();
  const navigate = useNavigate();
  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [status, setStatus] = useState<AnalysisStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [polling, setPolling] = useState(false);

  useEffect(() => {
    if (productId) {
      loadProduct();
    }
  }, [productId]);

  useEffect(() => {
    if (productId && (product?.status === 'processing' || polling)) {
      const interval = setInterval(() => {
        checkStatus();
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [productId, product?.status, polling]);

  const loadProduct = async () => {
    if (!productId) return;
    try {
      setLoading(true);
      setError(null);
      const data = await getProduct(productId);
      setProduct(data);
      if (data.status === 'processing') {
        checkStatus();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load product');
    } finally {
      setLoading(false);
    }
  };

  const checkStatus = async () => {
    if (!productId) return;
    try {
      const statusData = await getProductStatus(productId);
      setStatus(statusData);
      if (statusData.status === 'completed') {
        setPolling(false);
        await loadProduct();
      } else if (statusData.status === 'failed') {
        setPolling(false);
      }
    } catch (err) {
      console.error('Failed to check status:', err);
    }
  };

  const handleAnalyze = async () => {
    if (!productId) return;
    try {
      setAnalyzing(true);
      setPolling(true);
      await analyzeProduct(productId);
      await loadProduct();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start analysis');
      setAnalyzing(false);
      setPolling(false);
    }
  };

  const getSentimentColor = (score: number) => {
    if (score >= 7) return 'text-green-500';
    if (score >= 4) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getSentimentBg = (score: number) => {
    if (score >= 7) return 'bg-green-500/10 border-green-500/20';
    if (score >= 4) return 'bg-yellow-500/10 border-yellow-500/20';
    return 'bg-red-500/10 border-red-500/20';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="w-12 h-12 text-primary animate-spin" />
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle>Error</CardTitle>
            <CardDescription>{error || 'Product not found'}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => navigate('/products')} variant="outline">
              <ArrowLeft className="w-4 h-4 mr-2" /> Back to Products
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const analysis = product.analysis;
  const isProcessing = product.status === 'processing' || polling;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <Link to="/products" className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg">
              <BarChart3 className="w-6 h-6 text-primary-foreground" />
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Product Intelligence
            </span>
          </Link>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <Button
          variant="ghost"
          onClick={() => navigate('/products')}
          className="mb-6"
        >
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to Products
        </Button>

        {/* Product Header */}
        <div className="mb-8">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-4xl font-bold text-foreground mb-2">{product.product_name}</h1>
              <p className="text-muted-foreground">
                Added {new Date(product.created_at).toLocaleDateString()}
              </p>
            </div>
            <Badge className={product.status === 'completed' ? 'bg-green-500/10 text-green-500' : 
                              product.status === 'processing' ? 'bg-blue-500/10 text-blue-500' :
                              'bg-gray-500/10 text-gray-500'}>
              {product.status}
            </Badge>
          </div>

          {/* Processing Status */}
          {isProcessing && status && (
            <Card className="mb-6 border-primary/20">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Loader2 className="w-5 h-5 animate-spin text-primary" />
                  Analysis in Progress
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <ProcessingStatusText 
                  stage={status.stage || 'default'} 
                  currentStep={status.current_step}
                  className="min-h-[2rem]"
                />
                <Progress value={status.progress} className="mb-2" />
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">
                    Stage: <span className="font-medium text-foreground">{status.stage}</span>
                  </span>
                  <span className="text-muted-foreground">
                    <span className="font-medium text-foreground">{status.progress}%</span> complete
                  </span>
                </div>
              </CardContent>
            </Card>
          )}

        </div>

        {/* No Analysis State */}
        {!analysis && product.status === 'pending' && (
          <Card className="border-dashed">
            <CardContent className="pt-12 pb-12 text-center">
              <Sparkles className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
              <CardTitle className="mb-2">No Analysis Yet</CardTitle>
              <CardDescription className="mb-6">
                Start analyzing this product to get comprehensive insights from reviews
              </CardDescription>
              <Button
                onClick={handleAnalyze}
                disabled={analyzing}
                size="lg"
                className="bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-primary-foreground gap-2"
              >
                {analyzing ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" /> Starting Analysis...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" /> Start Analysis
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Failed Analysis State */}
        {!analysis && product.status === 'failed' && (
          <Card className="border-destructive/50">
            <CardContent className="pt-12 pb-12 text-center">
              <AlertCircle className="w-16 h-16 text-destructive mx-auto mb-4" />
              <CardTitle className="mb-2">Analysis Failed</CardTitle>
              <CardDescription className="mb-6">
                The previous analysis attempt failed. You can try again.
              </CardDescription>
              <Button
                onClick={handleAnalyze}
                disabled={analyzing}
                size="lg"
                className="bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-primary-foreground gap-2"
              >
                {analyzing ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" /> Starting Analysis...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" /> Try Again
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Analysis Results */}
        {analysis && product.status === 'completed' && (
          <Tabs defaultValue="overview" className="space-y-6">
            <TabsList>
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="sentiment">Sentiment</TabsTrigger>
              <TabsTrigger value="features">Features</TabsTrigger>
              <TabsTrigger value="insights">Insights</TabsTrigger>
              <TabsTrigger value="prices">Prices</TabsTrigger>
            </TabsList>

            {/* Overview Tab */}
            <TabsContent value="overview" className="space-y-6">
              {/* Overall Sentiment */}
              <Card>
                <CardHeader>
                  <CardTitle>Overall Sentiment</CardTitle>
                  <CardDescription>Average sentiment score from reviews</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-6">
                    <div className="text-center">
                      <div className={`text-5xl font-bold ${getSentimentColor(analysis.sentiment.score)}`}>
                        {analysis.sentiment.score.toFixed(1)}
                      </div>
                      <div className="text-sm text-muted-foreground mt-1">out of 10</div>
                    </div>
                    <Separator orientation="vertical" className="h-16" />
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge className={getSentimentBg(analysis.sentiment.score)}>
                          {analysis.sentiment.sentiment}
                        </Badge>
                      </div>
                      <p className="text-muted-foreground">{analysis.general_sentiment}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Pros and Cons */}
              <div className="grid md:grid-cols-2 gap-6">
                <Card className="border-green-500/20">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <CheckCircle2 className="w-5 h-5 text-green-500" /> Pros
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <MarkdownContent content={analysis.pros.join('\n\n')} />
                  </CardContent>
                </Card>

                <Card className="border-red-500/20">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <XCircle className="w-5 h-5 text-red-500" /> Cons
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <MarkdownContent content={analysis.cons.join('\n\n')} />
                  </CardContent>
                </Card>
              </div>

              {/* Top Praises & Complaints */}
              <div className="grid md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="w-5 h-5 text-green-500" /> Top Praises
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {analysis.top_praises.slice(0, 5).map((praise, idx) => (
                        <div key={idx} className="border-b border-border pb-4 last:border-0 last:pb-0">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium">{praise.aspect}</span>
                            <Badge variant="outline">{praise.frequency} mentions</Badge>
                          </div>
                          <Progress value={praise.percentage} className="h-2 mb-3" />
                          {praise.quotes && praise.quotes.length > 0 && (
                            <div className="space-y-2 mt-3">
                              {praise.quotes.slice(0, 3).map((quote, qIdx) => (
                                <div key={qIdx} className="bg-green-500/5 border border-green-500/20 rounded-lg p-3 text-sm">
                                  <p className="text-foreground italic">"{quote.quote}"</p>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingDown className="w-5 h-5 text-red-500" /> Top Complaints
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {analysis.top_complaints.slice(0, 5).map((complaint, idx) => (
                        <div key={idx} className="border-b border-border pb-4 last:border-0 last:pb-0">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium">{complaint.aspect}</span>
                            <Badge variant="outline">{complaint.frequency} mentions</Badge>
                          </div>
                          <Progress value={complaint.percentage} className="h-2 mb-3" />
                          {complaint.quotes && complaint.quotes.length > 0 && (
                            <div className="space-y-2 mt-3">
                              {complaint.quotes.slice(0, 3).map((quote, qIdx) => (
                                <div key={qIdx} className="bg-red-500/5 border border-red-500/20 rounded-lg p-3 text-sm">
                                  <p className="text-foreground italic">"{quote.quote}"</p>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Enhanced Summary */}
              {analysis.summary && (
                <Card>
                  <CardHeader>
                    <CardTitle>AI Summary</CardTitle>
                    {analysis.summary.one_liner && (
                      <CardDescription className="text-base font-medium text-foreground mt-2">
                        {analysis.summary.one_liner}
                      </CardDescription>
                    )}
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {analysis.summary.best_for && analysis.summary.best_for.length > 0 && (
                      <div>
                        <h4 className="font-semibold mb-2 flex items-center gap-2">
                          <Target className="w-4 h-4 text-green-500" /> Best For
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {analysis.summary.best_for.map((item, idx) => (
                            <Badge key={idx} className="bg-green-500/10 text-green-500 border-green-500/20">
                              {item}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                    {analysis.summary.not_recommended_for && analysis.summary.not_recommended_for.length > 0 && (
                      <div>
                        <h4 className="font-semibold mb-2 flex items-center gap-2">
                          <XCircle className="w-4 h-4 text-red-500" /> Not Recommended For
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {analysis.summary.not_recommended_for.map((item, idx) => (
                            <Badge key={idx} className="bg-red-500/10 text-red-500 border-red-500/20">
                              {item}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                    {analysis.summary.verdict && (
                      <div className="pt-2 border-t border-border">
                        <h4 className="font-semibold mb-2">Verdict</h4>
                        <p className="text-muted-foreground">{analysis.summary.verdict}</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* Value Analysis */}
              {analysis.value_analysis && (
                <Card className="border-primary/20">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <DollarSign className="w-5 h-5 text-primary" /> Value Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center gap-6">
                        <div className="text-center">
                          <div className="text-4xl font-bold text-primary">
                            {analysis.value_analysis.score.toFixed(1)}
                          </div>
                          <div className="text-sm text-muted-foreground mt-1">out of 10</div>
                        </div>
                        <Separator orientation="vertical" className="h-16" />
                        <div className="flex-1">
                          <div className="mb-2">
                            <span className="font-medium">{analysis.value_analysis.percentage_saying_worth_it}%</span>
                            <span className="text-muted-foreground ml-1">say it's worth it</span>
                          </div>
                          <Progress value={analysis.value_analysis.percentage_saying_worth_it} className="h-2" />
                        </div>
                      </div>
                      <p className="text-muted-foreground mt-4">{analysis.value_analysis.reasoning}</p>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* User Segments */}
              {analysis.user_segments && analysis.user_segments.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Users className="w-5 h-5 text-primary" /> User Segments
                    </CardTitle>
                    <CardDescription>Customer satisfaction by user type</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid md:grid-cols-2 gap-4">
                      {analysis.user_segments.map((segment, idx) => (
                        <div key={idx} className="border border-border rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium">{segment.segment}</span>
                            <Badge variant="outline">{segment.count} reviews</Badge>
                          </div>
                          <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                              <span>Satisfaction</span>
                              <span className="font-medium">{segment.satisfaction}%</span>
                            </div>
                            <Progress value={segment.satisfaction} className="h-2" />
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Quality Issues */}
              {analysis.quality_issues && analysis.quality_issues.length > 0 && (
                <Card className="border-yellow-500/20">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <ShieldAlert className="w-5 h-5 text-yellow-500" /> Quality Issues
                    </CardTitle>
                    <CardDescription>Reported issues and defects</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {analysis.quality_issues.map((issue, idx) => (
                        <div key={idx} className="border-b border-border pb-4 last:border-0 last:pb-0">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium">{issue.issue}</span>
                            <div className="flex items-center gap-2">
                              <Badge variant="outline">{issue.frequency} reports</Badge>
                              <Badge className={
                                issue.severity === 'high' ? 'bg-red-500/10 text-red-500' :
                                issue.severity === 'medium' ? 'bg-yellow-500/10 text-yellow-500' :
                                'bg-gray-500/10 text-gray-500'
                              }>
                                {issue.severity}
                              </Badge>
                            </div>
                          </div>
                          {issue.quotes && issue.quotes.length > 0 && (
                            <div className="space-y-2 mt-3">
                              {issue.quotes.map((quote, qIdx) => (
                                <div key={qIdx} className="bg-yellow-500/5 border border-yellow-500/20 rounded-lg p-3 text-sm">
                                  <p className="text-foreground italic">"{quote.quote}"</p>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Competitor Mentions */}
              {analysis.competitor_mentions && Object.keys(analysis.competitor_mentions).length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUpIcon className="w-5 h-5 text-primary" /> Competitor Mentions
                    </CardTitle>
                    <CardDescription>How this product compares to competitors mentioned in reviews</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {Object.entries(analysis.competitor_mentions).map(([competitor, data]) => (
                        <div key={competitor} className="border border-border rounded-lg p-4">
                          <div className="flex items-center justify-between mb-3">
                            <span className="font-medium">{competitor}</span>
                            <div className="flex items-center gap-2">
                              <Badge variant="outline">{data.frequency} mentions</Badge>
                              <Badge className={
                                data.sentiment === 'better' ? 'bg-green-500/10 text-green-500' :
                                data.sentiment === 'worse' ? 'bg-red-500/10 text-red-500' :
                                'bg-gray-500/10 text-gray-500'
                              }>
                                {data.sentiment}
                              </Badge>
                            </div>
                          </div>
                          {data.quotes && data.quotes.length > 0 && (
                            <div className="space-y-2 mt-3">
                              {data.quotes.map((quote, qIdx) => (
                                <div key={qIdx} className="bg-muted/50 border border-border rounded-lg p-3 text-sm">
                                  <p className="text-foreground italic">"{quote.quote}"</p>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Description */}
              {analysis.description && (
                <Card>
                  <CardHeader>
                    <CardTitle>Product Description</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <MarkdownContent content={analysis.description} />
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            {/* Sentiment Tab */}
            <TabsContent value="sentiment" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Sentiment Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  {analysis.sentiment.distribution && (
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between mb-2">
                          <span>Positive</span>
                          <span className="font-medium">{analysis.sentiment.distribution.positive}%</span>
                        </div>
                        <Progress value={analysis.sentiment.distribution.positive} className="h-3 bg-green-500/20" />
                      </div>
                      <div>
                        <div className="flex justify-between mb-2">
                          <span>Neutral</span>
                          <span className="font-medium">{analysis.sentiment.distribution.neutral}%</span>
                        </div>
                        <Progress value={analysis.sentiment.distribution.neutral} className="h-3 bg-gray-500/20" />
                      </div>
                      <div>
                        <div className="flex justify-between mb-2">
                          <span>Negative</span>
                          <span className="font-medium">{analysis.sentiment.distribution.negative}%</span>
                        </div>
                        <Progress value={analysis.sentiment.distribution.negative} className="h-3 bg-red-500/20" />
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Features Tab */}
            <TabsContent value="features" className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                {Object.entries(analysis.features).map(([feature, data]) => (
                  <Card key={feature}>
                    <CardHeader>
                      <CardTitle className="capitalize">{feature}</CardTitle>
                      <CardDescription>
                        Score: {data.score.toFixed(1)}/10 • {data.mentions} mentions
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <Badge className={getSentimentBg(data.score)}>
                          {data.sentiment}
                        </Badge>
                        <Progress value={data.score * 10} className="h-2" />
                        {data.quotes && data.quotes.length > 0 && (
                          <div className="space-y-2 mt-3">
                            {data.quotes.slice(0, 2).map((quote, qIdx) => (
                              <div key={qIdx} className="bg-muted/50 rounded-lg p-2 text-xs">
                                <p className="text-foreground italic">"{quote.quote}"</p>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            {/* Insights Tab */}
            <TabsContent value="insights" className="space-y-6">
              {/* User Segments */}
              {analysis.user_segments && analysis.user_segments.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Users className="w-5 h-5 text-primary" /> User Segments
                    </CardTitle>
                    <CardDescription>Customer satisfaction by user type</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {analysis.user_segments.map((segment, idx) => (
                        <div key={idx} className="border border-border rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium">{segment.segment}</span>
                            <Badge variant="outline">{segment.count} reviews</Badge>
                          </div>
                          <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                              <span>Satisfaction</span>
                              <span className="font-medium">{segment.satisfaction}%</span>
                            </div>
                            <Progress value={segment.satisfaction} className="h-2" />
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Quality Issues */}
              {analysis.quality_issues && analysis.quality_issues.length > 0 && (
                <Card className="border-yellow-500/20">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <ShieldAlert className="w-5 h-5 text-yellow-500" /> Quality Issues
                    </CardTitle>
                    <CardDescription>Reported issues and defects</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {analysis.quality_issues.map((issue, idx) => (
                        <div key={idx} className="border-b border-border pb-4 last:border-0 last:pb-0">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium">{issue.issue}</span>
                            <div className="flex items-center gap-2">
                              <Badge variant="outline">{issue.frequency} reports</Badge>
                              <Badge className={
                                issue.severity === 'high' ? 'bg-red-500/10 text-red-500' :
                                issue.severity === 'medium' ? 'bg-yellow-500/10 text-yellow-500' :
                                'bg-gray-500/10 text-gray-500'
                              }>
                                {issue.severity}
                              </Badge>
                            </div>
                          </div>
                          {issue.quotes && issue.quotes.length > 0 && (
                            <div className="space-y-2 mt-3">
                              {issue.quotes.map((quote, qIdx) => (
                                <div key={qIdx} className="bg-yellow-500/5 border border-yellow-500/20 rounded-lg p-3 text-sm">
                                  <p className="text-foreground italic">"{quote.quote}"</p>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Competitor Mentions */}
              {analysis.competitor_mentions && Object.keys(analysis.competitor_mentions).length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUpIcon className="w-5 h-5 text-primary" /> Competitor Mentions
                    </CardTitle>
                    <CardDescription>How this product compares to competitors mentioned in reviews</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {Object.entries(analysis.competitor_mentions).map(([competitor, data]) => (
                        <div key={competitor} className="border border-border rounded-lg p-4">
                          <div className="flex items-center justify-between mb-3">
                            <span className="font-medium">{competitor}</span>
                            <div className="flex items-center gap-2">
                              <Badge variant="outline">{data.frequency} mentions</Badge>
                              <Badge className={
                                data.sentiment === 'better' ? 'bg-green-500/10 text-green-500' :
                                data.sentiment === 'worse' ? 'bg-red-500/10 text-red-500' :
                                'bg-gray-500/10 text-gray-500'
                              }>
                                {data.sentiment}
                              </Badge>
                            </div>
                          </div>
                          {data.quotes && data.quotes.length > 0 && (
                            <div className="space-y-2 mt-3">
                              {data.quotes.map((quote, qIdx) => (
                                <div key={qIdx} className="bg-muted/50 border border-border rounded-lg p-3 text-sm">
                                  <p className="text-foreground italic">"{quote.quote}"</p>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Value Analysis */}
              {analysis.value_analysis && (
                <Card className="border-primary/20">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <DollarSign className="w-5 h-5 text-primary" /> Value Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center gap-6">
                        <div className="text-center">
                          <div className="text-4xl font-bold text-primary">
                            {analysis.value_analysis.score.toFixed(1)}
                          </div>
                          <div className="text-sm text-muted-foreground mt-1">out of 10</div>
                        </div>
                        <Separator orientation="vertical" className="h-16" />
                        <div className="flex-1">
                          <div className="mb-2">
                            <span className="font-medium">{analysis.value_analysis.percentage_saying_worth_it}%</span>
                            <span className="text-muted-foreground ml-1">say it's worth it</span>
                          </div>
                          <Progress value={analysis.value_analysis.percentage_saying_worth_it} className="h-2" />
                        </div>
                      </div>
                      <p className="text-muted-foreground mt-4">{analysis.value_analysis.reasoning}</p>
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            {/* Prices Tab */}
            <TabsContent value="prices" className="space-y-6">
              {analysis.prices && analysis.prices.length > 0 ? (
                <div className="grid md:grid-cols-2 gap-6">
                  {analysis.prices.map((price, idx) => (
                    <Card key={idx}>
                      <CardHeader>
                        <CardTitle>{price.platform}</CardTitle>
                        <CardDescription className="text-2xl font-bold text-primary">
                          {price.price}
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <a
                          href={price.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-accent hover:underline flex items-center gap-2"
                        >
                          View on {price.platform} <ExternalLink className="w-4 h-4" />
                        </a>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <Card>
                  <CardContent className="py-12 text-center">
                    <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">No price information available</p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>
          </Tabs>
        )}
      </main>
    </div>
  );
}

