class Error(Exception):
    pass
class UnauthorizedError(Error):
    pass

errors={
         "UnauthorizedError": {
         "message": "Invalid username or password",
         "status": 401
     },
}