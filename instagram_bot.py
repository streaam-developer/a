#!/usr/bin/env python3
"""
Instagram Automation Script using instagrapi
Advanced script for posting reels and managing Instagram account

Author: Instagram Bot
Version: 1.0.0
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import random

# Instagrapi imports
try:
    from instagrapi import Client
    from instagrapi.exceptions import (
        LoginRequired, 
        TwoFactorRequired, 
        ChallengeRequired,
        ClientError,
        MediaError
    )
except ImportError:
    print("Error: instagrapi not installed. Install it with: pip install instagrapi")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instagram_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class InstagramBot:
    """Advanced Instagram Bot for automation tasks"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.client = Client()
        self.session_path = "session.json"
        self.config = self.load_config()
        self.setup_client()
    
    def load_config(self) -> Dict:
        """Load configuration from JSON file"""
        default_config = {
            "username": "",
            "password": "",
            "session_file": "session.json",
            "proxy": None,
            "delay_range": [2, 5],
            "max_retries": 3,
            "accounts": []
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    logger.info(f"Loaded configuration from {self.config_path}")
                    return {**default_config, **config}
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                return default_config
        else:
            self.save_config(default_config)
            logger.info(f"Created default configuration at {self.config_path}")
            logger.warning("Please edit config.json with your Instagram credentials!")
            return default_config
    
    def save_config(self, config: Dict):
        """Save configuration to JSON file"""
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=4)
    
    def setup_client(self):
        """Setup Instagram client settings"""
        # Set custom user agent - use a more common one
        self.client.set_user_agent(
            "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        )
        
        # Configure delay settings
        self.client.delay_range = self.config.get("delay_range", [2, 5])
        
        # Set proxy if configured
        if self.config.get("proxy"):
            self.client.set_proxy(self.config.get("proxy"))
            logger.info("Proxy configured")
        
        # Load session if exists
        if os.path.exists(self.session_path):
            try:
                self.client.load_settings(self.session_path)
                logger.info("Loaded existing session")
            except Exception as e:
                logger.warning(f"Could not load session: {e}")
                # Remove corrupted session file
                try:
                    os.remove(self.session_path)
                except:
                    pass
    
    def login(self, username: str = None, password: str = None) -> bool:
        """
        Login to Instagram account
        
        Args:
            username: Instagram username
            password: Instagram password
            
        Returns:
            bool: Login success status
        """
        username = username or self.config.get("username")
        password = password or self.config.get("password")
        
        if not username or not password:
            logger.error("Username and password are required!")
            return False
        
        # Delete any old session file to start fresh
        if os.path.exists(self.session_path):
            try:
                os.remove(self.session_path)
                logger.info("Removed old session file")
            except:
                pass
        
        # Create fresh client
        logger.info("Creating fresh client...")
        self.client = Client()
        self.setup_client()
        
        # Try pre-login to get CSRF token
        logger.info("Getting pre-login session...")
        try:
            # Initialize session by making a simple request first
            self.client.session.headers.update({
                "X-IG-Capabilities": "3rTBrJ4AAA==",
                "X-IG-Connection-Type": "WIFI"
            })
        except Exception as e:
            logger.debug(f"Pre-login step: {e}")
        
        # Perform fresh login
        logger.info(f"Attempting fresh login for user: {username}")
        
        for attempt in range(self.config.get("max_retries", 3)):
            try:
                # Add a small delay before login to allow CSRF token to be fetched
                import time
                time.sleep(random.uniform(2, 5))
                
                if self.client.login(username, password):
                    logger.info("Successfully logged in!")
                    self.save_session()
                    return True
                    
            except TwoFactorRequired:
                logger.error("Two-factor authentication required!")
                two_factor_code = input("Enter 2FA code: ")
                try:
                    if self.client.login(username, password, two_factor_code):
                        logger.info("Successfully logged in with 2FA!")
                        self.save_session()
                        return True
                except Exception as e:
                    logger.error(f"2FA login failed: {e}")
                    
            except ChallengeRequired:
                logger.warning("Challenge required - please verify your account manually")
                # Handle challenge if possible
                try:
                    self.client.challenge_resolve(self.client.last_json)
                    logger.info("Challenge resolved")
                except Exception as e:
                    logger.error(f"Challenge resolution failed: {e}")
                    
            except LoginRequired:
                logger.error("Login required - check credentials")
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Login attempt {attempt + 1} failed: {error_msg}")
                
                # If CSRF error, create new client and retry
                if "CSRF" in error_msg or "403" in error_msg or "fail" in error_msg:
                    logger.info("Session error detected, recreating client...")
                    self.client = Client()
                    self.setup_client()
            
            # Wait before retry
            if attempt < self.config.get("max_retries", 3) - 1:
                wait_time = random.randint(15, 45)
                logger.info(f"Waiting {wait_time} seconds before retry...")
                import time
                time.sleep(wait_time)
        
        logger.error("Login failed after all attempts")
        return False
    
    def save_session(self):
        """Save current session to file"""
        try:
            self.client.dump_settings(self.session_path)
            logger.info("Session saved successfully")
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
    
    def logout(self):
        """Logout from Instagram"""
        try:
            self.client.logout()
            logger.info("Logged out successfully")
            if os.path.exists(self.session_path):
                os.remove(self.session_path)
                logger.info("Session file removed")
        except Exception as e:
            logger.error(f"Logout failed: {e}")
    
    def get_user_info(self) -> Optional[Dict]:
        """Get current user information"""
        try:
            user_id = self.client.user_id
            info = self.client.user_info(user_id)
            logger.info(f"Logged in as: {info.username}")
            return {
                "username": info.username,
                "full_name": info.full_name,
                "followers": info.follower_count,
                "following": info.following_count,
                "media_count": info.media_count
            }
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return None
    
    def post_reel(
        self, 
        video_path: str, 
        caption: str = "",
        thumbnail_path: str = None,
        extra_data: Dict = None
    ) -> bool:
        """
        Post a reel to Instagram
        
        Args:
            video_path: Path to video file
            caption: Caption for the reel
            thumbnail_path: Path to custom thumbnail
            extra_data: Additional metadata
            
        Returns:
            bool: Post success status
        """
        # Validate video file
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return False
        
        video_path = os.path.abspath(video_path)
        logger.info(f"Preparing to post reel: {video_path}")
        
        # Prepare media configuration
        media_data = {
            "path": video_path,
            "caption": caption,
            "thumbnail": thumbnail_path
        }
        
        # Add extra data if provided
        if extra_data:
            media_data.update(extra_data)
        
        # Attempt to post
        for attempt in range(self.config.get("max_retries", 3)):
            try:
                media = self.client.clip_upload(
                    media_data["path"],
                    caption=media_data["caption"],
                    thumbnail=media_data.get("thumbnail")
                )
                
                if media:
                    logger.info(f"Reel posted successfully! Media ID: {media.pk}")
                    self.save_post_metadata(media)
                    return True
                    
            except MediaError as e:
                logger.error(f"Media error: {e}")
                
            except ClientError as e:
                logger.error(f"Client error: {e}")
                
            except Exception as e:
                logger.error(f"Failed to post reel (attempt {attempt + 1}): {e}")
            
            # Wait before retry
            if attempt < self.config.get("max_retries", 3) - 1:
                wait_time = random.randint(10, 30)
                logger.info(f"Waiting {wait_time} seconds before retry...")
                import time
                time.sleep(wait_time)
        
        logger.error("Failed to post reel after all attempts")
        return False
    
    def post_photo(
        self, 
        photo_path: str, 
        caption: str = "",
        extra_data: Dict = None
    ) -> bool:
        """
        Post a photo to Instagram
        
        Args:
            photo_path: Path to photo file
            caption: Caption for the photo
            extra_data: Additional metadata
            
        Returns:
            bool: Post success status
        """
        if not os.path.exists(photo_path):
            logger.error(f"Photo file not found: {photo_path}")
            return False
        
        photo_path = os.path.abspath(photo_path)
        logger.info(f"Preparing to post photo: {photo_path}")
        
        try:
            media = self.client.photo_upload(
                photo_path,
                caption=caption
            )
            
            if media:
                logger.info(f"Photo posted successfully! Media ID: {media.pk}")
                self.save_post_metadata(media)
                return True
                
        except Exception as e:
            logger.error(f"Failed to post photo: {e}")
            return False
        
        return False
    
    def post_video(
        self, 
        video_path: str, 
        caption: str = "",
        thumbnail_path: str = None,
        extra_data: Dict = None
    ) -> bool:
        """
        Post a video to Instagram
        
        Args:
            video_path: Path to video file
            caption: Caption for the video
            thumbnail_path: Path to custom thumbnail
            extra_data: Additional metadata
            
        Returns:
            bool: Post success status
        """
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return False
        
        video_path = os.path.abspath(video_path)
        
        try:
            media = self.client.video_upload(
                video_path,
                caption=caption,
                thumbnail=thumbnail_path
            )
            
            if media:
                logger.info(f"Video posted successfully! Media ID: {media.pk}")
                self.save_post_metadata(media)
                return True
                
        except Exception as e:
            logger.error(f"Failed to post video: {e}")
            return False
        
        return False
    
    def post_album(
        self, 
        media_paths: List[str], 
        caption: str = ""
    ) -> bool:
        """
        Post an album to Instagram
        
        Args:
            media_paths: List of paths to media files
            caption: Caption for the album
            
        Returns:
            bool: Post success status
        """
        if not media_paths or len(media_paths) < 2:
            logger.error("Album requires at least 2 media files")
            return False
        
        # Validate all files exist
        for path in media_paths:
            if not os.path.exists(path):
                logger.error(f"Media file not found: {path}")
                return False
        
        logger.info(f"Preparing to post album with {len(media_paths)} files")
        
        try:
            media = self.client.album_upload(
                media_paths,
                caption=caption
            )
            
            if media:
                logger.info(f"Album posted successfully! Media ID: {media.pk}")
                self.save_post_metadata(media)
                return True
                
        except Exception as e:
            logger.error(f"Failed to post album: {e}")
            return False
        
        return False
    
    def save_post_metadata(self, media):
        """Save post metadata to JSON file"""
        metadata = {
            "media_id": media.pk,
            "media_code": media.code,
            "media_type": str(media.media_type),
            "timestamp": datetime.now().isoformat(),
            "permalink": media.permalink
        }
        
        metadata_file = "posted_media.json"
        metadata_list = []
        
        # Load existing metadata
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r') as f:
                    metadata_list = json.load(f)
            except:
                pass
        
        # Add new metadata
        metadata_list.append(metadata)
        
        # Save updated metadata
        with open(metadata_file, 'w') as f:
            json.dump(metadata_list, f, indent=4)
        
        logger.info(f"Metadata saved to {metadata_file}")
    
    def follow_user(self, username: str) -> bool:
        """Follow a user"""
        try:
            user_id = self.client.user_id_from_username(username)
            result = self.client.user_follow(user_id)
            logger.info(f"Successfully followed {username}")
            return result
        except Exception as e:
            logger.error(f"Failed to follow {username}: {e}")
            return False
    
    def unfollow_user(self, username: str) -> bool:
        """Unfollow a user"""
        try:
            user_id = self.client.user_id_from_username(username)
            result = self.client.user_unfollow(user_id)
            logger.info(f"Successfully unfollowed {username}")
            return result
        except Exception as e:
            logger.error(f"Failed to unfollow {username}: {e}")
            return False
    
    def like_media(self, media_id: str) -> bool:
        """Like a media"""
        try:
            result = self.client.media_like(media_id)
            logger.info(f"Successfully liked media {media_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to like media: {e}")
            return False
    
    def comment_media(self, media_id: str, comment: str) -> bool:
        """Comment on a media"""
        try:
            result = self.client.media_comment(media_id, comment)
            logger.info(f"Successfully commented on media {media_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to comment: {e}")
            return False
    
    def get_user_media(self, username: str, amount: int = 10) -> List:
        """Get user's recent media"""
        try:
            user_id = self.client.user_id_from_username(username)
            media = self.client.user_medias(user_id, amount)
            logger.info(f"Retrieved {len(media)} media from {username}")
            return media
        except Exception as e:
            logger.error(f"Failed to get user media: {e}")
            return []


def create_sample_config():
    """Create a sample configuration file"""
    config = {
        "username": "your_username",
        "password": "your_password",
        "session_file": "session.json",
        "proxy": None,
        "delay_range": [2, 5],
        "max_retries": 3,
        "accounts": []
    }
    
    with open("config.json", 'w') as f:
        json.dump(config, f, indent=4)
    
    print("Created sample config.json. Please edit it with your credentials!")


def main():
    """Main function to handle CLI arguments"""
    parser = argparse.ArgumentParser(
        description="Instagram Automation Bot using instagrapi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python instagram_bot.py login                    Login to Instagram
  python instagram_bot.py post-reel --video path   Post a reel
  python instagram_bot.py post-photo --photo path  Post a photo
  python instagram_bot.py info                     Get account info
  python instagram_bot.py logout                   Logout from Instagram
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Login command
    login_parser = subparsers.add_parser('login', help='Login to Instagram')
    login_parser.add_argument('-u', '--username', help='Instagram username')
    login_parser.add_argument('-p', '--password', help='Instagram password')
    
    # Post reel command
    reel_parser = subparsers.add_parser('post-reel', help='Post a reel')
    reel_parser.add_argument('-v', '--video', required=True, help='Path to video file')
    reel_parser.add_argument('-c', '--caption', default='', help='Caption for the reel')
    reel_parser.add_argument('-t', '--thumbnail', default=None, help='Path to thumbnail')
    
    # Post photo command
    photo_parser = subparsers.add_parser('post-photo', help='Post a photo')
    photo_parser.add_argument('-p', '--photo', required=True, help='Path to photo file')
    photo_parser.add_argument('-c', '--caption', default='', help='Caption for the photo')
    
    # Post video command
    video_parser = subparsers.add_parser('post-video', help='Post a video')
    video_parser.add_argument('-v', '--video', required=True, help='Path to video file')
    video_parser.add_argument('-c', '--caption', default='', help='Caption for the video')
    video_parser.add_argument('-t', '--thumbnail', default=None, help='Path to thumbnail')
    
    # Post album command
    album_parser = subparsers.add_parser('post-album', help='Post an album')
    album_parser.add_argument('-m', '--media', nargs='+', required=True, help='Paths to media files')
    album_parser.add_argument('-c', '--caption', default='', help='Caption for the album')
    
    # Info command
    subparsers.add_parser('info', help='Get account information')
    
    # Logout command
    subparsers.add_parser('logout', help='Logout from Instagram')
    
    # Config command
    subparsers.add_parser('config', help='Create sample configuration file')
    
    # Follow command
    follow_parser = subparsers.add_parser('follow', help='Follow a user')
    follow_parser.add_argument('-u', '--username', required=True, help='Username to follow')
    
    # Unfollow command
    unfollow_parser = subparsers.add_parser('unfollow', help='Unfollow a user')
    unfollow_parser.add_argument('-u', '--username', required=True, help='Username to unfollow')
    
    args = parser.parse_args()
    
    # Handle commands
    if args.command == 'config':
        create_sample_config()
        return
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize bot
    bot = InstagramBot()
    
    # Execute commands
    if args.command == 'login':
        success = bot.login(args.username, args.password)
        if success:
            info = bot.get_user_info()
            if info:
                print(f"\n✓ Logged in as: {info['username']}")
                print(f"  Followers: {info['followers']}")
                print(f"  Following: {info['following']}")
                print(f"  Posts: {info['media_count']}")
    
    elif args.command == 'post-reel':
        success = bot.post_reel(args.video, args.caption, args.thumbnail)
        if success:
            print("✓ Reel posted successfully!")
    
    elif args.command == 'post-photo':
        success = bot.post_photo(args.photo, args.caption)
        if success:
            print("✓ Photo posted successfully!")
    
    elif args.command == 'post-video':
        success = bot.post_video(args.video, args.caption, args.thumbnail)
        if success:
            print("✓ Video posted successfully!")
    
    elif args.command == 'post-album':
        success = bot.post_album(args.media, args.caption)
        if success:
            print("✓ Album posted successfully!")
    
    elif args.command == 'info':
        info = bot.get_user_info()
        if info:
            print(f"\n{'='*40}")
            print(f"Account Information")
            print(f"{'='*40}")
            print(f"Username: {info['username']}")
            print(f"Full Name: {info['full_name']}")
            print(f"Followers: {info['followers']}")
            print(f"Following: {info['following']}")
            print(f"Total Posts: {info['media_count']}")
            print(f"{'='*40}")
    
    elif args.command == 'logout':
        bot.logout()
        print("✓ Logged out successfully!")
    
    elif args.command == 'follow':
        success = bot.follow_user(args.username)
        if success:
            print(f"✓ Now following @{args.username}")
    
    elif args.command == 'unfollow':
        success = bot.unfollow_user(args.username)
        if success:
            print(f"✓ Unfollowed @{args.username}")


if __name__ == "__main__":
    main()
