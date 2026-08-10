from app.services.groq_services import generate_response


response = generate_response(
    "Explain software complexity in one sentence"
)


print(response)