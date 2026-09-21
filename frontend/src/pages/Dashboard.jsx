import { CheckCircle2, Clock3, FilePlus2, LogOut, MessageCircle, MessageSquareText, PanelLeft, Plus, Search, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";
import "../styles/dashboard.css";

function Dashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState("");
  const [history, setHistory] = useState([]);
  const [acceptedProjects, setAcceptedProjects] = useState([]);
  const [project, setProject] = useState({ title: "", description: "" });
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadWorkspace = async () => {
      try {
        const [userResponse, historyResponse, acceptedResponse] = await Promise.all([
          api.get("/dashboard"),
          api.get("/projects/history"),
          api.get("/contract/client-projects")
        ]);
        setUser(userResponse.data.full_name || userResponse.data.email);
        setHistory(historyResponse.data.projects || []);
        setAcceptedProjects(
          (acceptedResponse.data || []).filter(
            (item) => item.status === "BOTH_ACCEPTED"
          )
        );
      } catch (error) {
        console.error(error);
        setMessage("Session expired. Please sign in again.");
        localStorage.removeItem("token");
        navigate("/login");
      }
    };
    loadWorkspace();
  }, [navigate]);

  const handleChange = (event) => setProject({ ...project, [event.target.name]: event.target.value });
  const handleSubmit = async (event) => {
    event.preventDefault();
    if (project.title.length < 3) { setMessage("Project title is too short."); return; }
    if (project.description.length < 20) { setMessage("Please provide more project details."); return; }
    try {
      setLoading(true); setMessage("");
      const response = await api.post("/projects/create", project);
      if (response.data.project_id) navigate(`/requirement-assistance/${response.data.project_id}`);
    } catch (error) { setMessage(error.response?.data?.detail || "Project creation failed."); } finally { setLoading(false); }
  };
  const logout = () => { localStorage.removeItem("token"); localStorage.removeItem("user"); navigate("/login"); };

  return <div className="workspace-shell"><aside className="workspace-sidebar"><div className="workspace-brand"><span className="brand-mark"><Sparkles size={16} /></span><span>Briefly<span className="brand-dot">.</span></span></div><button className="new-project-button" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}><Plus size={16} /> New project</button><div className="sidebar-search"><Search size={15} /><input placeholder="Search projects" aria-label="Search projects" /></div><div className="history-heading"><span>Project history</span><span>{history.length}</span></div><div className="project-history">{history.length === 0 ? <p className="history-empty">Your projects will appear here.</p> : history.map((item) => <button className="history-item" key={item.project_id} onClick={() => navigate(`/requirement-assistance/${item.project_id}`)}><FilePlus2 size={15} /><span>{item.title}</span></button>)}</div><div className="sidebar-footer"><button onClick={() => navigate("/")}><MessageSquareText size={15} /> About Briefly</button><button onClick={logout}><LogOut size={15} /> Sign out</button></div></aside><main className="workspace-main"><header className="workspace-header"><button className="mobile-sidebar-toggle" aria-label="Open project history"><PanelLeft size={18} /></button><div><span className="workspace-eyebrow">CLIENT WORKSPACE</span><h1>Welcome back, {user || "there"}</h1><p>What would you like to make clear today?</p></div><div className="header-status"><span /> Workspace active</div></header><section className="project-composer"><div className="composer-top"><div className="composer-icon"><FilePlus2 size={20} /></div><div><span className="workspace-eyebrow">NEW PROJECT</span><h2>Start with the idea</h2><p>Tell us what you are building. Briefly will help shape the next questions.</p></div></div><form onSubmit={handleSubmit}><label>Project title<input type="text" name="title" placeholder="e.g. Smart education platform" value={project.title} onChange={handleChange} /></label><label>Project description<textarea name="description" rows="7" placeholder="Explain the problem, who it is for, and what a successful outcome looks like..." value={project.description} onChange={handleChange} /></label><div className="composer-footer"><span>Minimum 20 characters</span><button type="submit" disabled={loading}>{loading ? "Creating..." : "Start requirement analysis"}<Sparkles size={15} /></button></div></form>{message && <p className="workspace-message">{message}</p>}</section><section className="workspace-panel accepted-projects-panel"><div className="panel-heading"><div className="composer-icon"><CheckCircle2 size={20} /></div><div><span className="workspace-eyebrow">PREVIOUS PROJECTS</span><h2>Accepted and ready</h2><p>Open a completed negotiation to review the agreement and continue the project chat.</p></div></div>{acceptedProjects.length === 0 ? <p className="history-empty">Accepted projects will appear here after both parties agree.</p> : <div className="accepted-project-list">{acceptedProjects.map((item) => <button className="accepted-project-card" key={item.request_id} onClick={() => navigate(`/contract-workspace/${item.request_id}?role=client`)}><span className="accepted-project-icon"><MessageCircle size={17} /></span><span className="accepted-project-copy"><strong>{item.title || "Untitled project"}</strong><small>{item.status === "BOTH_ACCEPTED" ? "Both parties accepted" : "Negotiation in progress"}</small></span><span className="accepted-project-arrow">Open workspace</span></button>)}</div>}</section><section className="workspace-tip"><Clock3 size={18} /><div><b>Good projects start with context</b><p>Share what you know now. The assistant will help you uncover what is missing.</p></div></section></main></div>;
}

export default Dashboard;
