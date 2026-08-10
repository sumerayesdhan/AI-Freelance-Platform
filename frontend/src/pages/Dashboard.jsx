import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";

import "../styles/dashboard.css";



function Dashboard(){


    const navigate = useNavigate();



    const [user,setUser] = useState("");

    const [project,setProject] = useState({

        title:"",

        description:""

    });



    const [message,setMessage] = useState("");

    const [loading,setLoading] = useState(false);







    useEffect(()=>{


        const fetchUser = async()=>{


            try{


                const response =
                await api.get(
                    "/dashboard"
                );


                setUser(
                    response.data.email
                );


            }


            catch(error){


                console.log(error);


                setMessage(
                    "Session expired"
                );


                localStorage.removeItem(
                    "token"
                );


                navigate("/login");


            }


        };


        fetchUser();


    },[navigate]);









    const handleChange=(e)=>{


        setProject({

            ...project,

            [e.target.name]:
            e.target.value

        });


    };









    const handleSubmit=async(e)=>{


        e.preventDefault();



        if(
            project.title.length < 3
        ){

            setMessage(
                "Project title is too short"
            );

            return;

        }



        if(
            project.description.length < 20
        ){

            setMessage(
                "Please provide more project details"
            );

            return;

        }




        try{


            setLoading(true);



            const response =
            await api.post(

                "/projects/create",

                project

            );



            const projectId =
            response.data.project_id;




            if(projectId){


                navigate(

                `/requirement-assistance/${projectId}`

                );


            }



        }


        catch(error){


            setMessage(

                error.response?.data?.detail ||

                "Project creation failed"

            );


        }


        finally{


            setLoading(false);


        }


    };







    const logout=()=>{


        localStorage.removeItem(
            "token"
        );


        localStorage.removeItem(
            "user"
        );


        navigate("/login");


    };







    return(


        <div className="dashboard-container">



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







            <div className="dashboard-card">



                <h1>

                    Welcome 👋

                </h1>



                <p>

                    {user}

                </p>






                <h2>

                    Submit Your Project

                </h2>





                <form onSubmit={handleSubmit}>


                    <label>

                        Project Title

                    </label>


                    <input

                        type="text"

                        name="title"

                        placeholder="Example: Smart Education Platform"

                        value={project.title}

                        onChange={handleChange}

                    />






                    <label>

                        Project Description

                    </label>


                    <textarea

                        name="description"

                        rows="7"

                        placeholder="Explain your project idea and requirements..."

                        value={project.description}

                        onChange={handleChange}

                    />




                    <small>

                    Minimum 20 characters

                    </small>






                    <button

                    disabled={loading}

                    >

                    {

                    loading

                    ?

                    "Creating..."

                    :

                    "Start Requirement Analysis"

                    }


                    </button>



                </form>





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



export default Dashboard;