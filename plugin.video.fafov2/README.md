# FafoV2 - Advanced Kodi Media Center Addon

![FafoV2 Logo](resources/media/icon.png)

## Overview

FafoV2 is a comprehensive Kodi addon that provides seamless access to movies, TV series, live TV, and YouTube content. Built with modern Python and designed for Kodi 19+ (Matrix), it offers advanced features including YouTube trailer integration via yt-dlp, custom playlist management, and support for all video formats.

## Features

### 🎬 Content Categories
- **Movies**: Organize and play movie content with trailer support
- **TV Series**: Manage TV show episodes and series
- **Live TV**: Stream live television content
- **YouTube**: Full YouTube integration with search and playback

### ⚡ Advanced Functionality
- **yt-dlp Integration**: High-quality YouTube video extraction and playback
- **Custom Lists**: Create and manage multiple custom playlists
- **Direct Link Support**: Play videos from any URL or source
- **Multi-Format Support**: Compatible with all video formats supported by Kodi
- **Smart Search**: Search across YouTube and local content
- **Quality Selection**: Choose video quality preferences

### 🛠 Technical Features
- **Modern Python 3**: Built for Kodi 19+ (Matrix) compatibility
- **Robust Error Handling**: Graceful fallbacks and error recovery
- **Data Persistence**: Local storage of lists and preferences
- **Export/Import**: Backup and restore your custom lists
- **Settings Management**: Comprehensive configuration options

## Installation

### Method 1: GitHub Release (Recommended)
1. Download the latest release ZIP from [GitHub Releases](https://github.com/aussiemaniacs/FafoV2/releases)
2. In Kodi, go to Settings → Add-ons → Install from zip file
3. Select the downloaded ZIP file
4. Wait for installation confirmation

### Method 2: Repository Installation
1. Add the repository source: `https://github.com/aussiemaniacs/FafoV2`
2. Install from repository → aussiemaniacs → Video add-ons → FafoV2

### Method 3: Manual Installation
1. Clone or download this repository
2. Copy the `plugin.video.fafov2` folder to your Kodi addons directory:
   - **Windows**: `%APPDATA%\Kodi\addons\`
   - **Linux**: `~/.kodi/addons/`
   - **Android**: `/sdcard/Android/data/org.xbmc.kodi/files/.kodi/addons/`
3. Restart Kodi

## Dependencies

FafoV2 automatically manages most dependencies, but for optimal functionality:

### Required
- Kodi 19.0+ (Matrix)
- Python 3.8+
- script.module.requests
- script.module.six

### Optional (Recommended)
- **yt-dlp**: For enhanced YouTube functionality
- **plugin.video.youtube**: Fallback YouTube support
- **script.module.resolveurl**: Additional URL resolution

### Installing yt-dlp

For the best YouTube experience, install yt-dlp:

**Linux/macOS:**
```bash
pip install yt-dlp
```

**Windows:**
```powershell
pip install yt-dlp
```

**Android (Termux):**
```bash
pkg install python
pip install yt-dlp
```

## Usage

### Main Menu
After installation, access FafoV2 from Kodi's Video Add-ons section:

1. **🎬 Movies** - Browse and play movie content
2. **📺 TV Series** - Access TV shows and episodes  
3. **📡 Live TV** - Stream live television
4. **▶️ YouTube** - Search and play YouTube videos
5. **📝 Custom Lists** - Manage your custom playlists

### Adding Content

#### Direct Links
1. Select "🔗 Add Direct Link" from the main menu
2. Enter the video URL (supports most streaming formats)
3. Enter a title for the content
4. Choose the appropriate category
5. The item will be added and available for playback

#### YouTube Videos
1. Go to "▶️ YouTube" → "🔍 Search YouTube"
2. Enter your search term
3. Select videos from the results
4. Videos are automatically added to your YouTube category

#### Custom Lists
1. Navigate to "📝 Custom Lists"
2. Select "➕ Create New List"
3. Enter a name and optional description
4. Add items to your list using the context menu on any video

### Playback
- Click any video item to start playback
- FafoV2 automatically resolves URLs and provides the best available quality
- Supports all Kodi-compatible video formats
- YouTube videos are played through optimized streams

### Context Menu
Right-click (or long-press on touch devices) any video item to:
- Add to custom lists
- View video information
- Copy video URL
- Remove from current list

## Settings

Access settings through the addon settings or Main Menu → "⚙️ Settings":

### General
- **Debug Logging**: Enable detailed logging for troubleshooting
- **Max Search Results**: Control how many search results to display
- **Default Video Quality**: Set preferred video quality (480p/720p/1080p/best)

### YouTube
- **YouTube API Key**: Optional API key for enhanced features
- **Region**: Set your geographical region for relevant content
- **Safe Search**: Control content filtering
- **Prefer yt-dlp**: Use yt-dlp over YouTube plugin when available

### Playback
- **External Player**: Use external video player
- **Buffer Mode**: Control video buffering behavior
- **Seek Steps**: Set forward/backward skip duration
- **Subtitle Language**: Preferred subtitle language

### Advanced
- **Cache Size**: Control cache memory usage
- **Request Timeout**: Network request timeout duration
- **Export/Import**: Backup and restore your data

## Troubleshooting

### Common Issues

#### "YouTube functionality limited"
- **Solution**: Install yt-dlp following the installation instructions above
- **Alternative**: Enable the official YouTube addon as fallback

#### "Video playback failed"
- **Check**: Network connection and URL validity
- **Try**: Different video quality settings
- **Verify**: Video source is accessible

#### "No search results"
- **Check**: Internet connection
- **Verify**: Search terms and region settings
- **Try**: Different search keywords

#### "Lists not saving"
- **Check**: Kodi has write permissions to addon data directory
- **Try**: Restarting Kodi
- **Verify**: Available storage space

### Logs and Debugging

1. Enable "Debug Logging" in addon settings
2. Reproduce the issue
3. Check Kodi logs: Settings → System → Logging → View current log
4. Look for entries containing `[FafoV2]`

## Development

### Project Structure
```
plugin.video.fafov2/
├── addon.xml              # Addon manifest
├── default.py             # Main entry point
├── resources/
│   ├── lib/              # Core addon logic
│   │   ├── main.py       # Main addon class
│   │   ├── utils.py      # Utility functions
│   │   ├── youtube_handler.py  # YouTube integration
│   │   └── lists_manager.py    # List management
│   ├── language/         # Localization files
│   ├── media/           # Icons and artwork
│   └── settings.xml     # Addon settings definition
└── README.md           # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit with clear messages: `git commit -m "Add feature description"`
5. Push to your fork: `git push origin feature-name`
6. Submit a pull request

### Code Style
- Follow PEP 8 Python style guidelines
- Use descriptive variable and function names
- Include docstrings for all functions and classes
- Add error handling for external API calls
- Test on multiple Kodi versions when possible

## Support

### Getting Help
- **GitHub Issues**: [Report bugs or request features](https://github.com/aussiemaniacs/FafoV2/issues)
- **Documentation**: Check this README and inline code documentation
- **Community**: Kodi community forums

### Reporting Bugs
When reporting issues, please include:
- Kodi version and platform (Windows/Linux/Android/etc.)
- FafoV2 addon version
- Clear description of the problem
- Steps to reproduce the issue
- Relevant log entries (with debug logging enabled)

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

FafoV2 is a content aggregation addon that provides access to publicly available content. The addon does not host, store, or distribute any content itself. Users are responsible for ensuring their use complies with local laws and regulations. The developers are not responsible for the content accessed through this addon.

## Changelog

### v2.0.0 (2025-07-21)
- Complete rewrite with modern Kodi framework
- YouTube integration with yt-dlp support  
- Custom lists and playlist management
- Direct link support for all video formats
- Live TV streaming capabilities
- Enhanced user interface and navigation
- Multi-list support with advanced organization
- Improved video quality selection
- Better error handling and logging
- Export/import functionality for data backup
- Comprehensive settings and configuration options

### Previous Versions
See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## Acknowledgments

- **Kodi Team**: For the excellent media center platform
- **yt-dlp Project**: For reliable YouTube video extraction
- **Community Contributors**: For feedback, testing, and contributions
- **Original FafoV1**: Building upon the foundation of the original addon

---

**Made with ❤️ by aussiemaniacs**

For more information, visit [GitHub Repository](https://github.com/aussiemaniacs/FafoV2)