import { useState, useEffect } from 'react';
import GitHubLink from './components/GitHubLink';
import SearchFilterBar from './components/SearchFilterBar';
import ProductCard from './components/ProductCard';
import CartDrawer from './components/CartDrawer';
import AuthModal from './components/AuthModal';
import AccountSettings from './components/AccountSetting';
import OrderList from './components/OrderList';
import AdminCartView from './components/AdminCartView';
import { useAuth } from './hooks/useAuth';
import { useCart } from './hooks/useCart';
import { useOrders } from './hooks/useOrder';
import { getProducts } from './services/api';

function App() {
  // --- React State Management: Products & UX ---
  const [products, setProducts] = useState([]); // --- Products Data ---
  const [isLoading, setIsLoading] = useState(true); // --- Skeletons ---
  const [toastMessage, setToastMessage] = useState(null); // --- Feedback Loops ---
  const [searchQuery, setSearchQuery] = useState(""); // --- Search State ---
  const [selectedCategory, setSelectedCategory] = useState("All"); // --- Filter State ---
  const categories = ["All", ...new Set(products.map(item => item.category))]; // --- Dynamic Categories From Products Data ---
  const [currentView, setCurrentView] = useState("products");
  
  // --- Search & Filter Logic ---
  const filteredProducts = products.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === "All" || product.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // --- Initialize Custom Hooks (Code Quality Points) ---
  const auth = useAuth();
  const currentUser = auth.currentUser;
  const cart = useCart(currentUser, auth.setShowAuthModal, setToastMessage);
  const orders = useOrders(currentUser);
  
  

  // --- Fetch Products When The Page First Loads ---
  useEffect(() => {
    setIsLoading(true);
    getProducts()
      .then(data => setProducts(data))
      .catch(err => console.error("Error fetching products:", err))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      {/* --- Top Navigation --- */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex justify-between items-center">
    
          {/* --- Brand Section --- */}
          <div 
            onClick={() => setCurrentView("products")}
            className="flex items-center gap-3 cursor-pointer hover:opacity-90 transition"
          >
            <img 
              src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAMAAACahl6sAAAAb1BMVEX///8AAAA/Pz+/v7/b29vn5+cfHx93d3ejo6MjIyOXl5dfX1+np6dbW1uDg4NDQ0OLi4uRkZEYGBiJiYmwsLArKyt8fHzv7++cnJz5+fnFxcVxcXEPDw/o6Oi2trbPz882NjZUVFROTk5oaGgSEhJf9aVUAAAC00lEQVR4nO3c61aqQBiAYVDQtBTPiCc8dP/X2A5wyR4FRvmGoXqff66FA28ZTAXjOAAAAAAAAAAAAAAAAAD+sNBrmh/JV2xGn64Fx2komhGebFQkZgvBDn9greOfiVhHtLTZ4bofUiFbux3ubi/T4VvucN2+TMg0He3Y9ZvmjdNdz2RCzslgSwPn9GrDtMQTGSz9UZc7dzwj2iU7P4gMlp5730TGelov2bnMeYsQCb8m5PDxzRcZy2qIJELahpC2MRMSr4cvWrw6WTISUudXg96LUy8TId0aHa4btCdkVStk156Qfq0QlxBTIb1nzdoZ0nn6fRtCHEJKEUKIQ0gpQn5LSLhJvLbTNoXUQkgJQuogpIR+SDgcV9D+/7XVEC/7VapMoPn3Iashp+oO113r7dRqiNatChe9nVoN6emEvOvtlJAST4YsgwKzHxZS+D/EESFCCFEQIoUQBSFSCFEQIoUQBSFSCFEQIoUQBSFSCFEQIoUQBSFSCFEQIoUQxd8MmW+/xbrHqMVKiAmEKAiR0kCId+kYFVeHRKvO6XqTnBoSTYJz7snd4hBf496PWrrVIZ3bdnch7/+/LA6p94SKSEj6tE/wMMRLXg40Qi72Q97yB6uEpJG3J3qKQxb2Q9Kv+uhhyF55X3FI9iS8zZDk493zH4YkSw583mYZJWet7Lm67d3jf9NikzvzO9f73fzqEGczXl8XqLk7/cbzYW5RjpKQbM0Nw7cbNnFBzL4lZtd4aCIkzK4kMgtGFGhkipKduHbdV49SQzNzreu1xOCnq5mQqJOVDMaHrrQwF7Is2W6TD1kVbRWUhjihweWb8teRMst8SIXiafzeXEmzIU4Y1D7iAg2HOM649iE/loZMKrfLQo46Y5YvWxWfax/0I2mIXzmly0LWGkPuqlYciPtH+SlkdnWKOxXbZSHOsPLDdTR5wQMAAAAAAAAAAAAAAAAA4Ef4AjfzQaRIA30BAAAAAElFTkSuQmCC" 
              alt="Zijian Logo" 
              className="w-8 h-8 md:w-10 md:h-10 object-contain" 
            />
            <h1 className="text-xl md:text-2xl font-extrabold text-orange-600 tracking-tight leading-none">
              Zijian <span className="text-yellow-500">Electronic </span><span className="text-red-700">Devices </span><span className="text-gray-900">EBuy </span>
            </h1>
          </div>

          {/* --- Actions Section --- */}
          <div className="flex items-center gap-2 sm:gap-6">
            {!currentUser ? (
              <button 
                onClick={() => auth.setShowAuthModal(true)}
                className="text-sm font-bold text-gray-700 hover:text-orange-600 transition px-3 py-2"
              >
                Login / Register
              </button>
            ) : (
              <div className="flex items-center gap-4">         
                {/* --- User Information + Log Out --- */}
                <div className="hidden md:flex items-center gap-4 text-sm border-r border-gray-200 pr-4">
                  <button 
                    onClick={() => auth.setShowAccountSettings(true)}
                    className="font-medium text-gray-600 hover:text-orange-600 transition"
                    title="Click to Manage Your Account Settings"
                  >
                    Hi, {currentUser.username}
                    
                  </button>
                  <button 
                    onClick={auth.logout}
                    className="text-xs font-bold text-gray-400 hover:text-red-500 transition uppercase tracking-wider"
                  >
                    Logout
                  </button>
                </div> 

                {/* --- Cart + Order Button --- */}
                <button 
                  onClick={() => {
                  if (!auth.currentUser) {
                    auth.setShowAuthModal(true);
                    } else {
                    cart.setIsCartOpen(true);
                    }
                  }}
                  className="relative bg-blue-800 text-white p-2 sm:px-5 sm:py-2.5 rounded-full font-bold hover:bg-blue-600 transition shadow-md flex items-center gap-2"
                  title="View Your Cart, Please Checkout to Place Orders"
                >
                  <span className="hidden sm:inline">Cart</span>
                  
                  {/* --- Simple Cart Icon Placeholder --- */}
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                  {cart.totalCartItems > 0 && (
                    <span className="absolute -top-1 -right-1 bg-orange-500 text-white text-[10px] w-5 h-5 flex items-center justify-center rounded-full border-2 border-white">
                      {cart.totalCartItems}
                    </span>
                  )}
                </button>
                {currentUser && currentUser.role !== "admin" && (
                  <button
                    onClick={() => orders.setShowOrderModal(true)}
                    className="relative bg-green-800 text-white p-2 sm:px-5 sm:py-2.5 rounded-full font-bold hover:bg-green-600 transition shadow-md flex items-center gap-2"
                    title="View Your All Historical Orders"
                  >
                    Orders
                  </button>
                )}
                
                {/* --- GitHub Link (Hidden On Mobile) --- */}
                <div className="hidden sm:block">
                  <GitHubLink />
                </div>
              </div>
            )}
          </div>
        </div>
      </header>
      
      {/* --- Main Content --- */}
<main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
  {currentView === "adminCarts" ? (
    <AdminCartView currentUser={currentUser} />
  ) : (
    <>
      {/* --- Search & Filter Bar --- */}
      <SearchFilterBar
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        selectedCategory={selectedCategory}
        setSelectedCategory={setSelectedCategory}
        categories={categories}  
      />
      
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {/* --- Loading Skeletons For Perceived Performance --- */}
        {isLoading ? (
          [...Array(8)].map((_, i) => (
            <div key={i} className="animate-pulse bg-white p-4 rounded-lg shadow-sm border border-gray-100 flex flex-col items-center">
              <div className="w-full h-48 bg-gray-200 rounded-md mb-4"></div>
              <div className="w-3/4 h-4 bg-gray-200 rounded mb-2"></div>
              <div className="w-1/2 h-4 bg-gray-200 rounded"></div>
            </div>
          ))
        ) : filteredProducts.length === 0 ? (
          <div className="col-span-full text-center py-10 text-gray-500 font-medium">
            No products found matching your search.
          </div>
        ) : (
          filteredProducts.map((product) => (
            <ProductCard 
              key={product._id} 
              product={product} 
              onAddToCart={() => cart.handleAddToCart(product)} 
            />
          ))
        )}
      </div>
    </>
  )}
</main>

      {/* --- The SPA Drawer & Modals --- */}
      <CartDrawer 
        isOpen={cart.isCartOpen} 
        onClose={() => cart.setIsCartOpen(false)} 
        cartItems={cart.cartItems} 
        onUpdateQuantity={cart.handleUpdateQuantity}
        onRemoveItem={cart.handleRemoveItem}
        onCheckout={() => {
          orders.handleCheckout(cart.cartItems, cart.clearCart);
          cart.setIsCartOpen(false);
        }}
      />
      
      {/* --- Authentication Modal --- */}
      <AuthModal 
        isOpen={auth.showAuthModal} 
        onClose={() => auth.setShowAuthModal(false)} 
        useAuthHook={auth} 
      />
      
      {/* --- Account Settings Modal --- */}
      <AccountSettings 
        isOpen={auth.showAccountSettings} 
        onClose={() => auth.setShowAccountSettings(false)} 
        currentUser={currentUser}
        logout={auth.logout} 
      />

      {/* --- Order History Modal --- */}
      <OrderList 
        isOpen={orders.showOrderModal} 
        onClose={() => orders.setShowOrderModal(false)} 
        orders={orders.orders} 
      />

      {/* --- Feedback Loops (Toast) --- */}
      {toastMessage && (
        <div className="fixed bottom-5 right-5 bg-gray-900 text-white px-6 py-3 rounded-lg shadow-2xl z-50 flex items-center gap-3">
          <span className="text-green-400 font-bold">✓</span>
          {toastMessage}
        </div>
      )}
    </div>
  );
}

export default App;