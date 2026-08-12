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



function FreelancerRecommendationPage(){


    const {
        projectId
    } = useParams();


    const navigate = useNavigate();



    const [
        freelancers,
        setFreelancers
    ] = useState([]);




    useEffect(()=>{

        loadFreelancers();

    },[]);





    const loadFreelancers = async()=>{


        try{


            const response = await api.get(

                `/freelancers/recommend/${projectId}`

            );


            setFreelancers(

                response.data.recommendations

            );


        }


        catch(error){

            console.log(error);

        }


    };







    const startNegotiation = ()=>{


        navigate(

            `/negotiation/${projectId}`,

            {

                state:{

                    freelancers

                }

            }

        );


    };







    return(


        <div className="recommend-container">



            <h1>

                Top Freelancer Recommendations

            </h1>





            {

            freelancers.map((person)=>(


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

                        <b>

                        {person.job_success}

                        </b>


                        </p>






                        <p>

                        💰 Hourly Rate:

                        <b>

                        $

                        {person.hourly_rate}

                        </b>


                        </p>



                    </div>




                </div>


            ))

            }





            {/* SINGLE NEGOTIATION BUTTON */}


            <button

            className="start-negotiation-btn"

            onClick={startNegotiation}

            >

                Start AI Negotiation

            </button>




        </div>


    );


}


export default FreelancerRecommendationPage;