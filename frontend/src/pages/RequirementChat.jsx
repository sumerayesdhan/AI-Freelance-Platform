import {
    useEffect,
    useRef,
    useState
} from "react";


import {
    useNavigate
} from "react-router-dom";


import api from "../services/api";


import "../styles/chat.css";



function RequirementChat({

    projectId,

    initialDescription

}) {


    const navigate = useNavigate();



    const [messages,setMessages] = useState([]);


    const [input,setInput] = useState("");


    const [loading,setLoading] = useState(false);



    const chatEndRef = useRef(null);





    // Auto scroll

    useEffect(()=>{


        chatEndRef.current?.scrollIntoView({

            behavior:"smooth"

        });


    },[messages]);







    // Detect requirement completion

    const checkCompletion = (response)=>{


        if(

            response

            .toUpperCase()

            .includes(

                "REQUIREMENT_COMPLETE"

            )

        ){


            navigate(

                `/requirement-summary/${projectId}`

            );


        }


    };









    // Start conversation automatically

    useEffect(()=>{


        if(initialDescription){


            startConversation();


        }


    },[]);









    const startConversation = async()=>{


        try{


            setLoading(true);



            const response = await api.post(

                "/conversation/message",

                {


                    project_id: projectId,


                    message: initialDescription


                }


            );





            setMessages([


                {


                    role:"user",


                    content:initialDescription


                },


                {


                    role:"assistant",


                    content:
                    response.data.response


                }


            ]);





            checkCompletion(

                response.data.response

            );



        }


        catch(error){


            console.log(error);


        }


        finally{


            setLoading(false);


        }


    };









    const sendMessage = async()=>{


        if(!input.trim())

            return;





        const userText = input;



        setInput("");






        setMessages(prev=>[


            ...prev,


            {


                role:"user",


                content:userText


            }


        ]);







        try{


            setLoading(true);





            const response = await api.post(


                "/conversation/message",

                {


                    project_id:projectId,


                    message:userText


                }


            );








            setMessages(prev=>[


                ...prev,


                {


                    role:"assistant",


                    content:
                    response.data.response


                }


            ]);







            checkCompletion(

                response.data.response

            );





        }


        catch(error){


            console.log(error);


        }


        finally{


            setLoading(false);


        }



    };









    const handleKeyDown=(e)=>{


        if(e.key==="Enter"){


            sendMessage();


        }


    };









    return(


        <div className="chat-container">





            <h2>

                AI Requirement Assistant

            </h2>









            <div className="chat-box">





            {

            messages.map((msg,index)=>(



                <div


                key={index}


                className={

                    msg.role==="user"

                    ?

                    "user-message"

                    :

                    "ai-message"

                }


                >




                    <strong>


                    {

                    msg.role==="user"

                    ?

                    "You"

                    :

                    "AI"

                    }


                    </strong>




                    <p>

                    {msg.content}

                    </p>





                </div>



            ))


            }







            {

            loading &&


            <div className="ai-message">


                AI is thinking...


            </div>


            }






            <div ref={chatEndRef}/>



            </div>









            <div className="chat-input">





                <input



                    value={input}



                    onChange={

                        e=>

                        setInput(

                            e.target.value

                        )

                    }



                    onKeyDown={handleKeyDown}



                    placeholder="Answer AI question..."



                />







                <button


                    onClick={sendMessage}


                    disabled={loading}


                >


                    Send


                </button>





            </div>






        </div>


    );


}



export default RequirementChat;