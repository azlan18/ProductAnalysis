/**
 * API Service for Product Analysis Backend
 * Centralized API calls to backend at http://localhost:8000
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// ========== Types ==========

export interface Product {
  product_id: string;
  product_name: string;
  created_at: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  metadata?: Record<string, any>;
  processing_stats?: Record<string, any>;
}

export interface AnalysisStatus {
  product_id: string;
  stage: string;
  status: string;
  progress: number;
  current_step: string;
  timestamp: string;
  error?: string;
}

export interface CustomerQuote {
  quote: string;
}

export interface AnalysisResult {
  product_id: string;
  analyzed_at: string;
  sentiment: {
    score: number;
    sentiment: string;
    distribution?: {
      positive: number;
      negative: number;
      neutral: number;
    };
  };
  features: {
    [key: string]: {
      sentiment: string;
      score: number;
      mentions: number;
      quotes?: CustomerQuote[];
    };
  };
  top_praises: Array<{
    aspect: string;
    frequency: number;
    percentage: number;
    score: number;
    quotes?: CustomerQuote[];
  }>;
  top_complaints: Array<{
    aspect: string;
    frequency: number;
    percentage: number;
    score: number;
    quotes?: CustomerQuote[];
  }>;
  pros: string[];
  cons: string[];
  general_sentiment: string;
  description: string;
  prices?: Array<{
    platform: string;
    price: string;
    url: string;
  }>;
  summary?: {
    one_liner?: string;
    best_for?: string[];
    not_recommended_for?: string[];
    key_strengths?: string[];
    key_weaknesses?: string[];
    verdict?: string;
    strengths?: string[];
    weaknesses?: string[];
    recommendation?: string;
  };
  user_segments?: Array<{
    segment: string;
    satisfaction: number;
    count: number;
  }>;
  quality_issues?: Array<{
    issue: string;
    frequency: number;
    severity: string;
    quotes?: CustomerQuote[];
  }>;
  competitor_mentions?: Record<string, {
    sentiment: string;
    frequency: number;
    quotes?: CustomerQuote[];
  }>;
  value_analysis?: {
    score: number;
    percentage_saying_worth_it: number;
    reasoning: string;
  };
}

export interface ProductDetail extends Product {
  analysis?: AnalysisResult;
  reviews_count?: number;
}

export interface Comparison {
  comparison_id: string;
  created_at: string;
  compared_products: string[];
  overall_winner: string;
  winner_reasoning: string;
  comparison_matrix: Record<string, Record<string, number>>;
  pros_cons: Record<string, {
    pros: string[];
    cons: string[];
  }>;
  feature_comparison: Record<string, Record<string, any>>;
  verdict_by_use_case: Record<string, string>;
  key_differences: string[];
  summary: {
    recommendation?: string;
    key_differences?: string[];
  };
}

// ========== API Functions ==========

/**
 * Create a new product
 */
export async function createProduct(
  productName: string,
  metadata?: Record<string, any>
): Promise<Product> {
  const response = await fetch(`${API_BASE_URL}/products`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      product_name: productName,
      metadata: metadata || {}
    }),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create product');
  }
  
  return response.json();
}

/**
 * Get all products
 */
export async function getProducts(): Promise<Product[]> {
  const response = await fetch(`${API_BASE_URL}/products`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch products');
  }
  
  const data = await response.json();
  // Backend returns { "products": [...] }
  return data.products || [];
}

/**
 * Get product details by ID
 */
export async function getProduct(productId: string): Promise<ProductDetail> {
  const response = await fetch(`${API_BASE_URL}/products/${productId}`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch product');
  }
  
  const data = await response.json();
  
  // Backend returns analysis fields at top level, we need to nest them
  const hasAnalysis = data.sentiment || data.features || data.top_praises;
  
  if (hasAnalysis) {
    // Extract analysis fields
    const analysis: AnalysisResult = {
      product_id: data.product_id,
      analyzed_at: data.analyzed_at || new Date().toISOString(),
      sentiment: data.sentiment || {
        score: 0,
        sentiment: 'neutral',
        distribution: { positive: 0, negative: 0, neutral: 0 }
      },
      features: data.features || {},
      top_praises: data.top_praises || [],
      top_complaints: data.top_complaints || [],
      pros: data.pros || [],
      cons: data.cons || [],
      general_sentiment: data.general_sentiment || '',
      description: data.description || '',
      prices: (data.prices || []).map((p: any) => ({
        platform: p.source || p.platform || '',
        price: p.price || '',
        url: p.url || ''
      })),
      summary: data.summary || {},
      user_segments: data.user_segments || [],
      quality_issues: data.quality_issues || [],
      competitor_mentions: data.competitor_mentions || {},
      value_analysis: data.value_analysis || undefined
    };
    
    return {
      product_id: data.product_id,
      product_name: data.product_name,
      created_at: data.created_at,
      status: data.status,
      metadata: data.metadata,
      processing_stats: data.processing_stats,
      analysis: analysis,
      reviews_count: data.reviews_count || 0
    };
  } else {
    // No analysis yet
    return {
      product_id: data.product_id,
      product_name: data.product_name,
      created_at: data.created_at,
      status: data.status,
      metadata: data.metadata,
      processing_stats: data.processing_stats,
      reviews_count: data.reviews_count || 0
    };
  }
}

/**
 * Start product analysis
 */
export async function analyzeProduct(productId: string): Promise<{ status: string; product_id: string }> {
  const response = await fetch(`${API_BASE_URL}/products/${productId}/analyze`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to start analysis');
  }
  
  return response.json();
}

/**
 * Get product analysis status
 */
export async function getProductStatus(productId: string): Promise<AnalysisStatus> {
  const response = await fetch(`${API_BASE_URL}/products/${productId}/status`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch status');
  }
  
  return response.json();
}

/**
 * Compare products
 */
export async function compareProducts(productIds: string[]): Promise<Comparison> {
  const response = await fetch(`${API_BASE_URL}/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_ids: productIds }),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to compare products');
  }
  
  return response.json();
}

/**
 * Get comparison by ID
 */
export async function getComparison(comparisonId: string): Promise<Comparison> {
  const response = await fetch(`${API_BASE_URL}/compare/${comparisonId}`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch comparison');
  }
  
  return response.json();
}

