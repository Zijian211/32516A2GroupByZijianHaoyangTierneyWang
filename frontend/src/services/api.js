// --- Automatically Switches Between Local Testing And Vercel Cloud URL ---
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// --- Get Token From localStorage ---
const getAuthHeader = () => {
  const token = localStorage.getItem('access_token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

// --- Product Services (No Auth Required) ---
export const getProducts = async () => {
  const response = await fetch(`${API_URL}/products`);
  if (!response.ok) throw new Error("Failed to fetch products");
  return response.json();
};

// --- Cart Services ---
export const addToCartApi = async (itemData) => {
  const response = await fetch(`${API_URL}/cart`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeader() },
    body: JSON.stringify(itemData)
  });
  if (!response.ok) throw new Error("Failed to add to cart");
  return response.json();
};

export const getCartApi = async (userId) => {
  const response = await fetch(`${API_URL}/cart/${userId}`, {
    headers: { ...getAuthHeader() }
  });
  if (!response.ok) throw new Error("Failed to fetch cart");
  return response.json();
};

export const updateCartQuantityApi = async (userId, productId, quantity) => {
  const response = await fetch(`${API_URL}/cart/${userId}/${productId}?quantity=${quantity}`, {
    method: "PUT",
    headers: { ...getAuthHeader() }
  });
  if (!response.ok) throw new Error("Failed to update quantity");
  return response.json();
};

export const removeCartItemApi = async (userId, productId) => {
  const response = await fetch(`${API_URL}/cart/${userId}/${productId}`, {
    method: "DELETE",
    headers: { ...getAuthHeader() }
  });
  if (!response.ok) throw new Error("Failed to remove item");
  return response.json();
};

// --- Account Management Services ---
export const changePasswordApi = async (userId, passwordData) => {
  const response = await fetch(`${API_URL}/users/${userId}/password`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...getAuthHeader() },
    body: JSON.stringify(passwordData)
  });
  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || "Password change failed");
  }
  return response.json();
};

export const deleteAccountApi = async (userId) => {
  const response = await fetch(`${API_URL}/users/${userId}`, {
    method: "DELETE",
    headers: { ...getAuthHeader() }
  });
  if (!response.ok) throw new Error("Failed to delete account");
  return response.json();
};

// --- Order Services ---
export const checkoutApi = async (userId) => {
  const response = await fetch(`${API_URL}/orders?user_id=${userId}`, {
    method: "POST",
    headers: { ...getAuthHeader() }
  });
  if (!response.ok) throw new Error("Checkout failed");
  return response.json();
};

export const fetchOrdersApi = async (userId) => {
  const response = await fetch(`${API_URL}/orders/${userId}`, {
    headers: { ...getAuthHeader() }
  });
  if (!response.ok) throw new Error("Failed to fetch orders");
  return response.json();
};