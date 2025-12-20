# HLS Streaming Server

This project is a simple HLS streaming server built using Flask in Python. The server allows you to upload video files, which are then segmented and served as an HLS stream. It includes a basic web interface to view available videos and a video player to stream the content.

## Getting Started

### Prerequisites

Before running the server, make sure you have the following installed:

- Python 3
- Flask
- Flask-CORS

Install the required Python packages:

```bash
pip install Flask Flask-CORS
```

### Running the Server

2. Run the server:

```bash
python main.py
```

3. Open your browser and visit [http://localhost:5000/](http://localhost:5000/) to access the web interface.

## Usage

### Uploading Videos

1. Visit the upload page by clicking the "Upload" link on the web interface.

2. Choose a video file (MP4) and click "Upload."

### Viewing Available Videos

1. Go to the home page [http://localhost:5000/](http://localhost:5000/).

2. Click on the available video links to start streaming.

### HLS (HTTP Live Streaming)

HTTP Live Streaming (HLS) is an adaptive streaming protocol developed by Apple for delivering audio and video content over the internet. HLS breaks the media content into small, manageable chunks and delivers them over standard HTTP protocols. It enables adaptive bitrate streaming, allowing the client to switch between different quality levels based on network conditions.

HLS consists of a playlist file (usually with a .m3u8 extension) that serves as an index for the video chunks. The client requests these chunks sequentially, allowing for smooth playback and adaptive streaming.

