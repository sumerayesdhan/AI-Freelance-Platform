import { useEffect, useState } from "react";
import { ArrowLeft, CalendarDays } from "lucide-react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";

import api from "../services/api";
import "../styles/dashboard.css";


function TimelineGenerationPage() {
    const { requestId } = useParams();
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const role = searchParams.get("role") || "client";
    const [timeline, setTimeline] = useState(null);
    const [error, setError] = useState("");
    const [actionMessage, setActionMessage] = useState("");
    const [actionLoading, setActionLoading] = useState(false);

    useEffect(() => {
        api.get(`/contract/timeline/${requestId}`)
            .then((response) => setTimeline(response.data))
            .catch((requestError) => setError(
                requestError.response?.data?.detail || "Unable to load project timeline"
            ));
    }, [requestId]);

    const updatePhaseStatus = async (endpoint, phaseNumber) => {
        try {
            setActionLoading(true);
            setActionMessage("");
            const response = await api.post(
                `/contract/${endpoint}/${requestId}/${phaseNumber}`
            );
            setActionMessage(response.data.message);
            const refreshed = await api.get(`/contract/timeline/${requestId}`);
            setTimeline(refreshed.data);
        } catch (requestError) {
            setActionMessage(
                requestError.response?.data?.detail || "Unable to update project status"
            );
        } finally {
            setActionLoading(false);
        }
    };

    if (error) {
        return <main className="generated-page"><p className="message">{error}</p></main>;
    }

    if (!timeline) {
        return <main className="generated-page"><p>Generating project timeline...</p></main>;
    }

    return (
        <main className="generated-page">
            <header className="generated-page-header">
                <button className="generated-back-button" onClick={() => navigate(`/contract/${requestId}?role=${role}`)}>
                    <ArrowLeft size={17} /> Back to contract
                </button>
                <span className="contract-ready-badge">TIMELINE GENERATED</span>
            </header>

            <article className="generated-document timeline-document">
                <div className="generated-document-heading">
                    <span className="generated-icon"><CalendarDays size={22} /></span>
                    <div>
                        <span className="workspace-eyebrow">PROJECT SCHEDULE</span>
                        <h1>{timeline.project_title}</h1>
                        <p>Structured phases and milestones based on the accepted project duration.</p>
                    </div>
                </div>

                <section className="generated-section timeline-overview">
                    <div><span>Start date</span><strong>{new Date(timeline.start_date).toLocaleDateString()}</strong></div>
                    <div><span>Negotiated duration</span><strong>{timeline.final_duration_days} days</strong></div>
                    <div><span>Status</span><strong>{timeline.status}</strong></div>
                    <div><span>Overall progress</span><strong>{timeline.overall_progress}%</strong></div>
                </section>

                <section className="generated-section payment-breakdown-section">
                    <div className="generated-section-heading">
                        <span className="generated-label">NEGOTIATED PRICE BREAKDOWN</span>
                        <h2>Payment milestones</h2>
                    </div>
                    <div className="payment-breakdown-grid">
                        {timeline.payment_breakdown.map((payment) => (
                            <div className="payment-breakdown-card" key={payment.label}>
                                <span>{payment.label}</span>
                                <strong>${Number(payment.amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}</strong>
                                <small>{payment.percentage}% of final price</small>
                            </div>
                        ))}
                    </div>
                </section>

                <section className="timeline-phase-list">
                    {timeline.phases.map((phase) => (
                        <article className="timeline-phase" key={phase.phase}>
                            <div className="timeline-phase-number">{phase.phase}</div>
                            <div className="timeline-phase-content">
                                <div className="timeline-phase-heading">
                                    <div><span className="generated-label">Phase {phase.phase}</span><h2>{phase.name}</h2></div>
                                    <span>{phase.start_date} to {phase.end_date}</span>
                                </div>
                                <div className="timeline-phase-details">
                                    <div><strong>Tasks</strong><ul>{phase.tasks.map((task, index) => <li key={`${task}-${index}`}>{task}</li>)}</ul></div>
                                    <div><strong>Milestone</strong><p>{phase.milestone}</p><strong>Dependency</strong><p>{phase.dependency || "None"}</p></div>
                                </div>
                                <div className="timeline-phase-payment">
                                    <div>
                                        <span className="generated-label">PHASE PAYMENT</span>
                                        <strong>
                                            ${Number(phase.payment?.amount || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                                        </strong>
                                        <small>{phase.payment?.percentage}% of negotiated price</small>
                                    </div>
                                    <div className="timeline-phase-status">
                                        <span>{phase.phase_status}</span>
                                        {role === "freelancer" && phase.payment_request_status !== "REQUESTED" && phase.phase_status !== "COMPLETED" && (
                                            <button disabled={actionLoading} onClick={() => updatePhaseStatus("phase-payment-request", phase.phase)}>
                                                {actionLoading ? "Sending..." : "Request phase payment"}
                                            </button>
                                        )}
                                        {role === "client" && phase.phase_status !== "COMPLETED" && (
                                            <button disabled={actionLoading} onClick={() => updatePhaseStatus("phase-complete", phase.phase)}>
                                                {actionLoading ? "Updating..." : "Mark phase completed"}
                                            </button>
                                        )}
                                        {role === "client" && phase.payment_request_status === "REQUESTED" && (
                                            <p className="timeline-notification">{phase.notification?.message || "Payment requested for this phase."}</p>
                                        )}
                                        {actionMessage && <p className="workspace-message">{actionMessage}</p>}
                                    </div>
                                </div>
                            </div>
                        </article>
                    ))}
                </section>
            </article>
        </main>
    );
}

export default TimelineGenerationPage;
