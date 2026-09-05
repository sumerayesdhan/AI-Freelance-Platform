import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { jsPDF } from "jspdf";
import api from "../services/api";
import "../styles/dashboard.css";

function ContractViewPage() {
  const { requestId } = useParams();
  const navigate = useNavigate();
  const [contractSummary, setContractSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadContract = async () => {
      try {
        const response = await api.get(`/negotiation/${requestId}/contract`);
        setContractSummary(response.data);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    loadContract();
  }, [requestId]);

  const handleDownloadPdf = () => {
    if (!contractSummary) return;

    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    const margin = 16;
    let y = 18;

    doc.setFontSize(18);
    doc.setFont("helvetica", "bold");
    doc.text("AI FREELANCE PLATFORM", margin, y);
    y += 12;

    doc.setFontSize(28);
    doc.text("Project Contract", margin, y);
    y += 14;

    doc.setFontSize(12);
    doc.setFont("helvetica", "normal");
    doc.text(`Project reference: ${contractSummary.project_reference || "N/A"}`, margin, y);
    y += 16;

    doc.setLineWidth(0.5);
    doc.line(margin, y, pageWidth - margin, y);
    y += 18;

    doc.setFont("helvetica", "bold");
    doc.setFontSize(16);
    doc.text("PARTIES", margin, y);
    y += 10;

    doc.setFont("helvetica", "normal");
    doc.setFontSize(12);
    doc.text(`Client and ${contractSummary.parties?.freelancer || "Freelancer"}.`, margin, y);
    y += 26;

    doc.setFont("helvetica", "bold");
    doc.setFontSize(16);
    doc.text("STORED FREELANCER DETAILS", margin, y);
    y += 12;

    const detailRows = [
      ["Name", contractSummary.freelancer_profile?.name || "N/A"],
      ["Title", contractSummary.freelancer_profile?.title || "N/A"],
      ["Email", contractSummary.freelancer_profile?.email || "N/A"],
      ["Country", contractSummary.freelancer_profile?.country || "N/A"],
      ["Hourly rate", contractSummary.freelancer_profile?.hourly_rate ? `$${Number(contractSummary.freelancer_profile.hourly_rate).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : "N/A"],
      ["Skills", Array.isArray(contractSummary.freelancer_profile?.skills) ? contractSummary.freelancer_profile.skills.join(", ") : "N/A"],
    ];

    doc.setFont("helvetica", "normal");
    detailRows.forEach(([label, value]) => {
      doc.text(label, margin, y);
      doc.text(String(value), pageWidth / 2 + 6, y, { maxWidth: pageWidth / 2 - 18 });
      y += 10;
    });
    y += 8;

    doc.setFont("helvetica", "bold");
    doc.setFontSize(16);
    doc.text("AGREED TERMS", margin, y);
    y += 14;

    const terms = [
      ["Project scope", contractSummary.scope || "N/A"],
      ["Fixed project price", `$${Number(contractSummary.fixed_price || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`],
      ["Estimated hours", `${contractSummary.estimated_hours || 0} hours`],
      ["Deadline", `${contractSummary.timeline_days || 0} days`],
    ];

    doc.setFont("helvetica", "normal");
    doc.setFontSize(12);
    terms.forEach(([label, value]) => {
      doc.text(label, margin, y);
      doc.text(String(value), pageWidth / 2 + 6, y, { maxWidth: pageWidth / 2 - 18 });
      y += 10;
    });
    y += 10;

    doc.setFont("helvetica", "bold");
    doc.setFontSize(16);
    doc.text("APPROVALS", margin, y);
    y += 12;

    doc.setFont("helvetica", "normal");
    doc.setFontSize(12);
    doc.text(`Client: ${contractSummary.approvals?.client || "Approved"} · Freelancer: ${contractSummary.approvals?.freelancer || "Approved"}`, margin, y);
    y += 12;
    doc.text(contractSummary.note || "", margin, y, { maxWidth: pageWidth - margin * 2 });

    doc.save(`${contractSummary.download_filename || "project-contract"}.pdf`);
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-card"><h2>Loading contract...</h2></div>
      </div>
    );
  }

  if (!contractSummary) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-card">
          <h2>Contract not available</h2>
          <button onClick={() => navigate(-1)}>Back</button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-card" style={{ padding: 0 }}>
        <div style={{ display: "flex", justifyContent: "flex-end", padding: "20px 20px 0" }}>
          <button type="button" onClick={handleDownloadPdf} className="download-btn">Download as PDF</button>
        </div>

        <div className="contract-document" style={{ margin: "20px" }}>
          <div className="contract-brand">AI FREELANCE PLATFORM</div>
          <h1 className="contract-title">Project Contract</h1>
          <div className="contract-reference">Project reference: {contractSummary.project_reference}</div>
          <div className="contract-divider" />

          <div className="contract-section">
            <h3>PARTIES</h3>
            <p>Client and <strong>{contractSummary.parties?.freelancer}</strong>.</p>
          </div>

          <div className="contract-section">
            <h3>STORED FREELANCER DETAILS</h3>
            <div className="contract-row"><span className="contract-label">Name</span><span className="contract-value">{contractSummary.freelancer_profile?.name || "N/A"}</span></div>
            <div className="contract-row"><span className="contract-label">Title</span><span className="contract-value">{contractSummary.freelancer_profile?.title || "N/A"}</span></div>
            <div className="contract-row"><span className="contract-label">Email</span><span className="contract-value">{contractSummary.freelancer_profile?.email || "N/A"}</span></div>
            <div className="contract-row"><span className="contract-label">Country</span><span className="contract-value">{contractSummary.freelancer_profile?.country || "N/A"}</span></div>
            <div className="contract-row"><span className="contract-label">Hourly rate</span><span className="contract-value">${Number(contractSummary.freelancer_profile?.hourly_rate || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span></div>
            <div className="contract-row"><span className="contract-label">Skills</span><span className="contract-value">{Array.isArray(contractSummary.freelancer_profile?.skills) ? contractSummary.freelancer_profile.skills.join(", ") : "N/A"}</span></div>
          </div>

          <div className="contract-section">
            <h3>AGREED TERMS</h3>
            <div className="contract-row"><span className="contract-label">Project scope</span><span className="contract-value">{contractSummary.scope || "N/A"}</span></div>
            <div className="contract-row"><span className="contract-label">Fixed project price</span><span className="contract-value">${Number(contractSummary.fixed_price || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span></div>
            <div className="contract-row"><span className="contract-label">Estimated hours</span><span className="contract-value">{contractSummary.estimated_hours || 0} hours</span></div>
            <div className="contract-row"><span className="contract-label">Deadline</span><span className="contract-value">{contractSummary.timeline_days || 0} days</span></div>
          </div>

          <div className="contract-section approvals-block">
            <h3>APPROVALS</h3>
            <p>Client: <strong>{contractSummary.approvals?.client}</strong> · Freelancer: <strong>{contractSummary.approvals?.freelancer}</strong></p>
            <p className="approval-note">{contractSummary.note}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ContractViewPage;
