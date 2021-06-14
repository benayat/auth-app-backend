# auth-app-backend
In this backend project I decided to deep dive into JWT authentication in python-flask.

some of the challenges I faced - 
* where is it best to store the tokens? in client-side, and server.
* general auth for protected urls, and identity based auth.
* security considerations about implementation.

Some of the packages I used - flask-jwt-extende.

implementation decisions - I decided to use httponly cookies for the jwt access token, combined with csrf tokens, which will be sent back as a header - that's the best and most secure way I could find.

