import { useEffect, useCallback } from 'react';
import useLocalStorage from './useLocalStorage';

export interface User {
  // Define las propiedades del usuario si es necesario
}

function useAuth() {
  const [token, setToken] = useLocalStorage<string | null>('authToken', null);
  const [user, setUser] = useLocalStorage<User | null>('authUser', null);

  useEffect(() => {
    if (token) {
      // Verificar si el token es válido y obtener datos del usuario
      const payloadBase64 = token.split('.')[1];
      const decodedPayload = JSON.parse(atob(payloadBase64));
      const exp = decodedPayload.exp;
      
      if (Date.now() >= exp * 1000) {
        setToken(null);
        setUser(null);
      }
    }
  }, [token, setToken, setUser]);

  const signIn = useCallback((newToken: string, userData: User) => {
    setToken(newToken);
    setUser(userData);
  }, [setToken, setUser]);

  const signOut = useCallback(() => {
    setToken(null);
    setUser(null);
  }, [setToken, setUser]);

  const isAuthenticated = Boolean(token);

  return {
    token,
    user,
    isAuthenticated,
    signIn,
    signOut,
  };
}

export default useAuth;