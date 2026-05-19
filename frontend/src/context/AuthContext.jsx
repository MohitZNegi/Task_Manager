import { createContext, useContext, useState, useCallback } from "react";
import { taskApi } from "../api/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  /*
   * Token is stored in React state (in memory), NOT localStorage.
   * localStorage persists across browser sessions but is readable by
   * any JS on the page (XSS risk). In-memory state is cleared on
   * page refresh — a deliberate security trade-off for this project.
   * Production apps use httpOnly cookies set by the server.
   */
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [error, setError] = useState(null);

  const login = useCallback(async (email, password) => {
    setError(null);
    try {
      const data = await taskApi.login({ email, password });
      setToken(data.access_token);
      // Fetch the user profile immediately after login
      const profile = await taskApi.getMe(data.access_token);
      setUser(profile);
      return true;
    } catch (e) {
      setError(e.message);
      return false;
    }
  }, []);

  const register = useCallback(
    async (email, username, password) => {
      setError(null);
      try {
        await taskApi.register({ email, username, password });
        return await login(email, password); // auto-login after register
      } catch (e) {
        setError(e.message);
        return false;
      }
    },
    [login],
  );

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{ token, user, error, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
