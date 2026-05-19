import { useState } from "react";
import { useAuth } from "./context/AuthContext";
import LoginPage from "./components/LoginPage";
import RegisterPage from "./components/RegisterPage";
import TaskDashboard from "./components/TaskDashboard";

export default function App() {
  const { token, user, logout } = useAuth();
  const [showRegister, setShowRegister] = useState(false);

  // Not logged in show auth pages
  if (!token) {
    return showRegister ? (
      <RegisterPage onSwitch={() => setShowRegister(false)} />
    ) : (
      <LoginPage onSwitch={() => setShowRegister(true)} />
    );
  }

  // Logged in show the main app
  return <TaskDashboard user={user} onLogout={logout} />;
}
