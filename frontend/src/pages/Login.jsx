import { BriefcaseBusiness, LogIn, UserRound } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";
import "../styles/auth.css";

function Login() {
  const navigate = useNavigate();
  const [role, setRole] = useState("");
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const handleChange = (event) => setFormData({ ...formData, [event.target.name]: event.target.value });
  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!formData.email || !formData.password) { setMessage("Enter your email and password to continue."); return; }
    try {
      setLoading(true); setMessage("");
      if (role === "freelancer") {
        const response = await api.post("/freelancer/login", formData);
        localStorage.setItem("freelancer_token", response.data.access_token); localStorage.setItem("freelancer", JSON.stringify(response.data.user)); localStorage.setItem("freelancer_id", response.data.user.freelancer_id); navigate(`/freelancer-dashboard/${response.data.user.freelancer_id}`); return;
      }
      const response = await api.post("/auth/login", formData);
      localStorage.setItem("token", response.data.access_token); localStorage.setItem("user", response.data.user?.full_name || formData.email); navigate("/dashboard");
    } catch (error) { setMessage(error.response?.data?.detail || "Login failed. Please try again."); } finally { setLoading(false); }
  };
  return <main className="auth-shell"><div className="auth-orbit orbit-one" /><div className="auth-orbit orbit-two" /><nav className="auth-nav"><button className="brand" onClick={() => navigate("/")}><span className="brand-mark"><LogIn size={16} /></span><span>Briefly<span className="brand-dot">.</span></span></button><span>New here? <button className="auth-nav-link" onClick={() => navigate("/register")}>Create an account</button></span></nav><section className="auth-layout"><div className="auth-aside"><span className="eyebrow"><span className="eyebrow-line" /> welcome back</span><h1>Good work is waiting on the other side of <em>clarity.</em></h1><p>Pick up where you left off, with your project context and next best step in one place.</p></div><div className="auth-card">{!role ? <RolePicker onSelect={setRole} /> : <><button className="back-link" onClick={() => { setRole(""); setMessage(""); }}>← Choose a different role</button><span className="auth-icon">{role === "client" ? <UserRound size={20} /> : <BriefcaseBusiness size={20} />}</span><p className="auth-kicker">{role === "client" ? "CLIENT WORKSPACE" : "FREELANCER WORKSPACE"}</p><h2>Welcome back</h2><p className="auth-subtitle">Sign in to continue your {role === "client" ? "project journey" : "freelance journey"}.</p><form onSubmit={handleSubmit}><label>Email address<input type="email" name="email" placeholder="you@example.com" value={formData.email} onChange={handleChange} /></label><label>Password<input type="password" name="password" placeholder="Your password" value={formData.password} onChange={handleChange} /></label><button className="auth-submit" type="submit" disabled={loading}>{loading ? "Signing in..." : "Sign in"}<LogIn size={16} /></button></form>{message && <div className="form-message">{message}</div>}</>}</div></section></main>;
}

function RolePicker({ onSelect }) { return <><p className="auth-kicker">YOUR WORKSPACE</p><h2>Who are you?</h2><p className="auth-subtitle">Choose your workspace to continue.</p><div className="role-grid"><button className="role-card" onClick={() => onSelect("client")}><span className="role-icon"><UserRound size={21} /></span><span><b>Client</b><small>Build something meaningful</small></span><span className="role-arrow">→</span></button><button className="role-card" onClick={() => onSelect("freelancer")}><span className="role-icon"><BriefcaseBusiness size={21} /></span><span><b>Freelancer</b><small>Find work worth doing</small></span><span className="role-arrow">→</span></button></div></>; }

export default Login;
