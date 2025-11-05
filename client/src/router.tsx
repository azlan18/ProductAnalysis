import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import ProductsPage from './pages/ProductsPage';
import ProductDetailPage from './pages/ProductDetailPage';
import ComparePage from './pages/ComparePage';

const router = createBrowserRouter([
  {
    path: '/',
    element: <LandingPage />,
  },
  {
    path: '/products',
    element: <ProductsPage />,
  },
  {
    path: '/products/:productId',
    element: <ProductDetailPage />,
  },
  {
    path: '/compare',
    element: <ComparePage />,
  },
]);

export function AppRouter() {
  return <RouterProvider router={router} />;
}

