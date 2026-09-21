import { ArrowLeft, Download, FileText } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";

import api from "../services/api";
import "../styles/dashboard.css";

function ContractGenerationPage() {
    const { requestId } = useParams();
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const role = searchParams.get("role") || "client";
    const [contract, setContract] = useState(null);
    const [error, setError] = useState("");

    useEffect(() => {
        api.get(`/contract/${requestId}`)
            .then((response) => setContract(response.data))
            .catch((requestError) => setError(
                requestError.response?.data?.detail || "Contract not generated"
            ));
    }, [requestId]);

    if (error) {
        return <main className="generated-page"><p className="message">{error}</p></main>;
    }

    if (!contract) {
        return <main className="generated-page"><p>Generating contract...</p></main>;
    }

    const deliverables = Array.isArray(contract.project.deliverables)
        ? contract.project.deliverables
        : [contract.project.deliverables];
    const responsibilities = contract.terms.responsibilities || {};
    const agreementDate = contract.agreement_date
        ? new Date(contract.agreement_date).toLocaleDateString()
        : "Not available";

    return (
        <main className="generated-page">
            <header className="generated-page-header">
                <button
                    className="generated-back-button"
                    onClick={() => navigate(`/contract-workspace/${requestId}?role=${role}`)}
                >
                    <ArrowLeft size={17} /> Back to workspace
                </button>
                <div className="generated-page-actions">
                    <button className="generated-secondary-button" onClick={() => window.print()}>
                        <Download size={16} /> Download / Print
                    </button>
                    <button
                        className="generated-primary-button"
                        onClick={() => navigate(`/timeline/${requestId}?role=${role}`)}
                    >
                        View project timeline
                    </button>
                </div>
            </header>

            <article className="generated-document contract-document">
                <div className="generated-document-heading">
                    <span className="generated-icon"><FileText size={22} /></span>
                    <div>
                        <span className="workspace-eyebrow">FORMAL AGREEMENT</span>
                        <h1>Freelance Project Contract</h1>
                        <p>Generated from the final terms accepted by both parties.</p>
                    </div>
                    <span className="contract-ready-badge">CONTRACT READY</span>
                </div>

                <section className="generated-section generated-party-grid">
                    <div><span>Client</span><strong>{contract.client.name}</strong><p>{contract.client.email}</p></div>
                    <div><span>Freelancer</span><strong>{contract.freelancer.name}</strong><p>{contract.freelancer.title || contract.freelancer.email}</p></div>
                </section>

                <section className="generated-section">
                    <span className="generated-label">PROJECT</span>
                    <h2 className="contract-project-title">{contract.project.title}</h2>
                    <p className="contract-project-description">{contract.project.description}</p>
                    <div className="contract-deliverables">
                        <span className="generated-label">AGREED DELIVERABLES</span>
                        <ul>
                            {deliverables.filter(Boolean).map((item, index) => <li key={`${item}-${index}`}>{item}</li>)}
                        </ul>
                    </div>
                </section>

                <section className="generated-section contract-overview-grid">
                    <div><span>Final negotiated price</span><strong>${Number(contract.terms.final_price || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}</strong></div>
                    <div><span>Final timeline</span><strong>{contract.terms.final_timeline_days || 0} days</strong></div>
                    <div><span>Agreement date</span><strong>{agreementDate}</strong></div>
                </section>

                <section className="generated-section generated-terms-grid">
                    <div><span>Payment terms</span><p>{contract.terms.payment_terms}</p></div>
                    <div><span>Responsibilities</span><p><strong>Client:</strong> {responsibilities.client}</p><p><strong>Freelancer:</strong> {responsibilities.freelancer}</p></div>
                </section>
            </article>
        </main>
    );
}

export default ContractGenerationPage;
