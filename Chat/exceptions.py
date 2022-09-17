import json


class ClientError(Exception):

    def __init__(self, code, message=None):
        super().__init__(code,message)
        self.code = code
        if message:
            self.message = message

    def get_full_details(self):
        return (self.code,self.message)
