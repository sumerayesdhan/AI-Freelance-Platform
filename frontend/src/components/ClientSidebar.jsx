import { FilePlus2, LogOut, MessageSquareText, Plus, Search, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";
import "../styles/client-sidebar.css";

function ClientSidebar() {
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);

  useEffect(() => {
    api.get("/projects/history")
      .then((response) => setHistory(response.data.projects || []))
      .catch(() => setHistory([]));
  }, []);

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/login");
  };

  return <aside className="client-sidebar"><button className="sidebar-brand" onClick={() => navigate("/dashboard")}><span className="sidebar-brand-mark"><Sparkles size={15} /></span><span>Briefly<span>.</span></span></button><button className="sidebar-new-project" onClick={() => navigate("/dashboard")}><Plus size={16} /> New project</button><div className="sidebar-search"><Search size={15} /><span>Search projects</span></div><div className="sidebar-history-title"><span>Project history</span><span>{history.length}</span></div><div className="sidebar-history-list">{history.length ? history.map((project) => <button key={project.project_id} onClick={() => navigate(`/requirement-assistance/${project.project_id}`)}><FilePlus2 size={15} /><span>{project.title.split(" ").slice(0, 2).join(" ")}</span></button>) : <p>No projects yet</p>}</div><div className="sidebar-bottom"><button onClick={() => navigate("/")}><MessageSquareText size={15} /> About Briefly</button><button onClick={logout}><LogOut size={15} /> Logout</button></div></aside>;
}

export default ClientSidebar;
