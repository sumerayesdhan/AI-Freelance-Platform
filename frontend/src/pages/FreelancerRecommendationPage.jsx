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

            setMessage("");


            const response = await api.get(
                `/freelancers/recommend/${projectId}`
            );


            setFreelancers(
                response.data.recommendations ||
                response.data ||
                []
            );

        }

        catch (error) {

            console.error(
                "Failed to load freelancer recommendations:",
                error
            );


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
            // STEP 1
            // CREATE NEGOTIATION REQUEST
            // =================================================

            const requestResponse = await api.post(

                "/negotiation/request",

                {

                    freelancer_id:
                        Number(
                            person.freelancer_id
                        ),

                    project_id:
                        String(
                            projectId
                        )

                }

            );


            console.log(
                "Negotiation request created:",
                requestResponse.data
            );


            const requestId =
                requestResponse.data.request_id;


            if (!requestId) {

                throw new Error(
                    "Negotiation request ID was not returned by the server."
                );

            }


            // =================================================
            // SAVE NEGOTIATION INFORMATION
            // =================================================

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
            // STEP 2
            // RUN AUTONOMOUS AI NEGOTIATION
            //
            // Client Agent ↔ Freelancer Agent
            //
            // NO HUMAN FREELANCER INPUT HERE
            // =================================================

            setMessage(
                "AI agents are negotiating the project terms..."
            );


            const negotiationResponse =
                await api.post(
                    `/negotiation/auto-negotiate?request_id=${encodeURIComponent(
                        requestId
                    )}`
                );


            console.log(
                "Autonomous negotiation result:",
                negotiationResponse.data
            );


            // =================================================
            // STEP 3
            // CHECK NEGOTIATION RESULT
            // =================================================

            const result =
                negotiationResponse.data;


            if (
                result.status ===
                "NEGOTIATION_COMPLETED"
                &&
                result.agreement === true
            ) {

                // ---------------------------------------------
                // SAVE FINAL NEGOTIATION RESULT
                // ---------------------------------------------

                localStorage.setItem(
                    "negotiation_result",
                    JSON.stringify(result)
                );


                // ---------------------------------------------
                // GO TO FINAL NEGOTIATED TERMS
                //
                // IMPORTANT:
                // Do NOT send the client to freelancer login.
                // ---------------------------------------------

                navigate(
                    `/negotiation/${requestId}?role=client`
                );


                return;

            }


            // =================================================
            // NEGOTIATION FAILED
            // =================================================

            if (
                result.status ===
                "NEGOTIATION_FAILED"
            ) {

                setMessage(
                    result.negotiation_result?.failure_reason ||
                    result.failure_reason ||
                    "AI negotiation could not reach an agreement."
                );


                return;

            }


            // =================================================
            // UNEXPECTED RESPONSE
            // =================================================

            setMessage(
                "Negotiation finished, but no final agreement was returned."
            );

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

            <ClientSidebar />

            <ClientHeader />


            <h1>
                Top Freelancer Recommendations
            </h1>


            {
                message &&

                (

                    <p className="message">

                        {message}

                    </p>

                )
            }


            {
                freelancers.length === 0 &&
                !message

                ?

                (

                    <p className="recommend-empty">

                        No matching freelancers were found
                        for this project.

                    </p>

                )

                :

                freelancers.map(
                    (person) => (

                        <div
                            className="freelancer-card"
                            key={
                                person.freelancer_id
                            }
                        >


                            {/* =================================
                                FREELANCER NAME
                            ================================= */}

                            <h2>

                                #{person.rank}

                                {" "}

                                {
                                    person.freelancer_name
                                }

                            </h2>


                            {/* =================================
                                TITLE
                            ================================= */}

                            <p className="title">

                                {
                                    person.title
                                }

                            </p>


                            {/* =================================
                                DETAILS
                            ================================= */}

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

                                        {
                                            person.job_success
                                        }

                                    </b>

                                </p>


                                <p>

                                    💰 Hourly Rate:

                                    {" "}

                                    <b>

                                        $
                                        {
                                            person.hourly_rate
                                        }

                                    </b>

                                </p>


                            </div>


                            {/* =================================
                                START NEGOTIATION
                            ================================= */}

                            <button

                                className="start-negotiation-btn"

                                onClick={() =>
                                    startNegotiation(
                                        person
                                    )
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

                    )
                )
            }


        </div>

    );

}


export default FreelancerRecommendationPage;