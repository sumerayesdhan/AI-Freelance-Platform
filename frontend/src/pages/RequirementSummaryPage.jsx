import {
    useParams,
    useNavigate
} from "react-router-dom";

import {
    useEffect,
    useState
} from "react";


import api from "../services/api";


import "../styles/summary.css";



function RequirementSummaryPage(){


    const {
        projectId
    } = useParams();



    const navigate = useNavigate();



    const [requirement,setRequirement] = useState(null);

    const [loading,setLoading] = useState(true);





    useEffect(()=>{


        const fetchAnalysis = async()=>{


            try{


                const response = await api.get(

                    `/conversation/analysis/${projectId}`

                );



                console.log(
                    response.data
                );



                setRequirement(

                    response.data.requirement_analysis

                );



            }


            catch(error){


                console.log(error);


            }


            finally{


                setLoading(false);


            }


        };



        fetchAnalysis();



    },[projectId]);








    if(loading){


        return (

            <h2>

                Generating Requirement Analysis...

            </h2>

        );

    }








    if(!requirement){


        return (

            <h2>

                No requirement data found

            </h2>

        );

    }







    return(


        <div className="summary-container">



            <h1>

                Final Requirement Analysis

            </h1>






            <div className="summary-card">


                <h3>

                    Domain

                </h3>


                <p>

                    {requirement.project_domain}

                </p>




                <h3>

                    Project Type

                </h3>


                <p>

                    {requirement.project_type}

                </p>






                <h3>

                    Platform

                </h3>


                <p>

                    {requirement.platform}

                </p>






                <h3>

                    Target Users

                </h3>


                <ul>


                {

                requirement.target_users?.map(

                    (user,index)=>(

                        <li key={index}>

                            {user}

                        </li>

                    )

                )

                }


                </ul>







                <h3>

                    Features

                </h3>


                <ul>


                {

                requirement.features?.map(

                    (feature,index)=>(

                        <li key={index}>

                            {feature}

                        </li>

                    )

                )


                }


                </ul>







                <h3>

                    Technology Preference

                </h3>


                <p>

                {

                requirement.technology_preference

                ||

                "AI Recommended"

                }

                </p>







                <button


                    onClick={()=>


                        navigate(

                            `/project/${projectId}/analysis`

                        )


                    }


                >

                    Proceed To Complexity Prediction

                </button>



            </div>
        </div>


    );


}



export default RequirementSummaryPage;