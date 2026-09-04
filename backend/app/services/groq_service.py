from groq import Groq
from dotenv import load_dotenv
import os



load_dotenv()



GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)



if not GROQ_API_KEY:

    raise Exception(
        "GROQ_API_KEY missing in .env"
    )




client = Groq(

    api_key=GROQ_API_KEY

)





def generate_response(
    messages
):


    try:


        # Allow simple string prompts

        if isinstance(
            messages,
            str
        ):

            messages = [

                {
                    "role":"user",

                    "content":messages

                }

            ]




        response = client.chat.completions.create(

            model=
            "openai/gpt-oss-120b",


            messages=messages,


            temperature=0.2,


        )



        content = (
            response
            .choices[0]
            .message
            .content
        )


        return content





    except Exception as e:


        print(
            "Groq API Error:",
            e
        )


        return {

            "error":
            "Groq API failed",

            "details":
            str(e)

        }