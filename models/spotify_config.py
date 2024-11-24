from odoo import models, fields, api
import requests
import base64

class SpotifyConfig(models.Model):
    _name = 'spotify.config'
    _description = 'Spotify Configuration'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    client_id = fields.Char(string='Client ID', required=True)
    client_secret = fields.Char(string='Client Secret', required=True)
    access_token = fields.Char(string='Access Token')
    refresh_token = fields.Char(string='Refresh Token')

    @api.model
    def get_spotify_auth(self):
        config = self.search([], limit=1)
        if not config:
            return False
            
        if not config.access_token:
            
            auth_header = base64.b64encode(
                f"{config.client_id}:{config.client_secret}".encode()
            ).decode()
            
            response = requests.post(
                'https://accounts.spotify.com/api/token',
                headers={'Authorization': f'Basic {auth_header}'},
                data={'grant_type': 'client_credentials'}
            )
            
            if response.status_code == 200:
                config.write({
                    'access_token': response.json()['access_token']
                })
                
        return config.access_token