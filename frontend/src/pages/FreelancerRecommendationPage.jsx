import {
    useEffect,
    useState
} from "react";

import {
    useParams,
    useNavigate
} from "react-router-dom";

import api from "../services/api";

import "../styles/freelancer.css";
import ClientHeader from "../components/ClientHeader";
import ClientSidebar from "../components/ClientSidebar";


function FreelancerRecommendationPage() {

    const {
        projectId
    } = useParams();


    const navigate = useNavigate();


    const [
        freelancers,
        setFreelancers
    ] = useState([]);


    const [
        loadingId,
        setLoadingId
    ] = useState(null);


    const [
        message,
        setMessage
    ] = useState("");


    // =========================================================
    // LOAD RECOMMENDED FREELANCERS
    // =========================================================

    useEffect(() => {

        loadFreelancers();

    }, [projectId]);


    const loadFreelancers = async () => {

        try {

            const response = await api.get(
                `/freelancers/recommend/${projectId}`
            );


            setFreelancers(
                response.data.recommendations || response.data || []
            );

        }

        catch (error) {

            console.log(error);

            setMessage(
                "Failed to load freelancer recommendations"
            );

        }

    };


    // =========================================================
    // START NEGOTIATION
    // =========================================================

    const startNegotiation = async (person) => {

        try {

            setLoadingId(
                person.freelancer_id
            );

            setMessage("");


            // -------------------------------------------------
            // CREATE NEGOTIATION REQUEST
            // -------------------------------------------------

            const response = await api.post(

                "/negotiation/request",

                {

                    freelancer_id:
                        Number(person.freelancer_id),

                    project_id:
                        String(projectId)

                }

            );


            console.log(
                "Negotiation request created:",
                response.data
            );


            // -------------------------------------------------
            // NEGOTIATION REQUEST CREATED SUCCESSFULLY
            // -------------------------------------------------
            //
            // At this point the backend has:
            //
            // 1. Found the freelancer
            //
            // 2. Created the freelancer account
            //    if it does not already exist
            //
            // 3. Generated:
            //
            //    freelancer<ID>@example.com
            //
            // 4. Set demo password:
            //
            //    123456
            //
            // 5. Stored the negotiation request
            //    in MongoDB
            //
            // -------------------------------------------------


            // -------------------------------------------------
            // SAVE SELECTED FREELANCER INFORMATION
            // -------------------------------------------------

            localStorage.setItem(
                "selected_freelancer",
                JSON.stringify(person)
            );


            localStorage.setItem(
                "negotiation_request_id",
                response.data.request_id
            );


            localStorage.setItem(
                "negotiation_project_id",
                String(projectId)
            );


            // -------------------------------------------------
            // GO DIRECTLY TO FREELANCER LOGIN
            // -------------------------------------------------

            navigate(
                "/freelancer-login"
            );


        }

        catch (error) {

            console.log(
                "Start negotiation error:",
                error
            );


            setMessage(

                error.response?.data?.detail ||

                "Failed to start negotiation"

            );

        }

        finally {

            setLoadingId(null);

        }

    };


    // =========================================================
    // UI
    // =========================================================

    return (

        <div className="recommend-container">

            <ClientSidebar />

            <ClientHeader />


            <h1>
                Top Freelancer Recommendations
            </h1>


            {
                message &&

                <p className="message">
                    {message}
                </p>
            }


            {
                freelancers.length === 0 && !message ? (
                    <p className="recommend-empty">No matching freelancers were found for this project.</p>
                ) : freelancers.map((person) => (

                    <div
                        className="freelancer-card"
                        key={person.freelancer_id}
                    >


                        <h2>

                            #{person.rank}

                            {" "}

                            {person.freelancer_name}

                        </h2>


                        <p className="title">

                            {person.title}

                        </p>


                        <div className="details">


                            <p>

                                ⭐ Match Probability:

                                {" "}

                                <b>

                                    {
                                        (
                                            person.recommendation_probability
                                            *
                                            100
                                        ).toFixed(2)
                                    }%

                                </b>

                            </p>


                            <p>

                                🏆 Job Success:

                                {" "}

                                <b>

                                    {person.job_success}

                                </b>

                            </p>


                            <p>

                                💰 Hourly Rate:

                                {" "}

                                <b>

                                    $
                                    {person.hourly_rate}

                                </b>

                            </p>


                        </div>


                        {/* =================================
                            START NEGOTIATION
                        ================================= */}


                        <button

                            className="start-negotiation-btn"

                            onClick={() =>
                                startNegotiation(person)
                            }

                            disabled={
                                loadingId ===
                                person.freelancer_id
                            }

                        >

                            {

                                loadingId ===
                                person.freelancer_id

                                    ?

                                    "Starting..."

                                    :

                                    "Start Negotiation"

                            }

                        </button>


                    </div>

                ))
            }


        </div>

    );

}


export default FreelancerRecommendationPage;