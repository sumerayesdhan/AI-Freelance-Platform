import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import api from "../services/api";
import ClientHeader from "../components/ClientHeader";
import ClientSidebar from "../components/ClientSidebar";
import "../styles/summary.css";

function RequirementSummaryPage() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [requirement, setRequirement] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        const response = await api.get(`/conversation/analysis/${projectId}`);
        setRequirement(response.data.requirement_analysis);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalysis();
  }, [projectId]);

  if (loading) return <main className="summary-container"><ClientHeader /><h2 className="loading">Generating Requirement Analysis...</h2></main>;
  if (!requirement) return <main className="summary-container"><ClientHeader /><h2 className="loading">No requirement data found</h2></main>;

  return <main className="summary-container"><ClientSidebar /><ClientHeader /><div className="summary-title-row"><h1>Final Requirement Analysis</h1><div className="summary-title-actions"><button onClick={() => navigate(`/project/${projectId}/analysis`)}>Complexity Prediction</button><button onClick={() => navigate(`/freelancers/${projectId}`)}>Find Freelancers</button></div></div><div className="summary-card"><SummaryField title="Domain"><p>{requirement.project_domain}</p></SummaryField><SummaryField title="Project Type"><p>{requirement.project_type}</p></SummaryField><SummaryField title="Platform"><p>{requirement.platform}</p></SummaryField><SummaryField title="Target Users"><List items={requirement.target_users} /></SummaryField><SummaryField title="Features"><List items={requirement.features} /></SummaryField><SummaryField title="Technology Preference"><p>{requirement.technology_preference || "AI Recommended"}</p></SummaryField></div></main>;
}

function SummaryField({ title, children }) { return <section className="summary-item"><h3>{title}</h3>{children}</section>; }
function List({ items = [] }) { return <ul>{items.map((item, index) => <li key={`${item}-${index}`}>{item}</li>)}</ul>; }

export default RequirementSummaryPage;
