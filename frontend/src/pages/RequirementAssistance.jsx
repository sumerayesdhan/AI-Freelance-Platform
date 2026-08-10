import { useParams, useNavigate } from "react-router-dom";

import { useEffect, useState } from "react";

import api from "../services/api";

import RequirementChat from "./RequirementChat";

import RequirementSummary from "../components/RequirementSummary";

import "../styles/chat.css";



function RequirementAssistance(){


    const {projectId}=useParams();


    const navigate=useNavigate();



    const [project,setProject]=useState(null);


    const [requirement,setRequirement]=useState(null);


    const [complexity,setComplexity]=useState(null);


    const [loading,setLoading]=useState(false);






    useEffect(()=>{


        const fetchProject=async()=>{


            try{


                const response =
                await api.get(

                    `/projects/${projectId}`

                );


                setProject(
                    response.data
                );


            }

            catch(error){

                console.log(error);

            }


        };



        fetchProject();


    },[projectId]);









    const generateRequirement=async()=>{


        try{


            setLoading(true);



            const response =
            await api.get(

            `/conversation/understand/${projectId}`

            );



            setRequirement(

                response.data.requirement_analysis

            );



            setComplexity(

                response.data.complexity_analysis

            );


        }


        catch(error){


            console.log(error);


        }


        finally{


            setLoading(false);


        }


    };








    if(!project){


        return (

            <h2>

            Loading project...

            </h2>

        );

    }







    return(


        <div className="chat-page">



            <div className="chat-header">


                <h1>

                Requirement Assistance

                </h1>


                <h3>

                {project.title}

                </h3>


            </div>







            <div className="project-description">


                <h3>

                Initial Description

                </h3>


                <p>

                {project.description}

                </p>


            </div>







            <RequirementChat


                projectId={projectId}


                initialDescription={
                    project.description
                }


            />







            <button


                className="primary-btn"


                onClick={
                    generateRequirement
                }


                disabled={loading}


            >


            {

            loading

            ?

            "Analyzing..."

            :

            "Generate Requirement Analysis"

            }


            </button>







            {
                requirement &&


                <>


                <RequirementSummary

                    data={requirement}

                />



                <button


                className="primary-btn"


                onClick={()=>navigate(

                `/project/${projectId}/analysis`

                )}


                >

                View Project Analysis

                </button>


                </>


            }




        </div>


    );

}



export default RequirementAssistance;