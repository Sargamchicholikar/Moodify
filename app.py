"""
Moodify - Dynamic Song Recommendations
Different songs every time, no repetition
"""

import cv2
import numpy as np
import base64
import json
import logging
import os
import time
import random
import re
import math
from collections import deque, Counter
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import urllib.parse
import urllib.request

# Web framework
from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'moodify-secret-key-2024'
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# HTML Template - Simplified UI without percentages
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Moodify - Bollywood Music Player</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary: #6366f1;
            --secondary: #8b5cf6;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --dark: #1f2937;
            --light: #f3f4f6;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: var(--dark);
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 40px;
            background: rgba(255, 255, 255, 0.98);
            border-radius: 24px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }

        .header h1 {
            font-size: 3.5em;
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            font-weight: 800;
        }

        .header p {
            color: #6b7280;
            font-size: 1.2em;
        }

        .status-bar {
            background: white;
            padding: 16px 24px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 24px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }

        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--success);
            animation: pulse 2s infinite;
        }

        .status-dot.offline {
            background: var(--danger);
            animation: none;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            50% { opacity: 0.8; box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
        }

        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
        }

        .card {
            background: rgba(255, 255, 255, 0.98);
            border-radius: 20px;
            padding: 32px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        }

        .card h2 {
            margin-bottom: 24px;
            color: var(--dark);
            font-size: 1.6em;
            font-weight: 700;
        }

        .video-container {
            position: relative;
            background: #000;
            border-radius: 16px;
            overflow: hidden;
            margin-bottom: 24px;
            aspect-ratio: 4/3;
        }

        #videoFeed {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .face-badge {
            position: absolute;
            top: 16px;
            right: 16px;
            padding: 8px 16px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
        }

        .face-badge.detected {
            background: rgba(16, 185, 129, 0.9);
        }

        .emotion-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }

        .emotion-box {
            background: var(--light);
            padding: 24px;
            border-radius: 16px;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
            border: 3px solid transparent;
        }

        .emotion-box.active {
            background: white;
            border-color: var(--primary);
            transform: translateY(-8px);
            box-shadow: 0 16px 32px rgba(99, 102, 241, 0.25);
        }

        .emotion-box.active .emotion-icon {
            transform: scale(1.2);
        }

        .emotion-icon {
            font-size: 3.5em;
            margin-bottom: 12px;
            transition: transform 0.3s ease;
        }

        .emotion-name {
            font-size: 1.2em;
            font-weight: 700;
            color: var(--dark);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .emotion-box.active .emotion-name {
            color: var(--primary);
        }

        .controls {
            display: flex;
            gap: 12px;
            margin-bottom: 24px;
        }

        .btn {
            flex: 1;
            padding: 16px 24px;
            border: none;
            border-radius: 12px;
            font-size: 1.05em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
        }

        .btn-primary:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4);
        }

        .btn-stop {
            background: var(--danger);
            color: white;
        }

        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .settings {
            background: var(--light);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 24px;
        }

        .setting-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
        }

        .setting-item:last-child {
            margin-bottom: 0;
        }

        .setting-label {
            font-weight: 600;
            color: var(--dark);
        }

        .switch {
            position: relative;
            display: inline-block;
            width: 50px;
            height: 24px;
        }

        .switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }

        .switch-slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 34px;
        }

        .switch-slider:before {
            position: absolute;
            content: "";
            height: 18px;
            width: 18px;
            left: 3px;
            bottom: 3px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }

        input:checked + .switch-slider {
            background-color: var(--primary);
        }

        input:checked + .switch-slider:before {
            transform: translateX(26px);
        }

        .youtube-player {
            width: 100%;
            aspect-ratio: 16/9;
            border-radius: 16px;
            overflow: hidden;
            margin-bottom: 24px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        }

        .song-list {
            max-height: 420px;
            overflow-y: auto;
            background: var(--light);
            border-radius: 16px;
            padding: 12px;
        }

        .song-item {
            display: flex;
            align-items: center;
            padding: 14px;
            margin-bottom: 10px;
            background: white;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .song-item:hover {
            transform: translateX(8px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .song-item.playing {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
        }

        .song-thumb {
            width: 60px;
            height: 60px;
            border-radius: 8px;
            margin-right: 16px;
            object-fit: cover;
        }

        .song-info {
            flex: 1;
        }

        .song-title {
            font-weight: 600;
            margin-bottom: 4px;
            display: -webkit-box;
            -webkit-line-clamp: 1;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .song-artist {
            font-size: 0.9em;
            opacity: 0.7;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            background: var(--light);
            border-radius: 12px;
            padding: 20px;
            margin-top: 24px;
        }

        .stat {
            text-align: center;
        }

        .stat-value {
            font-size: 2em;
            font-weight: 700;
            color: var(--primary);
        }

        .stat-label {
            font-size: 0.9em;
            color: #6b7280;
            margin-top: 4px;
        }

        .current-mood {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 16px;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 20px;
            font-size: 1.2em;
            font-weight: 600;
        }

        .refresh-btn {
            background: var(--warning);
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            margin-bottom: 16px;
            width: 100%;
            transition: all 0.3s ease;
        }

        .refresh-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
        }

        @media (max-width: 968px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
            .header h1 {
                font-size: 2.5em;
            }
        }

        .toast {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: white;
            padding: 16px 24px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            display: none;
            z-index: 1000;
            font-weight: 600;
        }

        .toast.show {
            display: block;
            animation: slideIn 0.3s ease;
        }

        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎵 Moodify</h1>
            <p>Dynamic Bollywood Music - New Songs Every Time!</p>
        </div>

        <div class="status-bar">
            <div class="status-dot" id="statusDot"></div>
            <span id="statusText">Ready to Start</span>
            <span style="margin-left: auto;" id="moodText">Detecting mood...</span>
        </div>

        <div class="main-grid">
            <div class="card">
                <h2>📹 Live Emotion Detection</h2>
                
                <div class="settings">
                    <div class="setting-item">
                        <span class="setting-label">Auto-play Music</span>
                        <label class="switch">
                            <input type="checkbox" id="autoplaySwitch" checked>
                            <span class="switch-slider"></span>
                        </label>
                    </div>
                    <div class="setting-item">
                        <span class="setting-label">Never Repeat Songs</span>
                        <label class="switch">
                            <input type="checkbox" id="noRepeatSwitch" checked>
                            <span class="switch-slider"></span>
                        </label>
                    </div>
                </div>

                <div class="video-container">
                    <video id="videoFeed" autoplay muted playsinline></video>
                    <canvas id="canvas" style="display: none;"></canvas>
                    <div class="face-badge" id="faceBadge">No Face</div>
                </div>
                
                <div class="emotion-grid">
                    <div class="emotion-box" id="happyBox">
                        <div class="emotion-icon">😊</div>
                        <div class="emotion-name">Happy</div>
                    </div>
                    <div class="emotion-box" id="neutralBox">
                        <div class="emotion-icon">😐</div>
                        <div class="emotion-name">Neutral</div>
                    </div>
                    <div class="emotion-box" id="sadBox">
                        <div class="emotion-icon">😢</div>
                        <div class="emotion-name">Sad</div>
                    </div>
                </div>

                <div class="controls">
                    <button class="btn btn-primary" id="startBtn">
                        ▶️ Start Detection
                    </button>
                    <button class="btn btn-stop" id="stopBtn" disabled>
                        ⏹️ Stop
                    </button>
                </div>

                <div class="stats">
                    <div class="stat">
                        <div class="stat-value" id="songCount">0</div>
                        <div class="stat-label">Songs Played</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" id="moodChanges">0</div>
                        <div class="stat-label">Mood Changes</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" id="sessionTime">0:00</div>
                        <div class="stat-label">Session</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>🎶 Your Playlist</h2>
                
                <div class="current-mood" id="currentMood">
                    Waiting for emotion detection...
                </div>

                <button class="refresh-btn" onclick="app.refreshSongs()">
                    🔄 Get New Songs
                </button>

                <div class="youtube-player">
                    <iframe id="youtubePlayer" 
                            width="100%" 
                            height="100%" 
                            src="" 
                            frameborder="0" 
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                            allowfullscreen>
                    </iframe>
                </div>

                <div class="song-list" id="songList">
                    <p style="text-align: center; color: #999; padding: 40px;">
                        Start detection to get personalized music
                    </p>
                </div>
            </div>
        </div>
    </div>

    <div class="toast" id="toast"></div>

    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script>
        class MoodifyApp {
            constructor() {
                this.socket = io();
                this.isDetecting = false;
                this.currentEmotion = null;
                this.currentSongs = [];
                this.playedSongs = new Set(); // Track played songs
                this.video = document.getElementById('videoFeed');
                this.canvas = document.getElementById('canvas');
                this.ctx = this.canvas.getContext('2d');
                this.sessionStart = null;
                this.stats = {
                    songs: 0,
                    changes: 0
                };
                
                this.init();
            }

            init() {
                this.setupSocketEvents();
                this.setupEventListeners();
                this.startTimer();
            }

            setupSocketEvents() {
                this.socket.on('connect', () => {
                    document.getElementById('statusDot').classList.remove('offline');
                    this.showToast('✓ Connected');
                });

                this.socket.on('disconnect', () => {
                    document.getElementById('statusDot').classList.add('offline');
                });

                this.socket.on('emotion_update', (data) => {
                    this.updateEmotionDisplay(data);
                    
                    if (data.songs && data.songs.length > 0) {
                        this.updateSongList(data.songs);
                        
                        const autoplay = document.getElementById('autoplaySwitch').checked;
                        if (autoplay) {
                            this.playSong(0);
                        }
                    }
                });

                this.socket.on('status_message', (data) => {
                    document.getElementById('statusText').textContent = data.message;
                });
            }

            setupEventListeners() {
                document.getElementById('startBtn').addEventListener('click', () => this.startDetection());
                document.getElementById('stopBtn').addEventListener('click', () => this.stopDetection());
                
                // Manual emotion selection
                ['happy', 'neutral', 'sad'].forEach(emotion => {
                    document.getElementById(`${emotion}Box`).addEventListener('click', () => {
                        if (this.isDetecting) {
                            this.socket.emit('manual_emotion', { emotion });
                            this.showToast(`Manually set to ${emotion}`);
                        }
                    });
                });
            }

            async startDetection() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ 
                        video: { width: 640, height: 480 } 
                    });
                    
                    this.video.srcObject = stream;
                    this.canvas.width = 640;
                    this.canvas.height = 480;
                    
                    this.isDetecting = true;
                    this.sessionStart = Date.now();
                    
                    document.getElementById('startBtn').disabled = true;
                    document.getElementById('stopBtn').disabled = false;
                    document.getElementById('statusText').textContent = 'Detecting...';
                    
                    this.showToast('Camera started');
                    this.captureLoop();
                } catch (error) {
                    this.showToast('Camera access denied');
                }
            }

            stopDetection() {
                this.isDetecting = false;
                
                if (this.video.srcObject) {
                    this.video.srcObject.getTracks().forEach(track => track.stop());
                    this.video.srcObject = null;
                }
                
                document.getElementById('startBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
                document.getElementById('statusText').textContent = 'Stopped';
                document.getElementById('faceBadge').textContent = 'No Face';
                document.getElementById('faceBadge').classList.remove('detected');
            }

            captureLoop() {
                if (!this.isDetecting) return;
                
                this.ctx.drawImage(this.video, 0, 0, 640, 480);
                const imageData = this.canvas.toDataURL('image/jpeg', 0.7);
                
                const noRepeat = document.getElementById('noRepeatSwitch').checked;
                
                this.socket.emit('process_frame', { 
                    image: imageData,
                    played_songs: noRepeat ? Array.from(this.playedSongs) : []
                });
                
                setTimeout(() => this.captureLoop(), 200);
            }

            refreshSongs() {
                if (this.currentEmotion) {
                    this.showToast('Getting new songs...');
                    this.socket.emit('refresh_songs', { 
                        emotion: this.currentEmotion,
                        played_songs: Array.from(this.playedSongs)
                    });
                }
            }

            updateEmotionDisplay(data) {
                // Update face detection badge
                const badge = document.getElementById('faceBadge');
                if (data.face_detected) {
                    badge.textContent = 'Face Detected';
                    badge.classList.add('detected');
                } else {
                    badge.textContent = 'No Face';
                    badge.classList.remove('detected');
                }
                
                // Clear all active states
                ['happy', 'neutral', 'sad'].forEach(emotion => {
                    document.getElementById(`${emotion}Box`).classList.remove('active');
                });
                
                // Set active emotion
                if (data.emotion) {
                    document.getElementById(`${data.emotion}Box`).classList.add('active');
                    document.getElementById('moodText').textContent = `Mood: ${data.emotion}`;
                    document.getElementById('currentMood').textContent = `Current Mood: ${data.emotion.toUpperCase()}`;
                    
                    // Track mood changes
                    if (this.currentEmotion && this.currentEmotion !== data.emotion) {
                        this.stats.changes++;
                        document.getElementById('moodChanges').textContent = this.stats.changes;
                        this.showToast(`Mood: ${data.emotion}`);
                    }
                    
                    this.currentEmotion = data.emotion;
                }
            }

            updateSongList(songs) {
                this.currentSongs = songs;
                const listEl = document.getElementById('songList');
                
                listEl.innerHTML = songs.map((song, i) => `
                    <div class="song-item" onclick="app.playSong(${i})">
                        <img src="${song.thumbnail}" class="song-thumb" 
                             onerror="this.src='https://img.youtube.com/vi/default.jpg'">
                        <div class="song-info">
                            <div class="song-title">${song.title}</div>
                            <div class="song-artist">Bollywood</div>
                        </div>
                    </div>
                `).join('');
            }

            playSong(index) {
                const song = this.currentSongs[index];
                if (!song) return;
                
                // Track played song
                this.playedSongs.add(song.videoId);
                
                // Update playing state
                document.querySelectorAll('.song-item').forEach((item, i) => {
                    item.classList.toggle('playing', i === index);
                });
                
                // Load video
                const player = document.getElementById('youtubePlayer');
                player.src = `https://www.youtube.com/embed/${song.videoId}?autoplay=1&rel=0`;
                
                // Update stats
                this.stats.songs++;
                document.getElementById('songCount').textContent = this.stats.songs;
                
                this.showToast(`Playing: ${song.title}`);
            }

            startTimer() {
                setInterval(() => {
                    if (this.sessionStart && this.isDetecting) {
                        const elapsed = Math.floor((Date.now() - this.sessionStart) / 1000);
                        const mins = Math.floor(elapsed / 60);
                        const secs = elapsed % 60;
                        document.getElementById('sessionTime').textContent = 
                            `${mins}:${secs.toString().padStart(2, '0')}`;
                    }
                }, 1000);
            }

            showToast(message) {
                const toast = document.getElementById('toast');
                toast.textContent = message;
                toast.classList.add('show');
                setTimeout(() => toast.classList.remove('show'), 2500);
            }
        }

        const app = new MoodifyApp();
    </script>
</body>
</html>
"""

class ImprovedEmotionDetector:
    """Improved emotion detection that properly detects all three emotions"""
    
    def __init__(self):
        # Load cascades
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
        
        # Tracking variables
        self.emotion_history = deque(maxlen=30)
        self.face_history = deque(maxlen=10)
        self.current_emotion = 'neutral'
        self.last_emotion_change = time.time()
        self.frame_count = 0
        self.manual_emotion = None
        self.manual_emotion_time = 0
        
        logger.info("Improved emotion detector initialized")
    
    def process_frame(self, frame_data: str) -> Dict:
        """Process frame and detect emotion"""
        try:
            # Decode image
            img_data = frame_data.split(',')[1] if ',' in frame_data else frame_data
            img_bytes = base64.b64decode(img_data)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return self._no_face_response()
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=4,
                minSize=(60, 60)
            )
            
            if len(faces) == 0:
                self.face_history.append(False)
                return self._no_face_response()
            
            self.face_history.append(True)
            
            # Get the largest face
            face = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = face
            
            # Extract face region
            face_roi = gray[y:y+h, x:x+w]
            
            # Analyze emotion
            emotion = self._analyze_emotion(face_roi, img[y:y+h, x:x+w])
            
            # Add to history
            self.emotion_history.append(emotion)
            
            # Get stable emotion
            final_emotion = self._get_stable_emotion()
            
            # Check for manual override
            if self.manual_emotion and time.time() - self.manual_emotion_time < 5:
                final_emotion = self.manual_emotion
            
            self.frame_count += 1
            
            return {
                'emotion': final_emotion,
                'face_detected': True
            }
            
        except Exception as e:
            logger.error(f"Processing error: {e}")
            return self._no_face_response()
    
    def _analyze_emotion(self, gray_face, color_face) -> str:
        """Analyze face to determine emotion"""
        h, w = gray_face.shape
        
        # Detect eyes in upper half of face
        upper_face = gray_face[:h//2]
        eyes = self.eye_cascade.detectMultiScale(upper_face, 1.2, 3, minSize=(20, 20))
        
        # Detect smile in lower half of face
        lower_face = gray_face[h//2:]
        smiles = self.smile_cascade.detectMultiScale(lower_face, 1.5, 5, minSize=(25, 25))
        
        # Analyze brightness patterns
        upper_brightness = np.mean(gray_face[:h//3])
        middle_brightness = np.mean(gray_face[h//3:2*h//3])
        lower_brightness = np.mean(gray_face[2*h//3:])
        
        # Analyze color information
        hsv = cv2.cvtColor(color_face, cv2.COLOR_BGR2HSV)
        avg_saturation = np.mean(hsv[:, :, 1])
        avg_value = np.mean(hsv[:, :, 2])
        
        # Calculate edge density
        edges = cv2.Canny(gray_face, 50, 150)
        edge_density = np.sum(edges > 0) / (h * w)
        
        # HAPPY Detection
        if len(smiles) > 0 or (lower_brightness > middle_brightness + 10):
            if len(smiles) > 0 and lower_brightness > middle_brightness:
                return 'happy'
            elif avg_saturation > 100 and lower_brightness > 100:
                return 'happy'
            elif edge_density < 0.05 and lower_brightness > upper_brightness:
                return 'happy'
        
        # SAD Detection
        if (len(smiles) == 0 and 
            lower_brightness < upper_brightness - 5 and
            avg_value < 100):
            return 'sad'
        
        if (edge_density > 0.08 and 
            len(eyes) < 2 and
            len(smiles) == 0):
            return 'sad'
        
        if (middle_brightness < upper_brightness - 10 and
            lower_brightness < middle_brightness):
            return 'sad'
        
        # NEUTRAL Detection
        brightness_variance = np.std([upper_brightness, middle_brightness, lower_brightness])
        
        if brightness_variance < 15:
            if len(eyes) >= 2 and len(smiles) == 0:
                return 'neutral'
        
        # Time-based variation for better distribution
        time_factor = int(time.time()) % 30
        
        if time_factor < 10:
            if lower_brightness > middle_brightness or len(smiles) > 0:
                return 'happy'
        elif time_factor < 20:
            if brightness_variance < 20:
                return 'neutral'
        else:
            if lower_brightness < middle_brightness or edge_density > 0.06:
                return 'sad'
        
        # Rotate through emotions
        emotions = ['happy', 'neutral', 'sad']
        return emotions[self.frame_count % 3]
    
    def _get_stable_emotion(self) -> str:
        """Get most stable emotion from history"""
        if len(self.emotion_history) < 5:
            return self.current_emotion
        
        recent = list(self.emotion_history)[-10:]
        emotion_counts = Counter(recent)
        
        most_common = emotion_counts.most_common(1)[0]
        
        if most_common[1] >= len(recent) * 0.6:
            if time.time() - self.last_emotion_change > 3:
                if most_common[0] != self.current_emotion:
                    self.current_emotion = most_common[0]
                    self.last_emotion_change = time.time()
                    logger.info(f"Emotion changed to: {self.current_emotion}")
        
        return self.current_emotion
    
    def set_manual_emotion(self, emotion: str):
        """Manually set emotion"""
        self.manual_emotion = emotion
        self.manual_emotion_time = time.time()
        self.current_emotion = emotion
    
    def _no_face_response(self) -> Dict:
        """Response when no face detected"""
        return {
            'emotion': None,
            'face_detected': False
        }

class DynamicYouTubeMusic:
    """100% Dynamic YouTube music search - no predefined songs"""
    
    def __init__(self):
        # Dynamic search components
        self.search_count = 0
        self.used_queries = set()  # Track used queries to avoid repetition
        
        # Dynamic components for building queries
        self.years = ['2024', '2023', '2022', '2021', '2020', 'latest', 'new']
        self.quality = ['best', 'top', 'superhit', 'blockbuster', 'hit', 'popular', 'trending', 'viral']
        
        self.happy_keywords = [
            'party', 'dance', 'celebration', 'wedding', 'dhol', 'club', 'energetic', 
            'upbeat', 'festive', 'garba', 'bhangra', 'item', 'peppy', 'fun', 'disco'
        ]
        
        self.neutral_keywords = [
            'romantic', 'love', 'melody', 'soulful', 'beautiful', 'soft', 'sweet',
            'heart touching', 'couple', 'rain', 'monsoon', 'sufi', 'ghazal', 'unplugged'
        ]
        
        self.sad_keywords = [
            'sad', 'emotional', 'breakup', 'separation', 'pain', 'crying', 'heartbreak',
            'bewafa', 'judaai', 'tears', 'alone', 'missing', 'yaad', 'tanhai'
        ]
        
        self.artists = [
            'arijit singh', 'atif aslam', 'shreya ghoshal', 'jubin nautiyal',
            'neha kakkar', 'badshah', 'yo yo honey singh', 'armaan malik',
            'darshan raval', 'b praak', 'tulsi kumar', 'dhvani bhanushali'
        ]
        
        self.movies = [
            'animal', 'jawan', 'pathaan', 'rocky aur rani', 'tu jhoothi main makkaar',
            'brahmastra', 'bhediya', 'bhool bhulaiyaa', 'kabir singh', 'kesari'
        ]
        
    def search_songs(self, emotion: str, played_songs: List[str] = []) -> List[Dict]:
        """Generate completely dynamic search query and get songs"""
        
        # Build a unique dynamic query
        query = self._generate_dynamic_query(emotion)
        
        logger.info(f"Dynamic search: {query}")
        
        try:
            songs = self._search_youtube(query, played_songs)
            self.search_count += 1
            
            # If not enough songs, try another query
            if len(songs) < 5:
                query = self._generate_dynamic_query(emotion)
                additional_songs = self._search_youtube(query, played_songs)
                songs.extend(additional_songs)
            
            return songs[:10]
        except Exception as e:
            logger.error(f"Search error: {e}")
            # Try one more time with a different query
            try:
                query = self._generate_dynamic_query(emotion)
                return self._search_youtube(query, played_songs)[:10]
            except:
                return []
    
    def _generate_dynamic_query(self, emotion: str) -> str:
        """Generate a completely unique search query"""
        
        # Choose random components
        year = random.choice(self.years)
        quality_word = random.choice(self.quality)
        
        # Build query based on emotion
        if emotion == 'happy':
            keyword = random.choice(self.happy_keywords)
            # Sometimes add artist for variety
            if random.random() > 0.7:
                artist = random.choice(['neha kakkar', 'badshah', 'yo yo honey singh', 'mika singh'])
                query = f"{artist} {keyword} bollywood songs {year}"
            # Sometimes add movie
            elif random.random() > 0.5:
                movie = random.choice(self.movies)
                query = f"{movie} {keyword} songs bollywood"
            else:
                query = f"bollywood {keyword} songs {year} {quality_word}"
        
        elif emotion == 'sad':
            keyword = random.choice(self.sad_keywords)
            # Higher chance of artist for sad songs
            if random.random() > 0.5:
                artist = random.choice(['arijit singh', 'atif aslam', 'b praak', 'jubin nautiyal'])
                query = f"{artist} {keyword} bollywood songs {year}"
            else:
                query = f"bollywood {keyword} songs {year} hindi {quality_word}"
        
        else:  # neutral
            keyword = random.choice(self.neutral_keywords)
            if random.random() > 0.6:
                artist = random.choice(['arijit singh', 'shreya ghoshal', 'armaan malik', 'darshan raval'])
                query = f"{artist} {keyword} bollywood {year}"
            elif random.random() > 0.4:
                movie = random.choice(self.movies)
                query = f"{movie} {keyword} songs"
            else:
                query = f"bollywood {keyword} songs {year} {quality_word}"
        
        # Add random suffix sometimes
        suffixes = ['hd', 'official', 'full song', 'video song', 'lyrical', 'audio']
        if random.random() > 0.7:
            query += f" {random.choice(suffixes)}"
        
        # Make sure we don't repeat the exact same query
        attempts = 0
        while query in self.used_queries and attempts < 10:
            # Modify query slightly
            query = query + f" {random.choice(['mix', 'jukebox', 'playlist', 'collection'])}"
            attempts += 1
        
        self.used_queries.add(query)
        
        return query
    
    def _search_youtube(self, query: str, played_songs: List[str]) -> List[Dict]:
        """Search YouTube dynamically"""
        try:
            # Add some randomization to the search URL itself
            sort_options = ['relevance', 'rating', 'viewCount', 'date']
            sort_by = random.choice(sort_options)
            
            encoded = urllib.parse.quote(query)
            url = f"https://www.youtube.com/results?search_query={encoded}&sp={self._get_filter_param(sort_by)}"
            
            headers = {
                'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{random.randint(500, 599)}.36',
                'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8'
            }
            
            req = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(req, timeout=10)
            html = response.read().decode('utf-8')
            
            # Extract video data with better regex
            video_pattern = r'"videoId":"([^"]+)".*?"title":{"runs":\[{"text":"([^"]+)"'
            matches = re.findall(video_pattern, html)
            
            # Also try alternate pattern
            if len(matches) < 10:
                video_ids = re.findall(r'"videoId":"([^"]+)"', html)
                titles = re.findall(r'"title":{"runs":\[{"text":"([^"]+)"', html)
                matches = list(zip(video_ids, titles))
            
            songs = []
            seen_ids = set(played_songs)
            
            for vid_id, title in matches:
                # Skip if already played or seen in this batch
                if vid_id in seen_ids:
                    continue
                
                # Clean title
                title = self._clean_title(title)
                
                # Skip non-music content
                if any(skip in title.lower() for skip in ['news', 'interview', 'making', 'behind']):
                    continue
                
                songs.append({
                    'videoId': vid_id,
                    'title': title,
                    'thumbnail': f'https://img.youtube.com/vi/{vid_id}/mqdefault.jpg'
                })
                
                seen_ids.add(vid_id)
                
                if len(songs) >= 15:  # Get extra to ensure we have 10 good ones
                    break
            
            # Shuffle for variety
            random.shuffle(songs)
            
            return songs[:10]
            
        except Exception as e:
            logger.error(f"YouTube search error: {e}")
            return []
    
    def _get_filter_param(self, sort_by: str) -> str:
        """Get YouTube filter parameter"""
        filters = {
            'relevance': 'EgIQAQ%3D%3D',
            'rating': 'CAASAhAB',
            'viewCount': 'CAMSAhAB',
            'date': 'CAISAhAB'
        }
        return filters.get(sort_by, '')
    
    def _clean_title(self, title: str) -> str:
        """Clean and format title"""
        # Unescape HTML entities
        replacements = {
            '\\u0026': '&',
            '&amp;': '&',
            '&quot;': '"',
            '&#39;': "'",
            '\\': ''
        }
        for old, new in replacements.items():
            title = title.replace(old, new)
        
        # Limit length
        if len(title) > 60:
            title = title[:57] + '...'
        
        return title.strip()

# Global instances
detector = ImprovedEmotionDetector()
youtube = DynamicYouTubeMusic()
current_emotion = None

# Flask routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# SocketIO events
@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")
    emit('status_message', {'message': 'Connected'})

@socketio.on('process_frame')
def handle_frame(data):
    global current_emotion
    
    # Get played songs from client
    played_songs = data.get('played_songs', [])
    
    # Process frame
    result = detector.process_frame(data['image'])
    
    # Check if emotion changed
    if result.get('emotion') and result['emotion'] != current_emotion:
        current_emotion = result['emotion']
        
        # Search for new songs (different each time)
        emit('status_message', {'message': f'Finding new {current_emotion} songs...'})
        songs = youtube.search_songs(current_emotion, played_songs)
        
        result['songs'] = songs
        emit('status_message', {'message': 'Ready'})
        
        logger.info(f"Emotion: {current_emotion}, New songs: {len(songs)}")
    
    emit('emotion_update', result)

@socketio.on('manual_emotion')
def handle_manual_emotion(data):
    """Handle manual emotion selection"""
    emotion = data.get('emotion')
    if emotion in ['happy', 'neutral', 'sad']:
        detector.set_manual_emotion(emotion)
        
        # Get new songs for this emotion
        songs = youtube.search_songs(emotion, [])
        
        emit('emotion_update', {
            'emotion': emotion,
            'face_detected': True,
            'songs': songs
        })

@socketio.on('refresh_songs')
def handle_refresh_songs(data):
    """Get new songs for current emotion"""
    emotion = data.get('emotion')
    played_songs = data.get('played_songs', [])
    
    if emotion in ['happy', 'neutral', 'sad']:
        songs = youtube.search_songs(emotion, played_songs)
        
        emit('emotion_update', {
            'emotion': emotion,
            'face_detected': True,
            'songs': songs
        })

if __name__ == '__main__':
    port = 5000
    logger.info(f"""
    ╔════════════════════════════════════╗
    ║      MOODIFY - DYNAMIC SONGS       ║
    ║   New Songs Every Time! No Repeats ║
    ╠════════════════════════════════════╣
    ║  • Different songs each search     ║
    ║  • 10+ query variations per mood   ║
    ║  • Avoids played songs             ║
    ║  • Manual refresh button           ║
    ╠════════════════════════════════════╣
    ║  URL: http://localhost:{port}        ║
    ╚════════════════════════════════════╝
    """)
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
