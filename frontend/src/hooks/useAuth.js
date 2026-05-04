import { useState, useEffect } from 'react';

export const useAuth = () => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showAccountSettings, setShowAccountSettings] = useState(false);

  // --- Persist Session On Refresh ---
  useEffect(() => {
    const savedUser = localStorage.getItem('ecommerce_user');
    if (savedUser) {
      setCurrentUser(JSON.parse(savedUser));
    }
  }, []);
  
  // --- Automatically Switches Between Local Testing And Vercel Cloud URL ---
  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
  
  // --- Login Function ---
  const login = async (username, password) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        // --- Parse Pydantic Validation Arrays For Login ---
        if (Array.isArray(data.detail)) {
           throw new Error(data.detail[0].msg); 
        }
        throw new Error(data.detail || 'Failed to login');
      }

      const userData = { username, token: data.access_token };
      setCurrentUser(userData);
      localStorage.setItem('ecommerce_user', JSON.stringify(userData));
      return { success: true };

    } catch (err) {
      setError(err.message);
      return { success: false };
    } finally {
      setLoading(false);
    }
  };
  
  // --- Register Function ---
  const register = async (username, email, password) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        if (Array.isArray(data.detail)) {
           throw new Error(data.detail[0].msg); 
        }
        throw new Error(data.detail || 'Registration failed');
      }

      return await login(username, password);

    } catch (err) {
      setError(err.message);
      return { success: false };
    } finally {
      setLoading(false);
    }
  };
  
  // --- Logout Function ---
  const logout = () => {
    setCurrentUser(null);
    localStorage.removeItem('ecommerce_user');
  };

  // --- Return Object ---
  return { 
    currentUser, login, register, logout, loading, error, setError,
    showAuthModal, setShowAuthModal,
    showAccountSettings, setShowAccountSettings
  };
};