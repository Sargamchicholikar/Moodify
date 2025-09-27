# 🎵 Moodify - Emotion-Based Bollywood Music Player

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8-red.svg)](https://opencv.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

An AI-powered web application that detects your emotions in real-time through webcam and plays Bollywood music matching your mood. The system dynamically searches YouTube for fresh songs every time, ensuring you never hear the same playlist twice!

## ✨ Features

- 🎭 **Real-time Emotion Detection**: Detects 3 emotions - Happy, Neutral, and Sad
- 🎵 **Dynamic Music Selection**: No predefined playlists - searches YouTube in real-time
- 🔄 **Never Repeats**: Different songs every time, even for the same emotion
- 🎬 **YouTube Integration**: Direct playback through YouTube embedded player
- 🎯 **Smart Detection**: Uses OpenCV face detection with emotion analysis
- 📱 **Responsive Design**: Works on desktop and mobile browsers
- 🚀 **Easy Setup**: No API keys or complex configuration needed

## 📸 Screenshots

### Main Interface
![Moodify Interface](https://via.placeholder.com/800x400?text=Moodify+Interface)

### Emotion Detection
- **Happy**: Plays party songs, dance numbers, celebration tracks
- **Neutral**: Plays romantic melodies, soft music
- **Sad**: Plays emotional songs, heartbreak melodies

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Webcam
- Modern web browser (Chrome, Firefox, Safari)
- Internet connection

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/moodify.git
cd moodify
```

2. **Create virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python app.py
```

5. **Open browser**
```
Navigate to http://localhost:5000
```

## 🎮 How to Use

1. **Start Detection**: Click "Start Detection" button
2. **Allow Camera**: Grant camera permissions when prompted
3. **See Your Mood**: The app detects your facial expression
4. **Automatic Music**: Songs start playing based on your emotion
5. **Manual Override**: Click emotion boxes to manually set mood
6. **Get New Songs**: Click "Get New Songs" button for fresh recommendations

## 🎯 How It Works

### Emotion Detection Pipeline
```
Webcam → Face Detection → Feature Analysis → Emotion Classification → Music Search → YouTube Playback
```

### Technical Architecture
- **Frontend**: HTML5, CSS3, JavaScript with Socket.IO
- **Backend**: Flask with Flask-SocketIO for real-time communication
- **Computer Vision**: OpenCV with Haar Cascades
- **Music Source**: Dynamic YouTube search (no API required)

## 📂 Project Structure

```
moodify/
│
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Documentation
├── LICENSE               # MIT License
├── .gitignore            # Git ignore file
│
└── static/               # Static files (auto-created)
    └── logs/            # Application logs
```

## 🔧 Configuration

The application works out of the box without any configuration. Optional settings:

- **Port**: Change port by setting `PORT` environment variable
- **Debug Mode**: Set `DEBUG=True` for development

## 🌟 Features in Detail

### Dynamic Song Search
- Generates unique search queries using combinations of:
  - Keywords (party, romantic, sad, etc.)
  - Artists (Arijit Singh, Neha Kakkar, etc.)
  - Years (2024, 2023, latest, etc.)
  - Movie names (latest Bollywood movies)
- Never uses predefined playlists

### Emotion Detection
- Uses facial landmarks analysis
- Checks for smiles, eye patterns, facial brightness
- Temporal smoothing to prevent flickering
- Manual override option available

### Smart Features
- Tracks played songs to avoid repetition
- Refresh button for new recommendations
- Auto-play toggle
- Session statistics

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenCV community for computer vision tools
- Flask team for the excellent web framework
- YouTube for music content
- Bollywood music industry for amazing songs

## 🐛 Known Issues

- Emotion detection accuracy depends on lighting conditions
- Works best with good internet connection for YouTube streaming
- Camera permissions required in browser

## 📧 Contact

Sargam - [@yourusername](https://github.com/yourusername)

Project Link: [https://github.com/yourusername/moodify](https://github.com/yourusername/moodify)

## 🌐 Future Enhancements

- [ ] Add support for more emotions
- [ ] Implement user accounts and preferences
- [ ] Add support for other music genres
- [ ] Mobile app development
- [ ] Improve emotion detection accuracy
- [ ] Add playlist export feature

---

Made with ❤️ for music lovers by Sargam
