import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";
import "../styles/agreement.css";

function FreelancerDashboard() {
    const navigate = useNavigate();
    const [agreements, setAgreements] = useState([]);
    const [error, setError] = useState("");
    const freelancerName = JSON.parse(localStorage.getItem("user") || "{}").full_name || "Freelancer";

    useEffect(() => {
        const loadAgreements = async () => {
            try {
                const currentUser = JSON.parse(localStorage.getItem("user") || "{}");
                const response = await api.get(`/freelancers/agreements/freelancer/${encodeURIComponent(currentUser.email)}`);
                setAgreements(response.data.agreements);
            } catch (requestError) {
                setError(requestError.response?.data?.detail || "Unable to load agreements.");
            }
        };
        loadAgreements();
        const refreshTimer = window.setInterval(loadAgreements, 3000);
        return () => window.clearInterval(refreshTimer);
    }, []);

    const approve = async (projectId) => {
        const response = await api.post(`/freelancers/agreements/${projectId}/freelancer-approve`);
        setAgreements((current) => current.map((agreement) => agreement.project_id === projectId ? response.data : agreement));
    };

    const deleteAgreement = async (projectId) => {
        if (!window.confirm("Delete this agreement from the freelancer workspace?")) return;
        await api.delete(`/freelancers/agreements/${projectId}`);
        setAgreements((current) => current.filter((agreement) => agreement.project_id !== projectId));
    };

    const logout = () => {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        navigate("/login");
    };

    const uniqueAgreements = Object.values(agreements.reduce((projects, agreement) => {
        const projectKey = agreement.final_scope || agreement.project_id;
        const existing = projects[projectKey];
        if (!existing || (agreement.project_status === "completed" && existing.project_status !== "completed")) {
            projects[projectKey] = agreement;
        }
        return projects;
    }, {}));
    const ongoing = uniqueAgreements.filter((agreement) => agreement.project_status !== "completed");
    const completed = uniqueAgreements.filter((agreement) => agreement.project_status === "completed");

    const renderAgreement = (agreement) => {
        const bothApproved = agreement.client_approved && agreement.freelancer_approved;
        return <article className="freelancer-agreement" key={agreement.project_id}><div><p className="eyebrow">{bothApproved ? "Completed project" : agreement.client_approved ? "Client approved" : "Awaiting client approval"}</p><h3>{agreement.freelancer_name}</h3><p>{agreement.final_scope}</p><p><b>Budget:</b> ₹{Number(agreement.final_agreed_price).toLocaleString("en-IN")} · <b>Deadline:</b> {agreement.deadline}</p></div><div className="agreement-actions"><button disabled={agreement.freelancer_approved || !agreement.client_approved} onClick={() => approve(agreement.project_id)}>{agreement.freelancer_approved ? "Freelancer Approved" : agreement.client_approved ? "Approve Agreement" : "Waiting for Client Approval"}</button><button disabled={!bothApproved} onClick={() => navigate(`/contract/${agreement.project_id}`)}>Download Contract</button><button className="delete-agreement" onClick={() => deleteAgreement(agreement.project_id)}>Delete</button></div></article>;
    };

    return <main className="agreement-page"><nav className="agreement-nav"><h1>Freelancer Workspace</h1><span className="role-badge">Freelancer</span><button onClick={logout}>Logout</button></nav><header className="agreement-heading"><p className="eyebrow">Freelancer workspace</p><h2>Welcome back, {freelancerName}.</h2><p>Review selected projects, approvals, and contracts.</p></header>{error && <p className="agreement-error">{error}</p>}<section className="history-section"><h3>Ongoing Projects</h3>{ongoing.length ? ongoing.map(renderAgreement) : <p className="agreement-empty">No ongoing projects.</p>}</section><section className="history-section"><h3>Completed Projects</h3>{completed.length ? completed.map(renderAgreement) : <p className="agreement-empty">No completed projects.</p>}</section></main>;
}

export default FreelancerDashboard;
