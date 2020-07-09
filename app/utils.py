import json,random,string, datetime


class Response:
    def __init__(self):
        self.success = True
        self.status = 200
        self.data = ''
        self.errors = ''
        self.message = ''

    def response_json(self):
        return json.loads(json.dumps(self, default=lambda o: o.__dict__,indent=2))


def randon_hash_string():
    return hex(random.getrandbits(128))


def password_generator():
    return ''.join(random.choice(string.ascii_uppercase+ string.ascii_lowercase + string.digits) for _ in range(8))


# method to return current date
def get_cur_date():
    return str(datetime.datetime.now().date())