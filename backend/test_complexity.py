from app.agents.complexity_prediction import predict_complexity



requirement = """

Food delivery application.

Features:
- User login
- Restaurant listing
- Cart
- Payment gateway
- Live tracking
- Admin dashboard

Technology:
React and Node.js

"""


result = predict_complexity(
    requirement
)


print(result)