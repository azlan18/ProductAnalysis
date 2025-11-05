import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { 
  BarChart3, 
  Loader2, 
  Sparkles,
  Trophy,
  CheckCircle2,
  XCircle,
  ArrowRight
} from 'lucide-react';
import { getProducts, compareProducts, type Product, type Comparison } from '@/lib/api';

export default function ComparePage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedProducts, setSelectedProducts] = useState<string[]>([]);
  const [comparison, setComparison] = useState<Comparison | null>(null);
  const [loading, setLoading] = useState(true);
  const [comparing, setComparing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getProducts();
      // Only show completed products for comparison
      const completedProducts = data.filter(p => p.status === 'completed');
      setProducts(completedProducts);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleProduct = (productId: string) => {
    if (selectedProducts.includes(productId)) {
      setSelectedProducts(selectedProducts.filter(id => id !== productId));
    } else {
      if (selectedProducts.length < 4) {
        setSelectedProducts([...selectedProducts, productId]);
      }
    }
  };

  const handleCompare = async () => {
    if (selectedProducts.length < 2) return;

    try {
      setComparing(true);
      setError(null);
      const result = await compareProducts(selectedProducts);
      setComparison(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to compare products');
    } finally {
      setComparing(false);
    }
  };

  const getProductName = (productId: string) => {
    return products.find(p => p.product_id === productId)?.product_name || productId;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="w-12 h-12 text-primary animate-spin" />
      </div>
    );
  }

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

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">Compare Products</h1>
          <p className="text-muted-foreground">
            Select 2-4 products to compare side-by-side
          </p>
        </div>

        {error && (
          <Card className="mb-6 border-destructive">
            <CardContent className="pt-6">
              <p className="text-destructive">{error}</p>
            </CardContent>
          </Card>
        )}

        {/* Product Selection */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Select Products to Compare</CardTitle>
            <CardDescription>
              {selectedProducts.length} of 4 selected
            </CardDescription>
          </CardHeader>
          <CardContent>
            {products.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-muted-foreground mb-4">
                  No completed product analyses available. Add products and analyze them first.
                </p>
                <Link to="/products">
                  <Button>
                    Go to Products <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </Link>
              </div>
            ) : (
              <>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                  {products.map((product) => {
                    const isSelected = selectedProducts.includes(product.product_id);
                    return (
                      <Card
                        key={product.product_id}
                        className={`cursor-pointer transition-all ${
                          isSelected
                            ? 'border-primary border-2 bg-primary/5'
                            : 'border-border hover:border-accent/50'
                        }`}
                        onClick={() => handleToggleProduct(product.product_id)}
                      >
                        <CardContent className="pt-6">
                          <div className="flex items-start gap-3">
                            <Checkbox
                              checked={isSelected}
                              onCheckedChange={() => handleToggleProduct(product.product_id)}
                              onClick={(e) => e.stopPropagation()}
                            />
                            <div className="flex-1">
                              <Label className="font-medium cursor-pointer">
                                {product.product_name}
                              </Label>
                              <p className="text-sm text-muted-foreground mt-1">
                                {new Date(product.created_at).toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
                <Button
                  onClick={handleCompare}
                  disabled={selectedProducts.length < 2 || comparing}
                  className="w-full bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-primary-foreground gap-2"
                >
                  {comparing ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" /> Comparing...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" /> Compare Products
                    </>
                  )}
                </Button>
              </>
            )}
          </CardContent>
        </Card>

        {/* Comparison Results */}
        {comparison && (
          <div className="space-y-6">
            {/* Overall Winner */}
            <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-accent/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Trophy className="w-6 h-6 text-primary" /> Overall Winner
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h3 className="text-2xl font-bold text-foreground mb-2">
                      {getProductName(comparison.overall_winner)}
                    </h3>
                    <p className="text-muted-foreground">{comparison.winner_reasoning}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Comparison Matrix */}
            {Object.keys(comparison.comparison_matrix).length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Feature Comparison</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left p-2">Feature</th>
                          {comparison.compared_products.map((productId) => (
                            <th key={productId} className="text-center p-2">
                              {getProductName(productId)}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(comparison.comparison_matrix).map(([feature, scores]) => (
                          <tr key={feature} className="border-b">
                            <td className="p-2 font-medium capitalize">{feature}</td>
                            {comparison.compared_products.map((productId) => (
                              <td key={productId} className="text-center p-2">
                                {scores[productId] !== undefined ? (
                                  <Badge variant="outline">{scores[productId]}/10</Badge>
                                ) : (
                                  <span className="text-muted-foreground">-</span>
                                )}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Pros & Cons for Each Product */}
            {Object.keys(comparison.pros_cons).length > 0 && (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {comparison.compared_products.map((productId) => {
                  const prosCons = comparison.pros_cons[productId];
                  if (!prosCons) return null;
                  return (
                    <Card key={productId}>
                      <CardHeader>
                        <CardTitle>{getProductName(productId)}</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div>
                          <h4 className="font-semibold mb-2 flex items-center gap-2">
                            <CheckCircle2 className="w-4 h-4 text-green-500" /> Pros
                          </h4>
                          <ul className="space-y-1 text-sm">
                            {prosCons.pros.map((pro, idx) => (
                              <li key={idx} className="flex items-start gap-2">
                                <span className="text-green-500 mt-1">•</span>
                                <span>{pro}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                        <Separator />
                        <div>
                          <h4 className="font-semibold mb-2 flex items-center gap-2">
                            <XCircle className="w-4 h-4 text-red-500" /> Cons
                          </h4>
                          <ul className="space-y-1 text-sm">
                            {prosCons.cons.map((con, idx) => (
                              <li key={idx} className="flex items-start gap-2">
                                <span className="text-red-500 mt-1">•</span>
                                <span>{con}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            )}

            {/* Verdict by Use Case */}
            {Object.keys(comparison.verdict_by_use_case).length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Best For</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-4">
                    {Object.entries(comparison.verdict_by_use_case).map(([useCase, productId]) => (
                      <div key={useCase} className="p-4 border rounded-lg">
                        <h4 className="font-semibold mb-2 capitalize">{useCase}</h4>
                        <Badge variant="outline">{getProductName(productId)}</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Key Differences */}
            {comparison.key_differences.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Key Differences</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {comparison.key_differences.map((diff, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="text-primary mt-1">•</span>
                        <span>{diff}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}

            {/* Summary */}
            {comparison.summary && (
              <Card>
                <CardHeader>
                  <CardTitle>Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  {comparison.summary.recommendation && (
                    <p className="text-muted-foreground">{comparison.summary.recommendation}</p>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

