import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";


function FreelancerLogin() {

    const navigate = useNavigate();

    const [email, setEmail] = useState("");

    const [password, setPassword] = useState("");

    const [error, setError] = useState("");

    const [loading, setLoading] = useState(false);


    const handleLogin = async (e) => {

        e.preventDefault();

        setError("");

        setLoading(true);


        try {

            const response = await api.post(
                "/freelancer/login",
                {
                    email: email,
                    password: password
                }
            );


            // Store freelancer token separately
            localStorage.setItem(
                "freelancer_token",
                response.data.access_token
            );


            // Store freelancer information
            localStorage.setItem(
                "freelancer",
                JSON.stringify(
                    response.data.user
                )
            );


            // Store freelancer ID
            localStorage.setItem(
                "freelancer_id",
                response.data.user.freelancer_id
            );


            // Go to freelancer dashboard
            navigate(
                `/freelancer-dashboard/${response.data.user.freelancer_id}`
            );

        }

        catch (error) {

            console.error(
                "Freelancer login error:",
                error
            );


            setError(
                error.response?.data?.detail ||
                "Login failed. Please check your email and password."
            );

        }

        finally {

            setLoading(false);

        }

    };


    return (

        <div className="login-container">

            <div className="login-box">

                <h2>
                    Freelancer Login
                </h2>


                <p>
                    Login to view your negotiation requests
                </p>


                <form onSubmit={handleLogin}>

                    <div>

                        <label>
                            Email
                        </label>

                        <input
                            type="email"
                            placeholder="freelancer13@example.com"
                            value={email}
                            onChange={(e) =>
                                setEmail(e.target.value)
                            }
                            required
                        />

                    </div>


                    <div>

                        <label>
                            Password
                        </label>

                        <input
                            type="password"
                            placeholder="123456"
                            value={password}
                            onChange={(e) =>
                                setPassword(e.target.value)
                            }
                            required
                        />

                    </div>


                    {error && (

                        <p style={{ color: "red" }}>
                            {error}
                        </p>

                    )}


                    <button
                        type="submit"
                        disabled={loading}
                    >

                        {loading
                            ? "Logging in..."
                            : "Login"
                        }

                    </button>

                </form>

            </div>

        </div>

    );

}


export default FreelancerLogin;