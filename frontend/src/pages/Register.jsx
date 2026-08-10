import { useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";

import "../styles/auth.css";



function Register(){


    const navigate = useNavigate();



    const [formData,setFormData] = useState({

        full_name:"",
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

            !formData.full_name ||

            !formData.email ||

            !formData.password

        ){

            setMessage(
                "Please fill all fields"
            );

            return;

        }



        if(formData.password.length < 8){


            setMessage(
                "Password must contain minimum 8 characters"
            );


            return;

        }





        try{


            setLoading(true);



            const response = await api.post(

                "/auth/register",

                formData

            );



            setMessage(

                response.data.message

            );



            setTimeout(()=>{


                navigate("/login");


            },1000);



        }


        catch(error){


            setMessage(

                error.response?.data?.detail ||

                "Registration failed"

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

                    Create Account

                </h2>





                <form onSubmit={handleSubmit}>


                    <input

                        type="text"

                        name="full_name"

                        placeholder="Full Name"

                        value={
                            formData.full_name
                        }

                        onChange={handleChange}

                    />





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

                    "Creating Account..."

                    :

                    "Register"

                    }


                    </button>



                </form>





                <p>

                    Already have an account?


                    <span

                    onClick={()=>navigate("/login")}

                    >

                    Login

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


export default Register;