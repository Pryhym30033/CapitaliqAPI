class TokenResponse:
    def __init__(self, token_type, refresh_token, access_token, scope, expires_in_seconds, error, error_description):
        self.token_type = token_type
        self.refresh_token = refresh_token
        self.access_token = access_token
        self.scope = scope
        self.expires_in_seconds = expires_in_seconds
        self.error=error
        self.error_description=error_description

    @staticmethod
    def from_json(json_data):
        return TokenResponse(
            json_data.get('token_type'),
            json_data.get('refresh_token'),
            json_data.get('access_token'),
            json_data.get('scope'),
            json_data.get('expires_in_seconds'),
            json_data.get('error'),
            json_data.get('error_description')
        )
