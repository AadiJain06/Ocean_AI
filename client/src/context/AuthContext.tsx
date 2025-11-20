import { createContext, useContext, useEffect, useMemo, useState } from "react";

type AuthContextValue = {
  token: string | null;
  email: string | null;
  login: (token: string, email: string) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [email, setEmail] = useState<string | null>(null);

  useEffect(() => {
    const savedToken = localStorage.getItem("auth_token");
    const savedEmail = localStorage.getItem("auth_email");
    if (savedToken) {
      setToken(savedToken);
    }
    if (savedEmail) {
      setEmail(savedEmail);
    }
  }, []);

  const login = (newToken: string, newEmail: string) => {
    localStorage.setItem("auth_token", newToken);
    localStorage.setItem("auth_email", newEmail);
    setToken(newToken);
    setEmail(newEmail);
  };

  const logout = () => {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("auth_email");
    setToken(null);
    setEmail(null);
  };

  const value = useMemo(
    () => ({
      token,
      email,
      login,
      logout,
    }),
    [token, email]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("AuthProvider missing");
  }
  return ctx;
}

