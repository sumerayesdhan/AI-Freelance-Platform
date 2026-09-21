import { useEffect, useState } from "react";
import { ArrowRight, FilePlus2, LoaderCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";
import ClientSidebar from "../components/ClientSidebar";
import "../styles/dashboard.css";

function ProcessingProjectsPage() {
    const navigate = useNavigate();
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const loadProjects = async () => {
            try {
                const response = await api.get("/projects/history");
                setProjects(response.data.projects || []);
            } catch (requestError) {
                setError(
                    requestError.response?.data?.detail ||
                    "Unable to load your projects."
                );
            } finally {
                setLoading(false);
            }
        };

        loadProjects();
    }, []);

    return (
        <div className="workspace-shell">
            <ClientSidebar />
            <main className="workspace-main">
                <header className="workspace-header">
                    <div>
                        <span className="workspace-eyebrow">PROJECT HISTORY</span>
                        <h1>Projects in progress</h1>
                        <p>Pick up a project and continue shaping its requirements.</p>
                    </div>
                </header>
                <section className="workspace-panel">
                    {loading && (
                        <p className="empty-state">
                            <LoaderCircle size={16} /> Loading projects...
                        </p>
                    )}
                    {!loading && error && <p className="workspace-message">{error}</p>}
                    {!loading && !error && projects.length === 0 && (
                        <div className="empty-state">
                            <p>No projects are processing yet.</p>
                            <button type="button" onClick={() => navigate("/dashboard")}>
                                Create a project <ArrowRight size={15} />
                            </button>
                        </div>
                    )}
                    {!loading && !error && projects.length > 0 && (
                        <div className="project-history">
                            {projects.map((project) => (
                                <button
                                    className="history-item"
                                    key={project.project_id}
                                    type="button"
                                    onClick={() =>
                                        navigate(
                                            `/requirement-assistance/${project.project_id}`
                                        )
                                    }
                                >
                                    <FilePlus2 size={15} />
                                    <span>{project.title}</span>
                                    <ArrowRight size={15} />
                                </button>
                            ))}
                        </div>
                    )}
                </section>
            </main>
        </div>
    );
}

export default ProcessingProjectsPage;
