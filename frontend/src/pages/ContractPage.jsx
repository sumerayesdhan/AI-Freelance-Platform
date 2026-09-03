import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import api from "../services/api";
import "../styles/agreement.css";

function ContractPage() {
    const { projectId } = useParams();
    const [agreement, setAgreement] = useState(null);
    const [error, setError] = useState("");

    useEffect(() => {
        api.get(`/freelancers/agreements/${projectId}`).then((response) => setAgreement(response.data)).catch(() => setError("Contract is not available yet."));
    }, [projectId]);

    if (error) return <main className="contract-page"><p>{error}</p></main>;
    if (!agreement) return <main className="contract-page"><p>Preparing contract...</p></main>;

    return <main className="contract-page"><article className="contract-document"><p className="eyebrow">AI Freelance Platform</p><h1>Project Contract</h1><p className="contract-id">Project reference: {agreement.project_id}</p><hr /><h2>Parties</h2><p>Client and <b>{agreement.freelancer_name}</b></p><h2>Agreed terms</h2><dl><div><dt>Project scope</dt><dd>{agreement.final_scope}</dd></div><div><dt>Fixed project price</dt><dd>₹{Number(agreement.final_agreed_price).toLocaleString("en-IN")}</dd></div><div><dt>Estimated hours</dt><dd>{agreement.estimated_hours} hours</dd></div><div><dt>Deadline</dt><dd>{agreement.deadline}</dd></div></dl><h2>Approvals</h2><p>Client: {agreement.client_approved ? "Approved" : "Pending"} · Freelancer: {agreement.freelancer_approved ? "Approved" : "Pending"}</p><p className="contract-note">This contract reflects the negotiated scope and fixed project price.</p></article><button className="print-contract" onClick={() => window.print()}>Download Contract as PDF</button></main>;
}

export default ContractPage;
