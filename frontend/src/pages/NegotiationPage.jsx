import {
    useEffect,
    useState
} from "react";

import {
    useParams,
    useSearchParams,
    useNavigate
} from "react-router-dom";

import api from "../services/api";

import "../styles/dashboard.css";


function NegotiationPage() {

    const {
        requestId
    } = useParams();


    const [
        searchParams
    ] = useSearchParams();


    const navigate = useNavigate();


    const role =
        searchParams.get("role") || "client";


    const [
        negotiation,
        setNegotiation
    ] = useState(null);


    const [
        loading,
        setLoading
    ] = useState(true);


    const [
        decisionLoading,
        setDecisionLoading
    ] = useState(false);


    const [
        message,
        setMessage
    ] = useState("");


    // =========================================================
    // LOAD NEGOTIATION
    // =========================================================

    const loadNegotiation = async () => {

        try {

            setLoading(true);


            const response =
                await api.get(
                    `/negotiation/${requestId}`
                );


            setNegotiation(
                response.data
            );


        }

        catch (error) {

            console.error(error);


            setMessage(

                error.response?.data?.detail ||

                "Failed to load negotiation"

            );

        }

        finally {

            setLoading(false);

        }

    };


    useEffect(() => {

        loadNegotiation();

    }, [requestId]);


    // =========================================================
    // HUMAN ACCEPT / REJECT
    // =========================================================

    const submitDecision = async (decision) => {

        try {

            setDecisionLoading(true);

            setMessage("");


            let endpoint;


            if (role === "client") {

                endpoint =
                    `/negotiation/request/${requestId}/client-decision`;

            }

            else {

                endpoint =
                    `/negotiation/request/${requestId}/freelancer-decision`;

            }


            const response =
                await api.post(

                    endpoint,

                    null,

                    {

                        params: {
                            decision
                        }

                    }

                );


            console.log(
                "Decision response:",
                response.data
            );


            setMessage(
                response.data.message ||
                "Decision submitted successfully"
            );


            // Refresh MongoDB state
            await loadNegotiation();

        }

        catch (error) {

            console.error(
                "Decision error:",
                error
            );


            setMessage(

                error.response?.data?.detail ||

                "Failed to submit decision"

            );

        }

        finally {

            setDecisionLoading(false);

        }

    };


    // =========================================================
    // LOADING
    // =========================================================

    if (loading) {

        return (

            <div className="dashboard-container">

                <div className="dashboard-card">

                    <h2>
                        Loading negotiation...
                    </h2>

                </div>

            </div>

        );

    }


    // =========================================================
    // ERROR
    // =========================================================

    if (!negotiation) {

        return (

            <div className="dashboard-container">

                <div className="dashboard-card">

                    <h2>
                        Negotiation not found
                    </h2>

                    <p>
                        {message}
                    </p>

                </div>

            </div>

        );

    }


    const result =
        negotiation.negotiation_result;


    const agreement =
        result?.agreement;


    const finalPrice =
        result?.final_price;


    const finalTimeline =
        result?.final_timeline_days;


    const clientDecision =
        negotiation.client_decision;


    const freelancerDecision =
        negotiation.freelancer_decision;


    const contractStatus =
        negotiation.contract_status;


    const myDecision =
        role === "client"
            ? clientDecision
            : freelancerDecision;


    // =========================================================
    // NEGOTIATION FAILED
    // =========================================================

    if (
        negotiation.status ===
        "NEGOTIATION_FAILED"
    ) {

        return (

            <div className="dashboard-container">

                <div className="dashboard-card">

                    <h1>
                        Negotiation Failed
                    </h1>

                    <p>
                        The AI agents could not reach
                        an agreement.
                    </p>


                    <p>
                        Request ID:{" "}
                        <strong>
                            {requestId}
                        </strong>
                    </p>

                </div>

            </div>

        );

    }


    // =========================================================
    // RENDER
    // =========================================================

    return (

        <div className="dashboard-container">


            <nav className="dashboard-nav">

                <h2>
                    AI Freelance Platform
                </h2>


                {
                    role === "freelancer"

                        ?

                        (

                            <button
                                onClick={() =>
                                    navigate(
                                        `/freelancer-dashboard/${negotiation.freelancer_id}`
                                    )
                                }
                            >
                                Back to Dashboard
                            </button>

                        )

                        :

                        (

                            <button
                                onClick={() =>
                                    navigate("/dashboard")
                                }
                            >
                                Dashboard
                            </button>

                        )

                }

            </nav>


            <div className="dashboard-card">


                {/* =================================================
                    HEADER
                ================================================= */}

                <h1>
                    Final Negotiated Terms
                </h1>


                <p>

                    Request ID:{" "}

                    <strong>
                        {requestId}
                    </strong>

                </p>


                <p>

                    Status:{" "}

                    <strong>
                        {negotiation.status}
                    </strong>

                </p>


                {/* =================================================
                    AGREEMENT
                ================================================= */}

                {
                    agreement

                        ?

                        (

                            <>

                                <div
                                    style={{
                                        marginTop: "25px",
                                        padding: "20px",
                                        borderRadius: "10px",
                                        border: "1px solid #ddd"
                                    }}
                                >

                                    <h2>
                                        Agreement Reached ✅
                                    </h2>


                                    <p>

                                        <strong>
                                            Final Price:
                                        </strong>

                                        {" "}

                                        $
                                        {
                                            Number(
                                                finalPrice
                                            ).toLocaleString(
                                                undefined,
                                                {
                                                    minimumFractionDigits: 2,
                                                    maximumFractionDigits: 2
                                                }
                                            )
                                        }

                                    </p>


                                    <p>

                                        <strong>
                                            Final Timeline:
                                        </strong>

                                        {" "}

                                        {finalTimeline} days

                                    </p>


                                    <p>

                                        <strong>
                                            Negotiation Rounds:
                                        </strong>

                                        {" "}

                                        {result?.rounds || 0}

                                    </p>

                                </div>


                                {/* =================================================
                                    HUMAN DECISION STATUS
                                ================================================= */}

                                <div
                                    style={{
                                        marginTop: "25px",
                                        padding: "20px",
                                        borderRadius: "10px",
                                        border: "1px solid #ddd"
                                    }}
                                >

                                    <h2>
                                        Acceptance Status
                                    </h2>


                                    <p>

                                        <strong>
                                            Client:
                                        </strong>

                                        {" "}

                                        {clientDecision || "Waiting"}

                                    </p>


                                    <p>

                                        <strong>
                                            Freelancer:
                                        </strong>

                                        {" "}

                                        {freelancerDecision || "Waiting"}

                                    </p>


                                </div>


                                {/* =================================================
                                    MY DECISION
                                ================================================= */}

                                {
                                    myDecision

                                        ?

                                        (

                                            <div
                                                style={{
                                                    marginTop: "25px"
                                                }}
                                            >

                                                <h2>
                                                    Your Decision
                                                </h2>


                                                <p>

                                                    You selected:

                                                    {" "}

                                                    <strong>
                                                        {myDecision}
                                                    </strong>

                                                </p>


                                                {
                                                    myDecision === "ACCEPT" &&
                                                    freelancerDecision === null &&
                                                    role === "client"

                                                        ?

                                                        (
                                                            <p>
                                                                Waiting for the freelancer
                                                                to accept the final terms.
                                                            </p>
                                                        )

                                                        :

                                                        null
                                                }


                                                {
                                                    myDecision === "ACCEPT" &&
                                                    clientDecision === null &&
                                                    role === "freelancer"

                                                        ?

                                                        (
                                                            <p>
                                                                Waiting for the client
                                                                to accept the final terms.
                                                            </p>
                                                        )

                                                        :

                                                        null
                                                }


                                            </div>

                                        )

                                        :

                                        (

                                            <div
                                                style={{
                                                    marginTop: "30px"
                                                }}
                                            >

                                                <h2>

                                                    {
                                                        role === "client"
                                                            ? "Client Decision"
                                                            : "Freelancer Decision"
                                                    }

                                                </h2>


                                                <p>

                                                    Review the final negotiated
                                                    price and timeline carefully.

                                                </p>


                                                <div
                                                    style={{
                                                        display: "flex",
                                                        gap: "15px",
                                                        marginTop: "20px"
                                                    }}
                                                >

                                                    <button

                                                        onClick={() =>
                                                            submitDecision(
                                                                "ACCEPT"
                                                            )
                                                        }

                                                        disabled={
                                                            decisionLoading
                                                        }

                                                    >

                                                        {
                                                            decisionLoading
                                                                ? "Submitting..."
                                                                : "Accept Terms"
                                                        }

                                                    </button>


                                                    <button

                                                        onClick={() =>
                                                            submitDecision(
                                                                "REJECT"
                                                            )
                                                        }

                                                        disabled={
                                                            decisionLoading
                                                        }

                                                    >

                                                        Reject Terms

                                                    </button>

                                                </div>

                                            </div>

                                        )

                                }


                                {/* =================================================
                                    CONTRACT STATUS
                                ================================================= */}

                                <div
                                    style={{
                                        marginTop: "30px",
                                        padding: "20px",
                                        borderRadius: "10px",
                                        border: "1px solid #ddd"
                                    }}
                                >

                                    <h2>
                                        Contract Status
                                    </h2>


                                    {
                                        contractStatus ===
                                        "CONTRACT_READY"

                                            ?

                                            (

                                                <p>
                                                    ✅ Both client and freelancer
                                                    accepted. Contract is ready
                                                    for generation.
                                                </p>

                                            )

                                            :

                                            (

                                                <p>
                                                    Contract will be generated
                                                    only after both parties accept.
                                                </p>

                                            )

                                    }

                                </div>


                            </>

                        )

                        :

                        (

                            <div>

                                <h2>
                                    No Agreement
                                </h2>

                                <p>
                                    The AI agents did not reach
                                    mutually acceptable terms.
                                </p>

                            </div>

                        )

                }


                {
                    message &&

                    <p
                        className="message"
                        style={{
                            marginTop: "20px"
                        }}
                    >
                        {message}
                    </p>

                }


            </div>

        </div>

    );

}


export default NegotiationPage;