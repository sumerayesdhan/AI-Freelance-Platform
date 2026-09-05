import { useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";

import "../styles/auth.css";


function FreelancerRegister() {

    const navigate = useNavigate();


    const [formData, setFormData] = useState({

        freelancer_id: "",
        full_name: "",
        email: "",
        password: "",
        title: "",
        skills: "",
        hourly_rate: "",
        country: ""

    });


    const [message, setMessage] = useState("");

    const [loading, setLoading] = useState(false);


    // ========================================================
    // HANDLE INPUT
    // ========================================================

    const handleChange = (e) => {

        setFormData({

            ...formData,

            [e.target.name]: e.target.value

        });

    };


    // ========================================================
    // REGISTER FREELANCER
    // ========================================================

    const handleSubmit = async (e) => {

        e.preventDefault();


        if (
            !formData.freelancer_id ||
            !formData.full_name ||
            !formData.email ||
            !formData.password
        ) {

            setMessage(
                "Please fill all required fields"
            );

            return;

        }


        if (formData.password.length < 8) {

            setMessage(
                "Password must contain minimum 8 characters"
            );

            return;

        }


        try {

            setLoading(true);

            setMessage("");


            const response = await api.post(

                "/freelancer/register",

                {

                    freelancer_id:
                        Number(formData.freelancer_id),

                    full_name:
                        formData.full_name,

                    email:
                        formData.email,

                    password:
                        formData.password,

                    title:
                        formData.title,

                    skills:
                        formData.skills,

                    hourly_rate:
                        formData.hourly_rate
                            ? Number(formData.hourly_rate)
                            : 0,

                    country:
                        formData.country

                }

            );


            setMessage(
                response.data.message
            );


            // Save freelancer information
            localStorage.setItem(
                "freelancer_id",
                response.data.freelancer_id
            );


            localStorage.setItem(
                "freelancer_name",
                response.data.name
            );


            // Go to freelancer dashboard

            setTimeout(() => {

                navigate(
                    `/freelancer-dashboard/${response.data.freelancer_id}`
                );

            }, 1000);


        }

        catch (error) {

            setMessage(

                error.response?.data?.detail ||

                "Freelancer registration failed"

            );

        }

        finally {

            setLoading(false);

        }

    };


    return (

        <div className="auth-container">

            <div className="auth-card">


                <h1>

                    AI Freelance Platform

                </h1>


                <h2>

                    Freelancer Registration

                </h2>


                <form onSubmit={handleSubmit}>


                    {/* Freelancer ID */}

                    <input

                        type="number"

                        name="freelancer_id"

                        placeholder="Freelancer ID (Example: 13)"

                        value={
                            formData.freelancer_id
                        }

                        onChange={handleChange}

                    />


                    {/* Full Name */}

                    <input

                        type="text"

                        name="full_name"

                        placeholder="Full Name"

                        value={
                            formData.full_name
                        }

                        onChange={handleChange}

                    />


                    {/* Email */}

                    <input

                        type="email"

                        name="email"

                        placeholder="Email Address"

                        value={
                            formData.email
                        }

                        onChange={handleChange}

                    />


                    {/* Password */}

                    <input

                        type="password"

                        name="password"

                        placeholder="Password"

                        value={
                            formData.password
                        }

                        onChange={handleChange}

                    />


                    {/* Professional Title */}

                    <input

                        type="text"

                        name="title"

                        placeholder="Professional Title"

                        value={
                            formData.title
                        }

                        onChange={handleChange}

                    />


                    {/* Skills */}

                    <input

                        type="text"

                        name="skills"

                        placeholder="Skills (Python, React, ML...)"

                        value={
                            formData.skills
                        }

                        onChange={handleChange}

                    />


                    {/* Hourly Rate */}

                    <input

                        type="number"

                        name="hourly_rate"

                        placeholder="Hourly Rate ($)"

                        value={
                            formData.hourly_rate
                        }

                        onChange={handleChange}

                    />


                    {/* Country */}

                    <input

                        type="text"

                        name="country"

                        placeholder="Country"

                        value={
                            formData.country
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

                                "Register as Freelancer"

                        }

                    </button>


                </form>


                <p>

                    Are you a client?

                    <span

                        onClick={() =>
                            navigate("/register")
                        }

                    >

                        Register as Client

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


export default FreelancerRegister;