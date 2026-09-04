import { ArrowRight, Bot, Check, ChevronRight, CircleDollarSign, Gauge, Handshake, Layers3, MessageSquareText, Sparkles, UsersRound } from "lucide-react";
import { useNavigate } from "react-router-dom";

import "../styles/landing.css";

const featureCards = [
  {
    icon: MessageSquareText,
    title: "Clearer project briefs",
    text: "Turn a first idea into structured requirements your team can actually build from."
  },
  {
    icon: Gauge,
    title: "Confident decisions",
    text: "See complexity signals and project context before you commit time or budget."
  },
  {
    icon: Handshake,
    title: "Fairer negotiations",
    text: "Bring clients and freelancers to the same table with context, clarity, and momentum."
  }
];

const steps = [
  ["01", "Shape the brief", "Clients share the idea. Our assistant asks the questions that move it from vague to buildable."],
  ["02", "Find the right fit", "Compare freelancer profiles with the project context, skills, and expectations in view."],
  ["03", "Agree with confidence", "Use AI-assisted negotiation to explore a fair scope, rate, and next step."],
];

const platformFeatures = [
  ["Requirement assistance", "A guided conversation helps clients explain goals, users, constraints, and success criteria before a project reaches a freelancer."],
  ["Project understanding", "Convert the conversation into a readable project summary with domain, platform, target users, and delivery considerations."],
  ["Complexity prediction", "Get an early signal about project complexity so budgets, timelines, and expectations start from a more honest place."],
  ["Freelancer recommendations", "Discover relevant freelancers using project context, skills, experience, and fit instead of a title alone."],
  ["Negotiation workspace", "Keep proposals, questions, scope changes, and suggested next steps together in a focused conversation."],
  ["Shared momentum", "Move from analysis to action with clear project stages, practical summaries, and a visible path forward."],
];

const reasons = [
  ["Clarity before commitment", "Make the important unknowns visible while there is still time to make a good decision."],
  ["Built for both sides", "Clients get confidence and freelancers get context, so the relationship starts with mutual respect."],
  ["Human judgment stays central", "AI organizes the conversation and surfaces options. People still decide what good work means."],
];

function Landing() {
  const navigate = useNavigate();

  return (
    <main className="landing-page">
      <nav className="site-nav landing-nav">
        <button className="brand" onClick={() => navigate("/")} aria-label="Go to home">
          <span className="brand-mark"><Sparkles size={17} /></span>
          <span>Briefly<span className="brand-dot">.</span></span>
        </button>
        <div className="nav-links">
          <a href="#how-it-works">How it works</a>
          <a href="#features">Features</a>
          <button className="nav-login" onClick={() => navigate("/login")}>Log in</button>
          <button className="button button-small" onClick={() => navigate("/register")}>Get started <ArrowRight size={15} /></button>
        </div>
      </nav>

      <section className="hero-section page-width">
        <div className="hero-copy reveal-up">
          <p className="eyebrow"><span className="eyebrow-line" /> AI-powered freelance clarity</p>
          <h1>From first thought to <em>right fit.</em></h1>
          <p className="hero-lede">Briefly helps clients shape better projects and freelancers negotiate better work, with an intelligent layer between the two.</p>
          <div className="hero-actions">
            <button className="button" onClick={() => navigate("/register")}>Start a project <ArrowRight size={17} /></button>
            <button className="button button-ghost" onClick={() => navigate("/login")}>I already have an account</button>
          </div>
          <div className="hero-proof"><span className="proof-avatars"><i>J</i><i>M</i><i>A</i></span><span>Built for thoughtful teams and independent talent</span></div>
        </div>

        <div className="hero-visual reveal-up delay-1" aria-label="AI negotiation workspace preview">
          <div className="visual-glow" />
          <div className="workspace-window">
            <div className="window-top"><span className="window-dots"><i /><i /><i /></span><span className="window-label">project / mobile marketplace</span><span className="live-pill"><span /> live brief</span></div>
            <div className="workspace-content">
              <div className="workspace-side"><span className="side-active"><Layers3 size={15} /> Brief</span><span><UsersRound size={15} /> Matches</span><span><Handshake size={15} /> Deal room</span></div>
              <div className="workspace-main">
                <div className="workspace-heading"><div><span className="muted-label">AI PROJECT READOUT</span><h3>Marketplace for local makers</h3></div><span className="score">8.7 <small>/ 10</small></span></div>
                <div className="signal-row"><div><span>Scope clarity</span><strong>Strong</strong></div><div><span>Build shape</span><strong>Medium</strong></div><div><span>Talent fit</span><strong>94%</strong></div></div>
                <div className="chat-preview"><div className="ai-avatar"><Bot size={15} /></div><div><b>Briefly AI</b><p>“A great match should be able to own the product flow, not only the interface.”</p></div></div>
                <div className="match-row"><div className="person-avatar">N</div><div><b>Nia Okafor</b><span>Product designer · 6 years</span></div><span className="match-score">94% fit <ChevronRight size={15} /></span></div>
              </div>
            </div>
          </div>
          <div className="floating-note note-top"><Sparkles size={14} /><span>Context-aware suggestions</span></div>
          <div className="floating-note note-bottom"><CircleDollarSign size={15} /><span>Range aligned</span><b>$65–80/hr</b></div>
        </div>
      </section>

      <section className="logo-strip page-width"><span>THE WORKFLOW LAYER FOR</span><b>CLIENTS</b><b>CREATIVE TEAMS</b><b>INDEPENDENT TALENT</b><b>PRODUCT BUILDERS</b></section>

      <section className="intro-section page-width" id="how-it-works">
        <div className="section-kicker">01 / A better starting point</div>
        <div className="split-heading"><h2>Good work starts with a brief that respects <em>the work.</em></h2><p>Briefly is a calmer way to move from “we have an idea” to “we know what happens next.” One space for the thinking, people, and conversations that make freelance work click.</p></div>
        <div className="steps-grid">{steps.map(([number, title, text]) => <article className="step-item" key={number}><span className="step-number">{number}</span><h3>{title}</h3><p>{text}</p></article>)}</div>
      </section>

      <section className="feature-band" id="features"><div className="page-width"><div className="section-kicker">02 / The useful intelligence</div><div className="feature-heading"><h2>Less guesswork.<br /><em>More good work.</em></h2><p>Every feature is designed to make the next decision more informed, not more complicated.</p></div><div className="feature-grid">{featureCards.map(({ icon: Icon, title, text }) => <article className="feature-card" key={title}><span className="feature-icon"><Icon size={20} /></span><h3>{title}</h3><p>{text}</p><span className="card-arrow"><ArrowRight size={16} /></span></article>)}</div></div></section>

      <section className="about-section page-width"><div className="section-kicker">02.5 / About the platform</div><div className="about-heading"><h2>The thinking space between <em>an idea and its outcome.</em></h2><p>Briefly exists because freelance projects rarely fail for lack of talent. They lose momentum when the brief is unclear, the fit is guessed, or the negotiation happens without enough shared context.</p></div><div className="about-columns"><p>Our platform helps clients understand what they need, helps freelancers understand what they are being asked to build, and gives both sides a practical way to talk through the work.</p><p>From the first project description to the final agreement, every step is designed to reduce avoidable surprises while keeping the process personal, flexible, and useful.</p></div></section>

      <section className="details-section"><div className="page-width"><div className="section-kicker">02.7 / Everything in one flow</div><div className="details-heading"><h2>Tools for the moments<br /><em>that shape the work.</em></h2><p>Use the platform as a complete journey or bring it into the moment where you need more clarity.</p></div><div className="details-grid">{platformFeatures.map(([title, text], index) => <article className="detail-item" key={title}><span>{String(index + 1).padStart(2, "0")}</span><div><h3>{title}</h3><p>{text}</p></div></article>)}</div></div></section>

      <section className="audience-section page-width"><div className="audience-card audience-client"><span className="audience-tag">FOR CLIENTS</span><h2>Bring the idea.<br /><em>Leave with a plan.</em></h2><ul><li><Check size={16} /> Turn ambiguity into a useful project brief</li><li><Check size={16} /> Understand complexity before you invest</li><li><Check size={16} /> Meet talent with the right context</li></ul><button className="text-link" onClick={() => navigate("/register")}>Start as a client <ArrowRight size={16} /></button></div><div className="audience-card audience-freelancer"><span className="audience-tag">FOR FREELANCERS</span><h2>Protect your craft.<br /><em>Choose better work.</em></h2><ul><li><Check size={16} /> See the shape of a project before saying yes</li><li><Check size={16} /> Make your value visible in the conversation</li><li><Check size={16} /> Negotiate from shared expectations</li></ul><button className="text-link" onClick={() => navigate("/register")}>Join as a freelancer <ArrowRight size={16} /></button></div></section>

      <section className="negotiation-section page-width"><div className="negotiation-copy"><div className="section-kicker">03 / A more human negotiation</div><h2>AI that helps both sides <em>hear the same thing.</em></h2><p>Negotiation is not a tug of war. Briefly brings the project scope, priorities, rates, and constraints into one shared view so a good agreement can happen sooner.</p><div className="negotiation-points"><span><Bot size={18} /> Reads the context</span><span><Handshake size={18} /> Surfaces fair options</span><span><MessageSquareText size={18} /> Keeps the human in charge</span></div></div><div className="deal-card"><div className="deal-header"><span>DEAL ROOM / ACTIVE</span><span className="deal-status">● aligned</span></div><div className="deal-message client-message"><span className="mini-avatar">C</span><p>Could we begin with a two-week discovery sprint?</p></div><div className="deal-message ai-message"><span className="mini-avatar ai-mini"><Bot size={13} /></span><p>That keeps the first milestone focused and gives both sides a clear check-in point.</p></div><div className="deal-footer"><span>Suggested next step</span><b>Discovery sprint · $1,200–1,500</b></div></div></section>

      <section className="reasons-section page-width"><div className="section-kicker">04 / Why choose Briefly</div><div className="reasons-heading"><h2>Better decisions are a <em>shared advantage.</em></h2><p>A good platform should make the work feel more considered, not more complicated.</p></div><div className="reasons-grid">{reasons.map(([title, text]) => <article key={title}><span className="reason-check"><Check size={15} /></span><h3>{title}</h3><p>{text}</p></article>)}</div></section>

      <section className="cta-section page-width"><div className="cta-inner"><Sparkles size={23} /><h2>Make the next project<br /><em>the right one.</em></h2><p>Start with a better brief. Find a better fit. Work with more clarity.</p><button className="button button-light" onClick={() => navigate("/register")}>Create your free account <ArrowRight size={17} /></button></div></section>

      <footer className="site-footer page-width"><button className="brand" onClick={() => navigate("/")}><span className="brand-mark"><Sparkles size={17} /></span><span>Briefly<span className="brand-dot">.</span></span></button><span>Thoughtful tools for better freelance work.</span><span>© 2026 Briefly</span></footer>
    </main>
  );
}

export default Landing;
