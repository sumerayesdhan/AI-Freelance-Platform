import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import api from "../services/api";

import "../styles/dashboard.css";


function FreelancerDashboard() {

    const navigate = useNavigate();

    const { freelancerId } = useParams();


    const [freelancer, setFreelancer] = useState(null);

    const [requests, setRequests] = useState([]);

    const [loading, setLoading] = useState(true);

    const [message, setMessage] = useState("");


    // ========================================================
    // FETCH FREELANCER DASHBOARD
    // ========================================================

    useEffect(() => {

        const fetchDashboard = async () => {

            try {

                setLoading(true);


                const response = await api.get(

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

                console.error(error);


                setMessage(

                    error.response?.data?.detail ||

                    "Failed to load freelancer dashboard"

                );

            }

            finally {

                setLoading(false);

            }

        };


        fetchDashboard();

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

        navigate("/freelancer-register");

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
    // ERROR
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
                            navigate("/freelancer-register")
                        }
                    >
                        Register Freelancer
                    </button>

                </div>

            </div>

        );

    }


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

                    Welcome, {freelancer.full_name} 👋

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

                        {freelancer.title || "Not specified"}

                    </p>


                    <p>

                        <strong>
                            Skills:
                        </strong>{" "}

                        {freelancer.skills || "Not specified"}

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

                        {freelancer.country || "Not specified"}

                    </p>

                </div>


                {/* =================================================
                    NEGOTIATION REQUESTS
                ================================================= */}

                <div className="negotiation-section">

                    <h2>

                        Negotiation Requests

                    </h2>


                    <p>

                        Pending Requests:{" "}

                        <strong>
                            {requests.length}
                        </strong>

                    </p>


                    {

                        requests.length === 0

                            ?

                            (

                                <p>

                                    No pending negotiation requests.

                                </p>

                            )

                            :

                            (

                                requests.map((request) => (

                                    <div

                                        className="negotiation-request"

                                        key={request.request_id}

                                    >

                                        <h3>

                                            New Project Request

                                        </h3>


                                        <p>

                                            <strong>
                                                Request ID:
                                            </strong>{" "}

                                            {request.request_id}

                                        </p>


                                        <p>

                                            <strong>
                                                Project ID:
                                            </strong>{" "}

                                            {request.project_id}

                                        </p>


                                        <p>

                                            <strong>
                                                Status:
                                            </strong>{" "}

                                            {request.status}

                                        </p>


                                        <button

                                            onClick={() => {

                                                navigate(
                                                    `/negotiation/${request.request_id}`
                                                );

                                            }}

                                        >

                                            View Negotiation

                                        </button>

                                    </div>

                                ))

                            )

                    }

                </div>


                {

                    message &&

                    <p className="message">

                        {message}

                    </p>

                }


            </div>

        </div>

    );

}


export default FreelancerDashboard;