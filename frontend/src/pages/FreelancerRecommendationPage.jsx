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


function FreelancerRecommendationPage() {

    const { projectId } = useParams();

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
                response.data.recommendations || []
            );

        }

        catch (error) {

            console.error(error);

            setMessage(
                error.response?.data?.detail ||
                "Failed to load freelancer recommendations"
            );

        }

    };


    // =========================================================
    // START AUTONOMOUS NEGOTIATION
    // =========================================================

    const startNegotiation = async (person) => {

        try {

            setLoadingId(
                person.freelancer_id
            );

            setMessage("");


            // =================================================
            // STEP 1:
            // CREATE NEGOTIATION REQUEST
            // =================================================

            const requestResponse =
                await api.post(

                    "/negotiation/request",

                    {

                        freelancer_id:
                            Number(
                                person.freelancer_id
                            ),

                        project_id:
                            String(projectId)

                    }

                );


            const requestId =
                requestResponse.data.request_id;


            if (!requestId) {

                throw new Error(
                    "Negotiation request ID was not returned"
                );

            }


            console.log(
                "Negotiation request created:",
                requestResponse.data
            );


            // =================================================
            // STEP 2:
            // RUN AUTONOMOUS AI NEGOTIATION
            // =================================================
            //
            // IMPORTANT:
            //
            // The human freelancer does NOT negotiate here.
            //
            // Client Agent
            //       ↕
            // Freelancer Agent
            //
            // negotiate automatically.
            //
            // =================================================

            setMessage(
                "AI agents are negotiating automatically..."
            );


            const negotiationResponse =
                await api.post(

                    "/negotiation/auto-negotiate",

                    null,

                    {

                        params: {

                            request_id:
                                requestId

                        }

                    }

                );


            console.log(
                "Autonomous negotiation result:",
                negotiationResponse.data
            );


            // =================================================
            // STEP 3:
            // CHECK RESULT
            // =================================================

            if (
                negotiationResponse.data.status ===
                "NEGOTIATION_COMPLETED"
            ) {

                // Save selected freelancer locally.
                // This does NOT replace MongoDB.
                localStorage.setItem(
                    "selected_freelancer",
                    JSON.stringify(person)
                );


                localStorage.setItem(
                    "negotiation_request_id",
                    requestId
                );


                localStorage.setItem(
                    "negotiation_project_id",
                    String(projectId)
                );


                // =================================================
                // STEP 4:
                // SHOW FINAL TERMS TO CLIENT
                // =================================================

                navigate(
                    `/negotiation/${requestId}?role=client`
                );


            }

            else {

                setMessage(

                    negotiationResponse.data.message ||

                    "Autonomous negotiation could not be completed"

                );

            }

        }

        catch (error) {

            console.error(
                "Start negotiation error:",
                error
            );


            setMessage(

                error.response?.data?.detail ||

                error.message ||

                "Failed to start autonomous negotiation"

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
                freelancers.length === 0

                    ?

                    (

                        <p>
                            No freelancer recommendations found.
                        </p>

                    )

                    :

                    (

                        freelancers.map((person) => (

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

                                            ${person.hourly_rate}

                                        </b>

                                    </p>


                                </div>


                                {/* =================================
                                    CLIENT STARTS NEGOTIATION
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

                                            "AI Negotiating..."

                                            :

                                            "Start Negotiation"

                                    }

                                </button>


                            </div>

                        ))

                    )

            }


        </div>

    );

}


export default FreelancerRecommendationPage;