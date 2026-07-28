import { createContext, useContext, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { authService } from "../services/auth";
import toast from "react-hot-toast";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem("user");
      return stored ? JSON.parse(stored) : null;
    } catch {
      localStorage.removeItem("user");
      return null;
    }
  });
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [refreshToken, setRefreshToken] = useState(
    () => localStorage.getItem("refresh_token")
  );
  const navigate = useNavigate();

  const login = useCallback(
    async (email, password) => {
      const { data } = await authService.login(email, password);
      if (data.success) {
        const { access_token, refresh_token, user: userData } = data.data;
        localStorage.setItem("token", access_token);
        localStorage.setItem("refresh_token", refresh_token);
        localStorage.setItem("user", JSON.stringify(userData));
        setToken(access_token);
        setRefreshToken(refresh_token);
        setUser(userData);
        toast.success("Welcome back!");
        navigate("/dashboard");
      }
    },
    [navigate]
  );

  const logout = useCallback(async () => {
    try {
      await authService.logout(refreshToken);
    } catch {
      // ignore logout errors
    }
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    setToken(null);
    setRefreshToken(null);
    setUser(null);
    navigate("/login");
  }, [navigate, refreshToken]);

  const isAuthenticated = !!token;

  return (
    <AuthContext.Provider
      value={{ user, token, refreshToken, login, logout, isAuthenticated }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
