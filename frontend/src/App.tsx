import { useState } from "react";
import Login from "./pages/login";
import Dashboard from "./pages/Dashboard";
import "./App.css";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(
    Boolean(localStorage.getItem("access_token")),
  );

  if (!isAuthenticated) {
    return <Login onLoginSuccess={() => setIsAuthenticated(true)} />;
  }

  return (
    <Dashboard
      onLogout={() => {
        localStorage.removeItem("access_token");
        setIsAuthenticated(false);
      }}
    />
  );
}

export default App;
