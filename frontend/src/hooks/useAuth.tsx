import { useEffect, useCallback } from 'react';

export interface User {
  id: string;
  name: string;
  email: string;
}

// Función de utilidad para parsear JSON de manera segura
const safeParseJSON = <T,>(value: string | null, defaultValue: T): T => {
  if (!value) return defaultValue;
  try {
    return JSON.parse(value);
  } catch (error) {
    console.error('Error parsing JSON:', error);
    return defaultValue;
  }
};

function useAuth() {
  // Métodos seguros para obtener datos de localStorage
  const getTokenFromStorage = () => {
    try {
      return localStorage.getItem('authToken');
    } catch (error) {
      console.error('Error getting token from localStorage:', error);
      return null;
    }
  };

  const getUserFromStorage = () => {
    try {
      const storedUser = localStorage.getItem('authUser');
      return safeParseJSON<User | null>(storedUser, null);
    } catch (error) {
      console.error('Error getting user from localStorage:', error);
      return null;
    }
  };

  // Validar token
  const validateToken = useCallback(() => {
    const token = getTokenFromStorage();
    if (token) {
      try {
        const payloadBase64 = token.split('.')[1];
        const decodedPayload = JSON.parse(atob(payloadBase64));
        
        // Verificar expiración
        return Date.now() < (decodedPayload.exp * 1000);
      } catch (error) {
        console.error('Token validation error:', error);
        localStorage.removeItem('authToken');
        localStorage.removeItem('authUser');
        return false;
      }
    }
    return false;
  }, []);

  // Métodos de autenticación
  const signIn = (newToken: string, userData: User) => {
    try {
      localStorage.setItem('authToken', newToken);
      localStorage.setItem('authUser', JSON.stringify(userData));
    } catch (error) {
      console.error('Error storing auth data:', error);
    }
  };

  const signOut = () => {
    try {
      localStorage.removeItem('authToken');
      localStorage.removeItem('authUser');
    } catch (error) {
      console.error('Error removing auth data:', error);
    }
  };

  // Verificar token al inicio
  useEffect(() => {
    validateToken();
  }, [validateToken]);

  return {
    token: getTokenFromStorage(),
    user: getUserFromStorage(),
    isAuthenticated: validateToken(),
    signIn,
    signOut,
  };
}

export default useAuth;