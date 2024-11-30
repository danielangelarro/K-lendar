import React, { 
  createContext, 
  useContext, 
  ReactNode, 
  useState, 
  useEffect 
} from 'react';

// Interfaz de usuario
export interface User {
  id: string;
  name: string;
  email: string;
}

// Tipo de contexto de autenticación
interface AuthContextType {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  signIn: (token: string, userData: User) => void;
  signOut: () => void;
}

// Crear contexto
const AuthContext = createContext<AuthContextType>({
  token: null,
  user: null,
  isAuthenticated: false,
  signIn: () => {},
  signOut: () => {}
});

// Proveedor de contexto
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Estado de autenticación
  const [token, setToken] = useState<string | null>(() => {
    try {
      return localStorage.getItem('authToken');
    } catch {
      return null;
    }
  });

  const [user, setUser] = useState<User | null>(() => {
    try {
      const storedUser = localStorage.getItem('authUser');
      return storedUser ? JSON.parse(storedUser) : null;
    } catch {
      return null;
    }
  });

  // Método de inicio de sesión
  const signIn = (newToken: string, userData: User) => {
    try {
      localStorage.setItem('authToken', newToken);
      localStorage.setItem('authUser', JSON.stringify(userData));
      setToken(newToken);
      setUser(userData);
    } catch {
      // Manejar error de almacenamiento
    }
  };

  // Método de cierre de sesión
  const signOut = () => {
    try {
      localStorage.removeItem('authToken');
      localStorage.removeItem('authUser');
      setToken(null);
      setUser(null);
    } catch {
      // Manejar error de eliminación
    }
  };

  // Verificar autenticación
  const isAuthenticated = !!token;

  // Validar token (opcional)
  useEffect(() => {
    if (token) {
      try {
        const payload = token.split('.')[1];
        const decodedPayload = JSON.parse(atob(payload));
        
        // Verificar expiración
        if (Date.now() >= decodedPayload.exp * 1000) {
          signOut();
        }
      } catch {
        signOut();
      }
    }
  }, [token]);

  // Valor del contexto
  const contextValue = {
    token,
    user,
    isAuthenticated,
    signIn,
    signOut
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook personalizado para usar el contexto
export const useAuthContext = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }
  return context;
};