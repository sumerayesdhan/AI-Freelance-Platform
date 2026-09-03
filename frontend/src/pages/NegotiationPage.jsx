import { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";

import api from "../services/api";
import "../styles/negotiation.css";

function NegotiationPage() {
	const { projectId } = useParams();
	const { state } = useLocation();
	const [negotiation, setNegotiation] = useState(null);
	const [visibleMessages, setVisibleMessages] = useState([]);
	const [typingMessage, setTypingMessage] = useState("");
	const [error, setError] = useState("");

	useEffect(() => {
		const startNegotiation = async () => {
			try {
				const freelancer = state?.freelancer;
				if (!freelancer) {
					throw new Error("No recommended freelancer was selected.");
				}
				const response = await api.post(
					`/freelancers/negotiate/${projectId}`,
					{ freelancer }
				);
				setNegotiation(response.data);
			} catch (requestError) {
				setError(requestError.message || "Unable to start negotiation.");
			}
		};

		startNegotiation();
	}, [projectId, state]);

	useEffect(() => {
		if (!negotiation?.messages?.length) {
			return undefined;
		}

		let cancelled = false;
		let messageIndex = 0;
		let characterIndex = 0;
		let timer;

		const typeNextMessage = () => {
			if (cancelled || messageIndex >= negotiation.messages.length) {
				return;
			}

			const message = negotiation.messages[messageIndex];
			if (characterIndex < message.content.length) {
				characterIndex += 1;
				setTypingMessage(message.content.slice(0, characterIndex));
				timer = window.setTimeout(typeNextMessage, 18);
				return;
			}

			setVisibleMessages((current) => [...current, message]);
			setTypingMessage("");
			messageIndex += 1;
			characterIndex = 0;
			timer = window.setTimeout(typeNextMessage, 450);
		};

		typeNextMessage();
		return () => {
			cancelled = true;
			window.clearTimeout(timer);
		};
	}, [negotiation]);

	if (error) {
		return <main className="negotiation-page"><p className="negotiation-error">{error}</p></main>;
	}

	if (!negotiation) {
		return <main className="negotiation-page"><p className="negotiation-loading">Starting AI negotiation...</p></main>;
	}

	return (
		<main className="negotiation-page">
			<header className="negotiation-header">
				<p className="eyebrow">AI-assisted agreement</p>
				<h1>Negotiation in progress</h1>
				<p>{negotiation.freelancer_name} and the client aligned on scope, effort, and a fair fixed price.</p>
			</header>

			<section className="negotiation-layout">
				<div className="transcript" aria-label="Negotiation transcript">
					{visibleMessages.map((message, index) => (
						<article className={`negotiation-message ${message.speaker.toLowerCase()}`} key={`${message.speaker}-${index}`}>
							<div className="message-meta">{message.speaker}<span>0{index + 1}</span></div>
							<p>{message.content}</p>
						</article>
					))}
					{typingMessage && (
						<article className={`negotiation-message ${negotiation.messages[visibleMessages.length].speaker.toLowerCase()} typing-message`}>
							<div className="message-meta">{negotiation.messages[visibleMessages.length].speaker}<span>typing</span></div>
							<p>{typingMessage}<span className="typing-cursor" aria-hidden="true">|</span></p>
						</article>
					)}
				</div>

				<aside className="agreement-panel">
					<p className="eyebrow">Agreement reached</p>
					<h2>₹{Number(negotiation.final_agreed_price).toLocaleString("en-IN")}</h2>
					<dl>
						<div><dt>Estimated hours</dt><dd>{negotiation.estimated_hours} hours</dd></div>
						<div><dt>Hourly rate</dt><dd>₹{Number(negotiation.freelancer_hourly_rate).toLocaleString("en-IN")}/hour</dd></div>
						<div><dt>Deadline</dt><dd>{negotiation.deadline}</dd></div>
					</dl>
					<div className="scope-block">
						<dt>Final scope</dt>
						<p>{negotiation.final_scope}</p>
					</div>
					<strong className="status">{negotiation.status}</strong>
				</aside>
			</section>
		</main>
	);
}

export default NegotiationPage;
