import dash
#from flask import Flask
#from flask_caching import Cache
# start Dash web server
app = dash.Dash(__name__, title='SW', suppress_callback_exceptions=True,update_title='BUSY...')
#print(app.config)
#print(app.config.keys())
server = app.server

#CACHE_CONFIG = { "CACHE_TYPE": "filesystem", "CACHE_DEFAULT_TIMEOUT": 300, "CACHE_DIR": "cache" } # 'filesystem'
#cache = Cache()
#cache.init_app(app.server, config = CACHE_CONFIG)
