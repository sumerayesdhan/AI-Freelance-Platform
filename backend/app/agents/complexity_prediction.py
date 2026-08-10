import json

from app.services.groq_service import generate_response





def clean_json_response(response):


    cleaned = (

        response

        .replace("```json", "")

        .replace("```", "")

        .strip()

    )


    return cleaned






def predict_complexity(requirement):


    requirement_text = json.dumps(

        requirement,

        indent=2

    )




    prompt = f"""

You are a senior software architect
and project estimation expert.



Analyze the software requirement below.



Requirement:

{requirement_text}



Predict:



1. complexity_level

Choose only:

- Low

- Medium

- High



Consider:

- Number of features

- Number of user roles

- Integrations

- Security requirements

- Scalability requirements

- Technical uncertainty





2. estimated_duration


Choose realistic software development duration:

- 1-3 months

- 3-6 months

- 6-12 months

- 12+ months




3. risk_level


Choose:

- Low

- Medium

- High



Consider:

- Requirement clarity

- Technical challenges

- External integrations

- Deadline pressure





Return ONLY valid JSON.

No markdown.

No explanation.



Format:



{{
"complexity_level":"",
"estimated_duration":"",
"risk_level":"",
"reason":"",
"technical_factors":[]
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


        return json.loads(

            cleaned_response

        )



    except Exception:


        return {


            "error":
            "Invalid JSON",


            "raw":
            response

        }