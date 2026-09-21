import {
    useEffect,
    useState
} from "react";

import {
    useNavigate,
    useParams
} from "react-router-dom";

import api from "../services/api";

import "../styles/dashboard.css";


function FreelancerDashboard() {

    const navigate = useNavigate();

    const { freelancerId } = useParams();


    const [
        freelancer,
        setFreelancer
    ] = useState(null);


    const [
        requests,
        setRequests
    ] = useState([]);


    const [
        loading,
        setLoading
    ] = useState(true);


    const [
        message,
        setMessage
    ] = useState("");


    const [
        selectedProject,
        setSelectedProject
    ] = useState(null);


    const [
        projectLoading,
        setProjectLoading
    ] = useState(false);


    const [
        projectMessage,
        setProjectMessage
    ] = useState("");


    // ========================================================
    // FETCH FREELANCER DASHBOARD
    // ========================================================

    useEffect(() => {

        const fetchDashboard = async () => {

            try {

                setLoading(true);

                setMessage("");


                const response =
                    await api.get(
                        `/freelancer/dashboard/${freelancerId}`
                    );


                setFreelancer(
                    response.data.freelancer
                );


                setRequests(
                    response.data.negotiation_requests || []
                );

            }

            catch (error) {

                console.error(
                    "Freelancer dashboard error:",
                    error
                );


                setMessage(

                    error.response?.data?.detail ||

                    "Failed to load freelancer dashboard"

                );

            }

            finally {

                setLoading(false);

            }

        };


        if (freelancerId) {

            fetchDashboard();

        }

    }, [freelancerId]);


    // ========================================================
    // LOGOUT
    // ========================================================

    const logout = () => {

        localStorage.removeItem(
            "freelancer_id"
        );

        localStorage.removeItem(
            "freelancer_name"
        );

        localStorage.removeItem(
            "freelancer_token"
        );

        localStorage.removeItem(
            "freelancer"
        );


        navigate(
            "/freelancer-login"
        );

    };


    const viewProjectDetails = async (projectId) => {
        try {
            setProjectLoading(true);
            setProjectMessage("");
            setSelectedProject({ loading: true });

            const response = await api.get(
                `/freelancer/project/${projectId}`
            );

            setSelectedProject(response.data);
        } catch (error) {
            setSelectedProject(null);
            setProjectMessage(
                error.response?.data?.detail ||
                "Failed to load project details"
            );
        } finally {
            setProjectLoading(false);
        }
    };


    const closeProjectDetails = () => {
        setSelectedProject(null);
        setProjectMessage("");
    };


    // ========================================================
    // LOADING
    // ========================================================

    if (loading) {

        return (

            <div className="dashboard-container">

                <div className="dashboard-card">

                    <h2>
                        Loading Freelancer Dashboard...
                    </h2>

                </div>

            </div>

        );

    }


    // ========================================================
    // ERROR / FREELANCER NOT FOUND
    // ========================================================

    if (!freelancer) {

        return (

            <div className="dashboard-container">

                <div className="dashboard-card">

                    <h2>
                        Freelancer not found
                    </h2>


                    <p>
                        {message}
                    </p>


                    <button
                        onClick={() =>
                            navigate(
                                "/freelancer-login"
                            )
                        }
                    >

                        Freelancer Login

                    </button>

                </div>

            </div>

        );

    }


    // ========================================================
    // NEGOTIATION STATUS
    //
    // Backend can return a negotiation in any of these
    // states after AI negotiation is completed.
    // ========================================================

    const completedRequests =
        requests.filter(

            (request) =>

                [
                    "NEGOTIATION_COMPLETED",
                    "CLIENT_ACCEPTED",
                    "FREELANCER_ACCEPTED",
                    "BOTH_ACCEPTED"
                ].includes(
                    request.status
                )

        );


    // ========================================================
    // STATUS TEXT
    // ========================================================

    const getStatusText = (status) => {

        switch (status) {

            case "NEGOTIATION_COMPLETED":

                return "Negotiation Completed";

            case "CLIENT_ACCEPTED":

                return "Client Accepted - Waiting for Freelancer";

            case "FREELANCER_ACCEPTED":

                return "Freelancer Accepted - Waiting for Client";

            case "BOTH_ACCEPTED":

                return "Both Accepted - Contract Ready";

            default:

                return status || "Unknown";

        }

    };


    // ========================================================
    // DECISION TEXT
    // ========================================================

    const getDecisionText = (decision) => {

        if (!decision) {

            return "WAITING";

        }

        return decision;

    };


    // ========================================================
    // MAIN DASHBOARD
    // ========================================================

    return (

        <div className="dashboard-container freelancer-dashboard">


            {/* =================================================
                NAVIGATION
            ================================================= */}

            <nav className="dashboard-nav">

                <h2>
                    AI Freelance Platform
                </h2>


                <button
                    onClick={logout}
                >

                    Logout

                </button>

            </nav>


            {/* =================================================
                MAIN DASHBOARD
            ================================================= */}

            <div className="dashboard-card freelancer-dashboard-card">


                <h1>

                    Welcome,{" "}

                    {freelancer.full_name}

                    {" "}👋

                </h1>


                <p>
                    Freelancer Dashboard
                </p>


                {/* =================================================
                    PROFILE
                ================================================= */}

                <div className="freelancer-profile">

                    <h2>
                        My Profile
                    </h2>


                    <p>

                        <strong>
                            Freelancer ID:
                        </strong>{" "}

                        {freelancer.freelancer_id}

                    </p>


                    <p>

                        <strong>
                            Name:
                        </strong>{" "}

                        {freelancer.full_name}

                    </p>


                    <p>

                        <strong>
                            Email:
                        </strong>{" "}

                        {freelancer.email}

                    </p>


                    <p>

                        <strong>
                            Professional Title:
                        </strong>{" "}

                        {freelancer.title ||
                            "Not specified"}

                    </p>


                    <p>

                        <strong>
                            Skills:
                        </strong>{" "}

                        {freelancer.skills ||
                            "Not specified"}

                    </p>


                    <p>

                        <strong>
                            Hourly Rate:
                        </strong>{" "}

                        ${freelancer.hourly_rate || 0}/hr

                    </p>


                    <p>

                        <strong>
                            Country:
                        </strong>{" "}

                        {freelancer.country ||
                            "Not specified"}

                    </p>

                </div>


                {/* =================================================
                    NEGOTIATED PROJECTS
                ================================================= */}

                <div className="negotiation-section">

                    <h2>
                        Negotiated Projects
                    </h2>


                    {
                        completedRequests.length === 0

                        ?

                        (

                            <div>

                                <p>
                                    No negotiated projects available yet.
                                </p>

                            </div>

                        )

                        :

                        (

                            <div>

                                {
                                    completedRequests.map(
                                        (request) => {

                                            const result =
                                                request.negotiation_result || {};


                                            return (

                                                <div
                                                    className="negotiation-request"
                                                    key={
                                                        request.request_id
                                                    }
                                                >


                                                    {/* =================================================
                                                        NEGOTIATION STATUS
                                                    ================================================= */}

                                                    <h3>

                                                        {getStatusText(
                                                            request.status
                                                        )}

                                                    </h3>


                                                    {/* =================================================
                                                        REQUEST ID
                                                    ================================================= */}

                                                    <p>

                                                        <strong>
                                                            Request ID:
                                                        </strong>{" "}

                                                        {
                                                            request.request_id
                                                        }

                                                    </p>


                                                    {/* =================================================
                                                        PROJECT ID
                                                    ================================================= */}

                                                    <p>

                                                        <strong>
                                                            Project ID:
                                                        </strong>{" "}

                                                        {
                                                            request.project_id
                                                        }

                                                    </p>


                                                    {/* =================================================
                                                        STATUS
                                                    ================================================= */}

                                                    <p>

                                                        <strong>
                                                            Status:
                                                        </strong>{" "}

                                                        {
                                                            request.status
                                                        }

                                                    </p>


                                                    {/* =================================================
                                                        FINAL NEGOTIATED PRICE
                                                    ================================================= */}

                                                    {
                                                        result.final_price !==
                                                        undefined &&

                                                        (

                                                            <p>

                                                                <strong>
                                                                    Final Price:
                                                                </strong>{" "}

                                                                $

                                                                {
                                                                    Number(
                                                                        result.final_price
                                                                    ).toLocaleString(
                                                                        undefined,
                                                                        {
                                                                            minimumFractionDigits: 2,
                                                                            maximumFractionDigits: 2
                                                                        }
                                                                    )
                                                                }

                                                            </p>

                                                        )
                                                    }


                                                    {/* =================================================
                                                        FINAL NEGOTIATED TIMELINE
                                                    ================================================= */}

                                                    {
                                                        result.final_timeline_days !==
                                                        undefined &&

                                                        (

                                                            <p>

                                                                <strong>
                                                                    Final Timeline:
                                                                </strong>{" "}

                                                                {
                                                                    result.final_timeline_days
                                                                }

                                                                {" "}days

                                                            </p>

                                                        )
                                                    }


                                                    {/* =================================================
                                                        AI NEGOTIATION ROUNDS
                                                    ================================================= */}

                                                    {
                                                        result.rounds !==
                                                        undefined &&

                                                        (

                                                            <p>

                                                                <strong>
                                                                    Negotiation Rounds:
                                                                </strong>{" "}

                                                                {
                                                                    result.rounds
                                                                }

                                                            </p>

                                                        )
                                                    }


                                                    {/* =================================================
                                                        CLIENT DECISION
                                                    ================================================= */}

                                                    <p>

                                                        <strong>
                                                            Client Decision:
                                                        </strong>{" "}

                                                        {
                                                            getDecisionText(
                                                                request.client_decision
                                                            )
                                                        }

                                                    </p>


                                                    {/* =================================================
                                                        FREELANCER DECISION
                                                    ================================================= */}

                                                    <p>

                                                        <strong>
                                                            Freelancer Decision:
                                                        </strong>{" "}

                                                        {
                                                            getDecisionText(
                                                                request.freelancer_decision
                                                            )
                                                        }

                                                    </p>


                                                    {/* =================================================
                                                        CONTRACT STATUS
                                                    ================================================= */}

                                                    {
                                                        request.contract_status &&

                                                        (

                                                            <p>

                                                                <strong>
                                                                    Contract Status:
                                                                </strong>{" "}

                                                                {
                                                                    request.contract_status
                                                                }

                                                            </p>

                                                        )
                                                    }


                                                    {/* =================================================
                                                        VIEW FINAL TERMS
                                                    ================================================= */}

                                                    <div className="negotiation-actions">

                                                        <button
                                                            onClick={() =>
                                                                viewProjectDetails(
                                                                    request.project_id
                                                                )
                                                            }
                                                        >
                                                            View Project
                                                        </button>

                                                        <button
                                                            onClick={() =>
                                                                navigate(
                                                                    `/negotiation/${request.request_id}?role=freelancer`
                                                                )
                                                            }
                                                        >
                                                            View Final Terms
                                                        </button>

                                                    </div>


                                                </div>

                                            );

                                        }

                                    )
                                }

                            </div>

                        )
                    }

                </div>


                {/* =================================================
                    ERROR / INFORMATION MESSAGE
                ================================================= */}

                {
                    message &&

                    (

                        <p className="message">

                            {message}

                        </p>

                    )
                }


            </div>


            {
                (selectedProject || projectMessage) &&

                (

                    <div
                        className="project-details-overlay"
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby="project-details-title"
                        onClick={closeProjectDetails}
                    >

                        <div
                            className="project-details-modal"
                            onClick={(event) => event.stopPropagation()}
                        >

                            <button
                                className="project-details-close"
                                onClick={closeProjectDetails}
                                aria-label="Close project details"
                            >
                                x
                            </button>

                            <h2 id="project-details-title">
                                Project Description
                            </h2>

                            {
                                projectLoading &&
                                <p>Loading project details...</p>
                            }

                            {
                                projectMessage &&
                                <p className="message">{projectMessage}</p>
                            }

                            {
                                selectedProject &&
                                !selectedProject.loading &&
                                (
                                    <div className="project-details-content">
                                        <h3>
                                            {selectedProject.title || "Untitled project"}
                                        </h3>

                                        <p className="project-full-description">
                                            {selectedProject.description || "No description provided."}
                                        </p>

                                        <dl>
                                            <div>
                                                <dt>Status</dt>
                                                <dd>{selectedProject.status || "Submitted"}</dd>
                                            </div>
                                            <div>
                                                <dt>Project ID</dt>
                                                <dd>{selectedProject.project_id}</dd>
                                            </div>
                                            {
                                                selectedProject.created_at &&
                                                <div>
                                                    <dt>Created</dt>
                                                    <dd>{new Date(selectedProject.created_at).toLocaleString()}</dd>
                                                </div>
                                            }
                                        </dl>
                                    </div>
                                )
                            }

                        </div>

                    </div>

                )
            }

        </div>

    );

}


export default FreelancerDashboard;