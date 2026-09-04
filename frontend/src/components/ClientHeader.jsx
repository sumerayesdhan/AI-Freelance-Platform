import { LogOut, Sparkles } from "lucide-react";
import { useState } from "react";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";
import "../styles/client-header.css";

function ClientHeader() {
  const navigate = useNavigate();
  const [authenticated, setAuthenticated] = useState(Boolean(localStorage.getItem("token")));
  const [userName, setUserName] = useState(localStorage.getItem("user") || "Client");

  useEffect(() => {
    if (!authenticated) return;

    api.get("/dashboard")
      .then((response) => {
        const name = response.data.full_name || response.data.email || "Client";
        setUserName(name);
        localStorage.setItem("user", name);
      })
      .catch(() => {
        setUserName(localStorage.getItem("user") || "Client");
      });
  }, [authenticated]);

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setAuthenticated(false);
    navigate("/login");
  };

  return <header className="client-header"><button className="client-brand" onClick={() => navigate(authenticated ? "/dashboard" : "/")}><span className="client-brand-mark"><Sparkles size={16} /></span><span>Briefly<span className="client-brand-dot">.</span></span></button>{authenticated ? <div className="client-auth-links"><span className="client-user-name">{userName}</span><button className="client-logout" onClick={logout}><LogOut size={16} /> Logout</button></div> : <nav className="client-header-links"><a href="/#how-it-works">How it works</a><a href="/#features">Features</a><button onClick={() => navigate("/login")}>Log in</button><button className="client-header-cta" onClick={() => navigate("/register")}>Get started</button></nav>}</header>;
}

export default ClientHeader;
