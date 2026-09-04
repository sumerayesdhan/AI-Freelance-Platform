import { BriefcaseBusiness, ArrowRight, UserRound } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";
import "../styles/auth.css";

function Register() {
  const navigate = useNavigate();
  const [role, setRole] = useState("");
  const [formData, setFormData] = useState({ full_name: "", email: "", password: "", freelancer_id: "", title: "", skills: "", hourly_rate: "", country: "" });
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const handleChange = (event) => setFormData({ ...formData, [event.target.name]: event.target.value });
  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!formData.full_name || !formData.email || !formData.password || (role === "freelancer" && !formData.freelancer_id)) { setMessage("Please fill in all required fields."); return; }
    if (formData.password.length < 8) { setMessage("Password must contain at least 8 characters."); return; }
    try {
      setLoading(true); setMessage("");
      if (role === "freelancer") {
        const response = await api.post("/freelancer/register", { freelancer_id: Number(formData.freelancer_id), full_name: formData.full_name, email: formData.email, password: formData.password, title: formData.title, skills: formData.skills, hourly_rate: formData.hourly_rate ? Number(formData.hourly_rate) : 0, country: formData.country });
        localStorage.setItem("freelancer_id", response.data.freelancer_id); localStorage.setItem("freelancer_name", response.data.name); navigate(`/freelancer-dashboard/${response.data.freelancer_id}`); return;
      }
      const response = await api.post("/auth/register", { full_name: formData.full_name, email: formData.email, password: formData.password });
      setMessage(response.data.message || "Account created. You can sign in now."); setTimeout(() => navigate("/login"), 900);
    } catch (error) { setMessage(error.response?.data?.detail || "Registration failed. Please try again."); } finally { setLoading(false); }
  };
  return <main className="auth-shell"><div className="auth-orbit orbit-one" /><div className="auth-orbit orbit-two" /><nav className="auth-nav"><button className="brand" onClick={() => navigate("/")}><span className="brand-mark"><ArrowRight size={16} /></span><span>Briefly<span className="brand-dot">.</span></span></button><span>Already a member? <button className="auth-nav-link" onClick={() => navigate("/login")}>Sign in</button></span></nav><section className="auth-layout"><div className="auth-aside"><span className="eyebrow"><span className="eyebrow-line" /> make your next move</span><h1>There is better work out there. Start by choosing your <em>lane.</em></h1><p>Whether you are building the brief or bringing the craft, Briefly gives you the context to move with confidence.</p></div><div className="auth-card">{!role ? <RolePicker onSelect={setRole} /> : <><button className="back-link" onClick={() => { setRole(""); setMessage(""); }}>← Choose a different role</button><span className="auth-icon">{role === "client" ? <UserRound size={20} /> : <BriefcaseBusiness size={20} />}</span><p className="auth-kicker">JOIN AS A {role.toUpperCase()}</p><h2>Create your account</h2><p className="auth-subtitle">A thoughtful workspace for better freelance work.</p><form onSubmit={handleSubmit}><label>{role === "freelancer" ? "Freelancer ID" : "Full name"}<input type={role === "freelancer" ? "number" : "text"} name={role === "freelancer" ? "freelancer_id" : "full_name"} placeholder={role === "freelancer" ? "Your unique ID" : "Your full name"} value={formData[role === "freelancer" ? "freelancer_id" : "full_name"]} onChange={handleChange} /></label>{role === "freelancer" && <label>Full name<input type="text" name="full_name" placeholder="Your full name" value={formData.full_name} onChange={handleChange} /></label>}<label>Email address<input type="email" name="email" placeholder="you@example.com" value={formData.email} onChange={handleChange} /></label><label>Password<input type="password" name="password" placeholder="Create a secure password" value={formData.password} onChange={handleChange} /></label>{role === "freelancer" && <div className="form-grid"><label>Specialty<input type="text" name="title" placeholder="Product designer" value={formData.title} onChange={handleChange} /></label><label>Hourly rate<input type="number" name="hourly_rate" placeholder="75" value={formData.hourly_rate} onChange={handleChange} /></label><label className="full-field">Skills<input type="text" name="skills" placeholder="Research, UX, Figma" value={formData.skills} onChange={handleChange} /></label><label className="full-field">Country<input type="text" name="country" placeholder="Where you work from" value={formData.country} onChange={handleChange} /></label></div>}<button className="auth-submit" type="submit" disabled={loading}>{loading ? "Creating account..." : "Create account"}<ArrowRight size={16} /></button></form>{message && <div className="form-message">{message}</div>}</>}</div></section></main>;
}

function RolePicker({ onSelect }) { return <><p className="auth-kicker">YOUR WORKSPACE</p><h2>Join as a</h2><p className="auth-subtitle">Choose how you want to use Briefly.</p><div className="role-grid"><button className="role-card" onClick={() => onSelect("client")}><span className="role-icon"><UserRound size={21} /></span><span><b>Client</b><small>Turn an idea into a plan</small></span><span className="role-arrow">→</span></button><button className="role-card" onClick={() => onSelect("freelancer")}><span className="role-icon"><BriefcaseBusiness size={21} /></span><span><b>Freelancer</b><small>Find your next right fit</small></span><span className="role-arrow">→</span></button></div></>; }
export default Register;
