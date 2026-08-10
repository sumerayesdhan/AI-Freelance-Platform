import { useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";

import "../styles/auth.css";



function Login(){


    const navigate = useNavigate();



    const [formData,setFormData] = useState({

        email:"",
        password:""

    });



    const [message,setMessage] = useState("");

    const [loading,setLoading] = useState(false);





    const handleChange=(e)=>{


        setFormData({

            ...formData,

            [e.target.name]:
            e.target.value

        });


    };







    const handleSubmit = async(e)=>{


        e.preventDefault();




        if(
            !formData.email ||
            !formData.password
        ){

            setMessage(
                "Please enter email and password"
            );

            return;

        }




        try{


            setLoading(true);



            const response = await api.post(

                "/auth/login",

                formData

            );



            const token =
            response.data.access_token;



            localStorage.setItem(

                "token",

                token

            );



            localStorage.setItem(

                "user",

                formData.email

            );



            setMessage(
                "Login successful"
            );



            setTimeout(()=>{


                navigate("/dashboard");


            },500);



        }


        catch(error){


            setMessage(

                error.response?.data?.detail ||

                "Login failed"

            );


        }


        finally{


            setLoading(false);


        }


    };








    return(


        <div className="auth-container">


            <div className="auth-card">


                <h1>

                    AI Freelance Platform

                </h1>



                <h2>

                    Client Login

                </h2>





                <form onSubmit={handleSubmit}>


                    <input


                        type="email"


                        name="email"


                        placeholder="Email Address"


                        value={
                            formData.email
                        }


                        onChange={handleChange}


                    />





                    <input


                        type="password"


                        name="password"


                        placeholder="Password"


                        value={
                            formData.password
                        }


                        onChange={handleChange}


                    />





                    <button

                        type="submit"

                        disabled={loading}

                    >


                    {

                    loading

                    ?

                    "Logging in..."

                    :

                    "Login"

                    }


                    </button>



                </form>






                <p>


                    Don't have an account?


                    <span

                    onClick={()=>navigate("/register")}

                    >

                    Register

                    </span>


                </p>






                {

                message &&

                <div className="message">

                    {message}

                </div>

                }



            </div>


        </div>


    );

}


export default Login;