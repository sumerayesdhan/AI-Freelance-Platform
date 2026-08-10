import json

from app.services.groq_service import generate_response





def clean_json_response(response):


    cleaned = response.strip()


    cleaned = (
        cleaned
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )


    return cleaned






def understand_requirement(
    conversation
):


    # -----------------------------
    # Convert conversation
    # -----------------------------


    conversation_text = ""


    for msg in conversation:


        conversation_text += (

            str(msg.get("role"))

            + ": "

            + str(msg.get("content"))

            + "\n"

        )




    prompt = f"""

You are an expert software requirement analyst.


Analyze the following client conversation.


Your task:

Convert the conversation into a structured
software requirement document.



Conversation:

{conversation_text}



Extract ONLY these fields:



1. project_domain

Example:

Education, Healthcare, E-commerce



2. project_type

Example:

Web Application,
Mobile Application,
AI Application



3. target_users

Return list.



4. features

Return complete list of requested features.



5. technology_preference

If client mentioned technology,
extract it.

If client does not know,
return:

"I don't know - recommend technology"



6. platform

Example:

Web,
Mobile,
Both



7. deadline

Extract only if client mentioned.

Otherwise null.



8. budget_range

Extract only the client's budget.

Do not estimate.



9. additional_requirements

Include:

- security
- scalability
- accessibility
- performance
- integrations



IMPORTANT:

Return ONLY valid JSON.

No markdown.

No explanation.



JSON FORMAT:



{{
"project_domain":"",
"project_type":"",
"target_users":[],
"features":[],
"technology_preference":null,
"platform":"",
"deadline":null,
"budget_range":null,
"additional_requirements":[]
}}

"""



    response = generate_response(

        [

            {
                "role":"user",

                "content":prompt

            }

        ]

    )




    try:


        cleaned_response = clean_json_response(
            response
        )


        result = json.loads(
            cleaned_response
        )



        # Normalize fields


        result.setdefault(
            "target_users",
            []
        )


        result.setdefault(
            "features",
            []
        )


        result.setdefault(
            "additional_requirements",
            []
        )


        return result




    except Exception:


        return {


            "error":
            "Invalid JSON generated",


            "raw_response":
            response

        }