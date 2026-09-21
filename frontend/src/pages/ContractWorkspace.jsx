import { useEffect, useState } from "react";
import { FilePlus2, LogOut, MessageCircle, Send, X } from "lucide-react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";

import api from "../services/api";
import "../styles/dashboard.css";

function ContractWorkspace() {
    const { requestId } = useParams();
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const role = (searchParams.get("role") || "client").toLowerCase();
    const freelancerId = localStorage.getItem("freelancer_id");
    const [negotiation, setNegotiation] = useState(null);
    const [history, setHistory] = useState([]);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [chatOpen, setChatOpen] = useState(false);
    const [loading, setLoading] = useState(true);
    const [sending, setSending] = useState(false);
    const [error, setError] = useState("");

    const loadWorkspace = async () => {
        try {
            const negotiationResponse = await api.get(`/negotiation/${requestId}`);
            setNegotiation(negotiationResponse.data);

            if (role === "client") {
                const historyResponse = await api.get("/projects/history");
                setHistory(historyResponse.data.projects || []);
            } else if (freelancerId) {
                const dashboardResponse = await api.get(
                    `/freelancer/dashboard/${freelancerId}`
                );
                setHistory(dashboardResponse.data.negotiation_requests || []);
            }

            const chatResponse = await api.get(
                `/conversation/contract/${requestId}`
            );
            setMessages(chatResponse.data.messages || []);
        } catch (requestError) {
            setError(
                requestError.response?.data?.detail ||
                "Unable to load the contract workspace"
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadWorkspace();
        const interval = window.setInterval(loadWorkspace, 5000);
        return () => window.clearInterval(interval);
    }, [requestId, role, freelancerId]);

    const sendMessage = async (event) => {
        event.preventDefault();
        const text = input.trim();
        if (!text || sending) return;

        try {
            setSending(true);
            await api.post(`/conversation/contract/${requestId}`, {
                message: text,
                sender_role: role === "freelancer" ? "FREELANCER" : "CLIENT"
            });
            setInput("");
            await loadWorkspace();
        } catch (requestError) {
            setError(
                requestError.response?.data?.detail ||
                "Unable to send message"
            );
        } finally {
            setSending(false);
        }
    };

    const logout = () => {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        localStorage.removeItem("freelancer_token");
        localStorage.removeItem("freelancer_id");
        navigate(role === "freelancer" ? "/freelancer-login" : "/login");
    };

    if (loading) {
        return <main className="contract-workspace"><p>Loading workspace...</p></main>;
    }

    if (error && !negotiation) {
        return <main className="contract-workspace"><p className="message">{error}</p></main>;
    }

    const result = negotiation?.negotiation_result || {};
    const visibleHistory = role === "client"
        ? history
        : history.filter((item) => item.request_id !== requestId);

    return (
        <main className="contract-workspace">
            <aside className="contract-sidebar">
                <button className="contract-brand" onClick={() => navigate(role === "client" ? "/dashboard" : `/freelancer-dashboard/${freelancerId}`)}>
                    <span className="contract-brand-mark"><MessageCircle size={16} /></span>
                    Briefly<span>.</span>
                </button>
                <div className="contract-sidebar-title">
                    <span>{role === "client" ? "Project history" : "Negotiated projects"}</span>
                    <span>{visibleHistory.length}</span>
                </div>
                <div className="contract-history-list">
                    {visibleHistory.length === 0 && <p>No history yet.</p>}
                    {visibleHistory.map((item) => (
                        <button
                            key={role === "client" ? item.project_id : item.request_id}
                            onClick={() => role === "client"
                                ? navigate(`/requirement-assistance/${item.project_id}`)
                                : navigate(`/negotiation/${item.request_id}?role=freelancer`)
                            }
                        >
                            <FilePlus2 size={15} />
                            <span>{item.title || item.project_id || item.request_id}</span>
                        </button>
                    ))}
                </div>
                <button className="contract-logout" onClick={logout}><LogOut size={15} /> Sign out</button>
            </aside>

            <section className="contract-main">
                <header className="contract-header">
                    <div>
                        <span className="workspace-eyebrow">CONTRACT WORKSPACE</span>
                        <h1>{role === "client" ? "Your project workspace" : "Your client workspace"}</h1>
                        <p>Both parties accepted the negotiated terms.</p>
                    </div>
                    <span className="contract-ready-badge">Contract ready</span>
                </header>

                <section className="contract-summary">
                    <span className="workspace-eyebrow">FINAL AGREEMENT</span>
                    <h2>{negotiation?.project_id || "Negotiated project"}</h2>
                    <div className="contract-metrics">
                        <div><small>Final price</small><strong>${Number(result.final_price || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}</strong></div>
                        <div><small>Timeline</small><strong>{result.final_timeline_days || 0} days</strong></div>
                        <div><small>Status</small><strong>BOTH ACCEPTED</strong></div>
                    </div>
                </section>

                <section className="contract-next-steps">
                    <div>
                        <span className="workspace-eyebrow">NEXT STEPS</span>
                        <h2>Turn the agreement into a delivery plan.</h2>
                        <p>Review the formal contract and the schedule generated from the accepted terms.</p>
                    </div>
                    <div className="contract-next-step-actions">
                        <button onClick={() => navigate(`/contract/${requestId}?role=${role}`)}>
                            View contract
                        </button>
                        <button onClick={() => navigate(`/timeline/${requestId}?role=${role}`)}>
                            View timeline
                        </button>
                    </div>
                </section>

                {error && <p className="workspace-message">{error}</p>}
            </section>

            <button className="contract-chat-launcher" onClick={() => setChatOpen(true)} aria-label="Open project chat">
                <MessageCircle size={23} />
            </button>

            {chatOpen && (
                <section className="contract-chat-panel">
                    <header>
                        <div><strong>Project chat</strong><span>{role === "client" ? "Freelancer" : "Client"}</span></div>
                        <button onClick={() => setChatOpen(false)} aria-label="Close project chat"><X size={18} /></button>
                    </header>
                    <div className="contract-chat-messages">
                        {messages.length === 0 && <p className="contract-chat-empty">Start the conversation about your project.</p>}
                        {messages.map((message, index) => {
                            const own = message.sender_role?.toLowerCase() === role;
                            return <div className={own ? "contract-message own" : "contract-message"} key={`${message.created_at}-${index}`}><small>{message.sender_role}</small><p>{message.message}</p></div>;
                        })}
                    </div>
                    <form onSubmit={sendMessage} className="contract-chat-form">
                        <input value={input} onChange={(event) => setInput(event.target.value)} placeholder="Write a message..." aria-label="Write a message" />
                        <button type="submit" disabled={sending || !input.trim()} aria-label="Send message"><Send size={17} /></button>
                    </form>
                </section>
            )}
        </main>
    );
}

export default ContractWorkspace;
