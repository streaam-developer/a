# Instagram Bot - Advanced Automation Script

A powerful Instagram automation tool built with Python using the `instagrapi` library. This script provides comprehensive functionality for managing your Instagram account, including posting reels, photos, videos, and performing various engagement actions.

## Features

- 🔐 **Secure Login** - Login with session persistence and 2FA support
- 🎬 **Post Reels** - Upload and post Instagram Reels
- 📷 **Post Photos** - Upload single or multiple photos
- 🎥 **Post Videos** - Upload videos with custom thumbnails
- 📚 **Post Albums** - Create albums with multiple media files
- 👥 **Follow/Unfollow** - Manage followers
- 👍 **Like & Comment** - Engage with other posts
- 📊 **Account Info** - View account statistics
- ⚙️ **Configurable** - Easy configuration via JSON
- 🔄 **Session Management** - Automatic session saving/loading
- 🛡️ **Error Handling** - Robust retry mechanisms

## Installation

1. Install Python 3.8 or higher
2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Edit `config.json` with your Instagram credentials:
```json
{
    "username": "your_username",
    "password": "your_password",
    "session_file": "session.json",
    "proxy": null,
    "delay_range": [2, 5],
    "max_retries": 3
}
```

## Usage

### Login to Instagram
```bash
python instagram_bot.py login
python instagram_bot.py login -u username -p password
```

### Post a Reel
```bash
python instagram_bot.py post-reel -v video.mp4 -c "Your caption here"
python instagram_bot.py post-reel -v video.mp4 -c "Caption" -t thumbnail.jpg
```

### Post a Photo
```bash
python instagram_bot.py post-photo -p photo.jpg -c "Your caption"
```

### Post a Video
```bash
python instagram_bot.py post-video -v video.mp4 -c "Your caption"
```

### Post an Album
```bash
python instagram_bot.py post-album -m photo1.jpg photo2.jpg photo3.jpg -c "Album caption"
```

### Get Account Info
```bash
python instagram_bot.py info
```

### Follow a User
```bash
python instagram_bot.py follow -u username
```

### Unfollow a User
```bash
python instagram_bot.py unfollow -u username
```

### Logout
```bash
python instagram_bot.py logout
```

## Programmatic Usage

You can also use the bot programmatically in your Python code:

```python
from instagram_bot import InstagramBot

# Initialize bot
bot = InstagramBot()

# Login
if bot.login("username", "password"):
    # Get account info
    info = bot.get_user_info()
    print(f"Logged in as: {info['username']}")
    
    # Post a reel
    bot.post_reel("video.mp4", "My awesome reel!")
    
    # Post a photo
    bot.post_photo("photo.jpg", "Check this out!")
    
    # Follow a user
    bot.follow_user("target_username")
    
    # Logout when done
    bot.logout()
```

## Important Notes

1. **Two-Factor Authentication**: If 2FA is enabled, the script will prompt you to enter the code
2. **Session Persistence**: After first login, sessions are saved for automatic re-authentication
3. **Rate Limiting**: The script includes delays to avoid Instagram rate limits
4. **Proxy Support**: Configure proxy in `config.json` if needed

## File Structure

```
.
├── instagram_bot.py      # Main bot script
├── config.json          # Configuration file
├── session.json         # Saved session (auto-generated)
├── requirements.txt     # Python dependencies
├── instagram_bot.log    # Log file (auto-generated)
├── posted_media.json    # Posted media metadata
└── README.md           # This file
```

## Disclaimer

This tool is for educational purposes. Please comply with Instagram's Terms of Service and use responsibly. Automated actions may violate Instagram's policies and result in account restrictions.
