import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Loader2, Plus, Sparkles, BarChart3 } from 'lucide-react';
import { getProducts, createProduct } from '@/lib/api';
import type { Product } from '@/lib/api';

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [productName, setProductName] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getProducts();
      setProducts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load products');
      console.error('Failed to load products:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProduct = async () => {
    if (!productName.trim()) return;

    try {
      setCreating(true);
      const newProduct = await createProduct(productName.trim());
      await loadProducts();
      setShowCreateModal(false);
      setProductName('');
    } catch (err) {
      console.error('Failed to create product:', err);
      alert(err instanceof Error ? err.message : 'Failed to create product');
    } finally {
      setCreating(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500/10 text-green-500 border-green-500/20';
      case 'processing':
        return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
      case 'failed':
        return 'bg-red-500/10 text-red-500 border-red-500/20';
      default:
        return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg">
              <BarChart3 className="w-6 h-6 text-primary-foreground" />
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Product Intelligence
            </span>
          </Link>
          <div className="flex items-center gap-4">
            <Link to="/compare">
              <Button variant="outline" className="gap-2">
                <Sparkles className="w-4 h-4" /> Compare
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header Section */}
        {!loading && !error && products.length > 0 && (
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-foreground mb-2">My Products</h1>
              <p className="text-muted-foreground">
                Manage your product analyses and insights
              </p>
            </div>
            <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
              <DialogTrigger asChild>
                <Button
                  className="bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-primary-foreground gap-2 h-11 px-6"
                >
                  <Plus className="w-5 h-5" /> Add New Product
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Add New Product</DialogTitle>
                  <DialogDescription>
                    Enter the product name to start analysis. Our AI will search for reviews and analyze them.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="product-name">Product Name</Label>
                    <Input
                      id="product-name"
                      placeholder="e.g., iPhone 15 Pro"
                      value={productName}
                      onChange={(e) => setProductName(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && !creating) {
                          handleCreateProduct();
                        }
                      }}
                    />
                  </div>
                  <Button
                    onClick={handleCreateProduct}
                    disabled={!productName.trim() || creating}
                    className="w-full"
                  >
                    {creating ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" /> Creating...
                      </>
                    ) : (
                      'Add Product'
                    )}
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        )}

        {/* Products Grid */}
        {loading ? (
          <div className="text-center py-24">
            <Loader2 className="w-12 h-12 text-primary animate-spin mx-auto mb-4" />
            <p className="text-muted-foreground">Loading products...</p>
          </div>
        ) : error ? (
          <div className="text-center py-24">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-destructive/10 mb-6">
              <Sparkles className="w-10 h-10 text-destructive" />
            </div>
            <h2 className="text-3xl font-bold text-foreground mb-3">Error loading products</h2>
            <p className="text-muted-foreground mb-8 max-w-md mx-auto text-lg">{error}</p>
            <Button onClick={loadProducts} variant="outline">
              Try Again
            </Button>
          </div>
        ) : products.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {products.map((product) => (
              <Link key={product.product_id} to={`/products/${product.product_id}`}>
                <Card className="border border-border hover:border-accent/50 transition-all duration-300 cursor-pointer group h-full">
                  <CardHeader>
                    <div className="flex items-start justify-between mb-2">
                      <CardTitle className="group-hover:text-accent transition-colors">
                        {product.product_name}
                      </CardTitle>
                      <Badge className={getStatusColor(product.status)}>
                        {product.status}
                      </Badge>
                    </div>
                    <CardDescription>
                      Added {new Date(product.created_at).toLocaleDateString()}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      {product.status === 'processing' && (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      )}
                      {product.status === 'completed' && (
                        <BarChart3 className="w-4 h-4 text-green-500" />
                      )}
                      <span>
                        {product.status === 'completed' && 'Analysis complete'}
                        {product.status === 'processing' && 'Analyzing...'}
                        {product.status === 'pending' && 'Ready to analyze'}
                        {product.status === 'failed' && 'Analysis failed'}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        ) : (
          <div className="text-center py-24">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-primary/10 to-accent/10 mb-6">
              <Sparkles className="w-10 h-10 text-primary" />
            </div>
            <h2 className="text-3xl font-bold text-foreground mb-3">No products yet</h2>
            <p className="text-muted-foreground mb-8 max-w-md mx-auto text-lg">
              Add your first product to start analyzing reviews and getting insights
            </p>
            <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
              <DialogTrigger asChild>
                <Button
                  className="bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-primary-foreground gap-2 h-11 px-6"
                >
                  <Plus className="w-4 h-4" /> Add First Product
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Add New Product</DialogTitle>
                  <DialogDescription>
                    Enter the product name to start analysis. Our AI will search for reviews and analyze them.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="product-name">Product Name</Label>
                    <Input
                      id="product-name"
                      placeholder="e.g., iPhone 15 Pro"
                      value={productName}
                      onChange={(e) => setProductName(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && !creating) {
                          handleCreateProduct();
                        }
                      }}
                    />
                  </div>
                  <Button
                    onClick={handleCreateProduct}
                    disabled={!productName.trim() || creating}
                    className="w-full"
                  >
                    {creating ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" /> Creating...
                      </>
                    ) : (
                      'Add Product'
                    )}
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        )}
      </main>
    </div>
  );
}

