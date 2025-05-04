# Cache for voice states and created channels
voice_state_cache = {}  # {user_id: channel_id}
created_channels = {}  # {channel_id: user_id}
locked_channels = set()  # list of channel IDs
