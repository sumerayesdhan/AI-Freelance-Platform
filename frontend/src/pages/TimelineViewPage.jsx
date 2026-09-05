import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { jsPDF } from "jspdf";
import api from "../services/api";
import "../styles/dashboard.css";

function TimelineViewPage() {
  const { requestId } = useParams();
  const navigate = useNavigate();
  const [timelineSummary, setTimelineSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadTimeline = async () => {
      try {
        const response = await api.get(`/negotiation/${requestId}/timeline`);
        setTimelineSummary(response.data);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    loadTimeline();
  }, [requestId]);

  const handleDownloadPdf = () => {
    if (!timelineSummary) return;

    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    const margin = 16;
    let y = 18;

    doc.setFontSize(18);
    doc.setFont("helvetica", "bold");
    doc.text("AI FREELANCE PLATFORM", margin, y);
    y += 12;

    doc.setFontSize(28);
    doc.text("Project Timeline", margin, y);
    y += 10;

    doc.setFontSize(12);
    doc.setFont("helvetica", "normal");
    doc.text(`${timelineSummary.total_days || 0} days`, pageWidth - 40, y, { align: "right" });
    y += 14;
    doc.text(timelineSummary.summary || "", margin, y, { maxWidth: pageWidth - margin * 2 });
    y += 20;

    (timelineSummary.phases || []).forEach((phase) => {
      if (y > 260) {
        doc.addPage();
        y = 18;
      }

      doc.setFillColor(220, 235, 213);
      doc.roundedRect(margin, y, 48, 12, 3, 3, "F");
      doc.setFont("helvetica", "bold");
      doc.setFontSize(11);
      doc.text(`${phase.days || 0} days`, margin + 8, y + 8);
      doc.setFontSize(14);
      doc.text(phase.name || "Phase", margin + 60, y + 8);
      y += 18;

      doc.setFontSize(12);
      doc.setFont("helvetica", "normal");
      doc.text(`${phase.description || ""}`, margin + 60, y, { maxWidth: pageWidth - margin - 80 });
      y += 16;
      doc.text(`Days ${phase.start_day}-${phase.end_day}`, pageWidth - 60, y, { align: "right" });
      y += 18;
    });

    doc.save(`project-timeline-${requestId}.pdf`);
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-card"><h2>Loading timeline...</h2></div>
      </div>
    );
  }

  if (!timelineSummary) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-card">
          <h2>Timeline not available</h2>
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

        <div className="timeline-document" style={{ margin: "20px" }}>
          <div className="timeline-header">
            <h3>Project Timeline</h3>
            <span>{timelineSummary.total_days} days</span>
          </div>
          <p className="timeline-summary">{timelineSummary.summary}</p>
          <div className="timeline-steps">
            {timelineSummary.phases?.map((phase, index) => (
              <div className="timeline-step" key={`${phase.name}-${index}`}>
                <div className="timeline-day-pill">{phase.days} days</div>
                <div className="timeline-content">
                  <div className="timeline-phase-row">
                    <strong>{phase.name}</strong>
                    <span>Days {phase.start_day}-{phase.end_day}</span>
                  </div>
                  <p>{phase.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default TimelineViewPage;
