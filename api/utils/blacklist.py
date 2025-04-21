token_blacklist = set()

def is_token_revoked(jwt_header, jwt_payload):
    return jwt_payload['jti'] in token_blacklist
