import { ArrowRight, BriefcaseBusiness, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";
import "../styles/dashboard.css";

function ClientStartPage() {
    const navigate = useNavigate();
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get("/contract/client-projects")
            .then((response) => setProjects(
                (response.data || []).filter(
                    (project) => project.status === "BOTH_ACCEPTED"
                )
            ))
            .finally(() => setLoading(false));
    }, []);

            const ongoingProject = projects[0];

    return (
        <main className="workspace-main client-start-main">
            <section className="workspace-panel">
                <div className="panel-heading">
                    <div className="composer-icon">
                        <Sparkles size={20} />
                    </div>
                    <div>
                        <span className="workspace-eyebrow">CLIENT WORKSPACE</span>
                        <h1>Start a new project</h1>
                        <p>Share your idea and let Briefly help turn it into a clear project brief.</p>
                    </div>
                </div>
                <button
                    className="composer-footer button"
                    type="button"
                    onClick={() => navigate("/dashboard")}
                >
                    Continue to project workspace
                    <ArrowRight size={16} />
                </button>
            </section>

            <section className="workspace-panel ongoing-project-panel">
                <div className="panel-heading">
                    <div className="composer-icon">
                        <BriefcaseBusiness size={20} />
                    </div>
                    <div>
                        <span className="workspace-eyebrow">ONGOING PROJECT</span>
                        <h2>Continue an accepted project</h2>
                        <p>Return directly to the workspace for your negotiated project and chat.</p>
                    </div>
                </div>
                <button
                    className="composer-footer button"
                    type="button"
                    disabled={loading || !ongoingProject}
                    onClick={() => navigate(`/contract-workspace/${ongoingProject.request_id}?role=client`)}
                >
                    Proceed to ongoing project
                    <ArrowRight size={16} />
                </button>
            </section>

        </main>
    );
}

export default ClientStartPage;
