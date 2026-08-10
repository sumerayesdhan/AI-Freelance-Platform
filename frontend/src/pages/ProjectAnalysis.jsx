import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import api from "../services/api";

import "../styles/analysis.css";



function ProjectAnalysis(){


    const {projectId}=useParams();


    const [analysis,setAnalysis]=useState(null);


    const [loading,setLoading]=useState(true);





    useEffect(()=>{


        const fetchAnalysis=async()=>{


            try{


                const response =
                await api.get(

                    `/conversation/analysis/${projectId}`

                );


                setAnalysis(
                    response.data
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

            <h2 className="loading">

            Generating Project Analysis...

            </h2>

        );

    }







    if(!analysis){


        return (

            <h2>

            No analysis available

            </h2>

        );

    }







    const requirement =
    analysis.requirement_analysis;



    const complexity =
    analysis.complexity_analysis;







    return(


        <div className="analysis-container">





            <h1>

            Project Analysis

            </h1>






            <div className="analysis-card">


                <h2>

                Requirement Summary

                </h2>




                <div className="info-item">

                <b>Domain:</b>

                <span>

                {requirement.project_domain}

                </span>

                </div>





                <div className="info-item">

                <b>Project Type:</b>

                <span>

                {requirement.project_type}

                </span>

                </div>





                <div className="info-item">

                <b>Platform:</b>

                <span>

                {requirement.platform}

                </span>

                </div>







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


            </div>









            <div className="complexity-section">


                <h2>

                Complexity Prediction

                </h2>





                <div className="metric-grid">



                    <div className="metric-card">

                        <h3>
                        Complexity
                        </h3>


                        <h1>

                        {complexity.complexity_level}

                        </h1>


                    </div>





                    <div className="metric-card">


                        <h3>

                        Duration

                        </h3>


                        <h1>

                        {complexity.estimated_duration}

                        </h1>


                    </div>





                    <div className="metric-card">


                        <h3>

                        Risk

                        </h3>


                        <h1>

                        {complexity.risk_level}

                        </h1>


                    </div>



                </div>








                <div className="analysis-card">


                    <h3>

                    Reason

                    </h3>


                    <p>

                    {complexity.reason}

                    </p>





                    <h3>

                    Technical Factors

                    </h3>



                    <ul>


                    {

                    complexity.technical_factors?.map(

                        (factor,index)=>(


                            <li key={index}>

                            {factor}

                            </li>


                        )

                    )

                    }


                    </ul>



                </div>



            </div>






        </div>


    );


}


export default ProjectAnalysis;