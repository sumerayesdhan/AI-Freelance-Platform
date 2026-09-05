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

        <div className="dashboard-container">


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

            <div className="dashboard-card">


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

        </div>

    );

}


export default FreelancerDashboard;