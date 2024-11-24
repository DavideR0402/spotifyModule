from odoo import models, fields, api
import requests
import logging

_logger = logging.getLogger(__name__)

class SpotifyPlaylist(models.Model):
    _name = 'spotify.playlist'
    _description = 'Spotify Playlist'

    name = fields.Char(string='Name', required=True)
    spotify_id = fields.Char(string='Spotify ID', required=True)
    track_count = fields.Integer(string='Track Count')
    track_ids = fields.One2many('spotify.track', 'playlist_id', string='Tracks')
    description = fields.Text(string='Description')
    image_url = fields.Char(string='Image URL')
    
    playlist_count = fields.Integer(compute='_compute_dashboard_data')
    total_tracks = fields.Integer(compute='_compute_dashboard_data')
    dashboard_playlist_ids = fields.Many2many('spotify.playlist', compute='_compute_dashboard_data')
    recent_track_ids = fields.Many2many('spotify.track', compute='_compute_dashboard_data')

    @api.depends()
    def _compute_dashboard_data(self):
        for record in self:
            record.playlist_count = self.search_count([])
            record.total_tracks = self.env['spotify.track'].search_count([])
            record.dashboard_playlist_ids = self.search([])
            record.recent_track_ids = self.env['spotify.track'].search(
                [], order='create_date desc', limit=10
            )

    def action_sync_tracks(self):
        self.ensure_one()
        SpotifyTrack = self.env['spotify.track']
        access_token = self.env['spotify.config'].get_spotify_auth()
        
        if not access_token:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': 'Please configure Spotify credentials',
                    'type': 'danger',
                }
            }
            
        try:
            self.track_ids.unlink()
            
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(
                f'https://api.spotify.com/v1/playlists/{self.spotify_id}/tracks',
                headers=headers
            )
            
            response.raise_for_status()
            tracks = response.json().get('items', [])
            
            for track in tracks:
                if not track.get('track'):
                    continue
                    
                track_data = track['track']
                SpotifyTrack.create({
                    'name': track_data.get('name', 'Unknown'),
                    'artist': track_data['artists'][0]['name'] if track_data.get('artists') else 'Unknown',
                    'spotify_id': track_data.get('id', ''),
                    'playlist_id': self.id,
                })
            
            self.track_count = len(tracks)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': f'Successfully synced {len(tracks)} tracks',
                    'type': 'success',
                }
            }
            
        except requests.exceptions.RequestException as e:
            _logger.error('Error syncing tracks: %s', str(e))
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': 'Failed to sync tracks. Please try again.',
                    'type': 'danger',
                }
            }

    @api.model
    def action_sync_playlists(self):
        access_token = self.env['spotify.config'].get_spotify_auth()
        
        if not access_token:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': 'Please configure Spotify credentials',
                    'type': 'danger',
                }
            }
        
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.get(
                'https://api.spotify.com/v1/me/playlists',
                headers=headers
            )
            
            if response.status_code in (401, 403):
                response = requests.get(
                    'https://api.spotify.com/v1/browse/featured-playlists',
                    headers=headers
                )
                playlists_data = response.json().get('playlists', {}).get('items', [])
            else:
                response.raise_for_status()
                playlists_data = response.json().get('items', [])
            
            created_count = 0
            updated_count = 0
            
            for playlist in playlists_data:
                if not playlist.get('name'):
                    continue
                    
                existing = self.search([('spotify_id', '=', playlist['id'])])
                vals = {
                    'name': playlist['name'],
                    'spotify_id': playlist['id'],
                    'description': playlist.get('description', ''),
                    'track_count': playlist.get('tracks', {}).get('total', 0),
                    'image_url': playlist['images'][0]['url'] if playlist.get('images') else False,
                }
                
                if existing:
                    existing.write(vals)
                    updated_count += 1
                else:
                    self.create(vals)
                    created_count += 1
            
            message = f'Synchronized playlists: {created_count} created, {updated_count} updated'
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': message,
                    'type': 'success',
                }
            }
            
        except requests.exceptions.RequestException as e:
            _logger.error('Error syncing playlists: %s', str(e))
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': 'Failed to sync playlists. Please try again.',
                    'type': 'danger',
                }
            }