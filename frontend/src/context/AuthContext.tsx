import React, { createContext, useContext, ReactNode } from 'react';
import useAuth, { User } from '../hooks/useAuth';

interface AuthContextType {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  signIn: (token: string, userData: User) => void;
  signOut: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const auth = useAuth();

  return (
    <AuthContext.Provider value={auth}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuthContext = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }
  return context;
};