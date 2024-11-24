{
    'name': 'Spotify',
    'version': '1.0.0',
    'category': 'Tools, Music',
    'summary': 'Integration Spotify with Odoo to fetch playlists',
    'sequence': 1,
    'author': 'Luis Castaño',
    'description': """
        This module allows you to:
        * Configure Spotify API credentials
        * Sync playlists from your Spotify account
        * View and manage playlist tracks
    """,
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/spotify_config_views.xml',
        'views/spotify_playlist_views.xml',
        'views/spotify_dashboard_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'external_dependencies': {
        'python': ['requests'],
    },
}