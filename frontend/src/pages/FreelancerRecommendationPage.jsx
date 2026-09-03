import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import api from "../services/api";
import "../styles/freelancer.css";

function FreelancerRecommendationPage() {
    const { projectId } = useParams();
    const navigate = useNavigate();
    const [freelancers, setFreelancers] = useState([]);
    const [selectedFreelancer, setSelectedFreelancer] = useState(null);

    useEffect(() => {
        const loadFreelancers = async () => {
            try {
                const response = await api.get(`/freelancers/recommend/${projectId}`);
                setFreelancers(response.data.recommendations);
            } catch (error) {
                console.log(error);
            }
        };
        loadFreelancers();
    }, [projectId]);

    const startNegotiation = () => {
        navigate(`/negotiation/${projectId}`, {
            state: { freelancer: selectedFreelancer }
        });
    };

    return (
        <div className="recommend-container">
            <h1>Top Freelancer Recommendations</h1>
            {freelancers.map((person) => {
                const isSelected = selectedFreelancer?.freelancer_id === person.freelancer_id;
                return (
                    <div
                        className={isSelected ? "freelancer-card selected" : "freelancer-card"}
                        key={person.freelancer_id}
                        onClick={() => setSelectedFreelancer(person)}
                    >
                        <h2>#{person.rank} {person.freelancer_name}</h2>
                        <p className="title">{person.title}</p>
                        <div className="details">
                            <p>⭐ Match Probability: <b>{(person.recommendation_probability * 100).toFixed(2)}%</b></p>
                            <p>🏆 Job Success: <b>{person.job_success}</b></p>
                            <p>💰 Hourly Rate: <b>${person.hourly_rate}</b></p>
                        </div>
                        <button
                            type="button"
                            className="select-freelancer-btn"
                            onClick={(event) => {
                                event.stopPropagation();
                                setSelectedFreelancer(person);
                            }}
                        >
                            {isSelected ? "Selected" : "Select Freelancer"}
                        </button>
                    </div>
                );
            })}
            <button
                className="start-negotiation-btn"
                onClick={startNegotiation}
                disabled={!selectedFreelancer}
            >
                {selectedFreelancer
                    ? `Start AI Negotiation with ${selectedFreelancer.freelancer_name}`
                    : "Select a freelancer to negotiate"}
            </button>
        </div>
    );
}

export default FreelancerRecommendationPage;
