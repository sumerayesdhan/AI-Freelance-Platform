from fastapi import Depends, HTTPException, status

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from jose import jwt, JWTError

from dotenv import load_dotenv

import os



load_dotenv()



SECRET_KEY = os.getenv(
    "SECRET_KEY"
)


ALGORITHM = os.getenv(
    "ALGORITHM",
    "HS256"
)



if not SECRET_KEY:

    raise Exception(
        "SECRET_KEY missing in .env"
    )



security = HTTPBearer()






def get_current_user(

    credentials: HTTPAuthorizationCredentials = Depends(security)

):


    token = credentials.credentials



    try:


        payload = jwt.decode(

            token,

            SECRET_KEY,

            algorithms=[ALGORITHM]

        )



        email = payload.get(
            "sub"
        )



        if not email:


            raise HTTPException(

                status_code=status.HTTP_401_UNAUTHORIZED,

                detail="Invalid token"

            )



        return email




    except JWTError:


        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail="Invalid or expired token"

        )