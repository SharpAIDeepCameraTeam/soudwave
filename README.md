# Soundwave Studios

A music generation project using Magenta and TensorFlow for creating EDM and other electronic music.

## Features

- EDM music generation using Magenta's models
- Dynamic buildups and rhythmic patterns
- Chromatic progressions
- Drum pattern generation
- Interactive web interface

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run with Docker:
```bash
docker build -t soundwave-music-gen .
docker run -p 5001:5001 soundwave-music-gen
```

## Project Structure

- `music_generator.py`: Core music generation logic
- `app.py`: Flask web application
- `requirements.txt`: Python dependencies
- `Dockerfile`: Container configuration

## License

This project is licensed under the MIT License - see the LICENSE file for details.
