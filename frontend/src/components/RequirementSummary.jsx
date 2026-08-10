import "../styles/analysis.css";


function RequirementSummary({data}){


    if(!data)

        return null;





    return(


        <div className="summary-card">



            <h2>

                Requirement Analysis

            </h2>





            <div className="summary-item">

                <h3>
                    Project Domain
                </h3>

                <p>
                    {data.project_domain}
                </p>

            </div>






            <div className="summary-item">

                <h3>
                    Project Type
                </h3>

                <p>
                    {data.project_type}
                </p>

            </div>






            <div className="summary-item">

                <h3>
                    Platform
                </h3>

                <p>
                    {data.platform}
                </p>

            </div>







            <div className="summary-item">


                <h3>
                    Target Users
                </h3>



                <ul>


                {

                data.target_users?.map(

                    (user,index)=>(

                        <li key={index}>

                            {user}

                        </li>

                    )

                )

                }


                </ul>


            </div>







            <div className="summary-item">


                <h3>
                    Features
                </h3>


                <ul>


                {

                data.features?.map(

                    (feature,index)=>(

                        <li key={index}>

                            {feature}

                        </li>

                    )

                )

                }


                </ul>


            </div>







            <div className="summary-item">


                <h3>
                    Technology Preference
                </h3>


                <p>

                {

                data.technology_preference ||

                "AI Recommended"

                }

                </p>


            </div>





        </div>


    );

}



export default RequirementSummary;