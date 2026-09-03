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

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!role) {
            setMessage("Select Client or Freelancer to continue");
            return;
        }
        if (!formData.email || !formData.password) {
            setMessage("Please enter email and password");
            return;
        }
        try {
            setLoading(true);
            const response = await api.post("/auth/login", { ...formData, role });
            const user = response.data.user || { email: formData.email, role: "client" };
            localStorage.setItem("token", response.data.access_token);
            localStorage.setItem("user", JSON.stringify({ ...user, role }));
            navigate(user.role === "freelancer" ? "/freelancer-dashboard" : "/dashboard");
        } catch (error) {
            setMessage(error.response?.data?.detail || "Login failed");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <div className="auth-intro"><p className="auth-kicker">FreelanceConnect</p><h1>Welcome back</h1><p>Connect with skilled talent, shape your project, and reach a fair agreement with AI assistance.</p></div>
                {!role ? <div className="role-selection"><h2>Who are you logging in as?</h2><div className="role-options"><button type="button" onClick={() => setRole("client")}>Client</button><button type="button" onClick={() => setRole("freelancer")}>Freelancer</button></div></div> : <form onSubmit={handleSubmit}>
                    <div className="selected-role"><span>{role === "client" ? "Client" : "Freelancer"}</span><button type="button" onClick={() => setRole("")}>Change</button></div>
                    <input type="email" name="email" placeholder="Email Address" value={formData.email} onChange={(event) => setFormData({ ...formData, email: event.target.value })} />
                    <input type="password" name="password" placeholder="Password" value={formData.password} onChange={(event) => setFormData({ ...formData, password: event.target.value })} />
                    <button type="submit" disabled={loading}>{loading ? "Logging in..." : "Login"}</button>
                </form>}
                <p>Don't have a client account? <span onClick={() => navigate("/register")}>Register</span></p>
                {message && <div className="message">{message}</div>}
            </div>
        </div>
    );
}

export default Login;
