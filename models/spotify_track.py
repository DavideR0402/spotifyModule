from odoo import models, fields

class SpotifyTrack(models.Model):
    
    _name = 'spotify.track'
    _description = 'Spotify Track'

    name = fields.Char(string='Name', required=True)
    artist = fields.Char(string='Artist')
    spotify_id = fields.Char(string='Spotify ID', required=True)
    playlist_id = fields.Many2one('spotify.playlist', string='Playlist')