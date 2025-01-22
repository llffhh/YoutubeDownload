import streamlit as st
import subprocess
import os
from typing import Optional
import time

def download_audio(url: str, bitrate: str, output_dir: str = "downloads", progress_bar = None) -> tuple[bool, str]:
    """
    Download audio from a YouTube video with specified bitrate and progress tracking.
    Returns tuple of (success_status, error_message)
    """
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Using the exact same command structure that worked in command line
        # yt-dlp -x --audio-format mp3 --ffmpeg-location "C:\Users\hebe1\opt\ffmpeg\bin" https://youtu.be/Dzs9mDgUK4o?si=UeN2ffkrkF9zKVsb
        command = [
            'yt-dlp',
            '-x',
            '--audio-format', 'mp3',
            '--ffmpeg-location', r"C:\Users\hebe1\opt\ffmpeg\bin",  # Removed ffmpeg.exe from path
            url
        ]
        
        if bitrate:  # Add bitrate only if specified
            command.extend(['--audio-quality', bitrate])
        
        # Print command for debugging
        st.write("Executing command:", " ".join(command))
        
        # Run the command and capture output in real-time
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Store output and error
        output_message = ""
        error_message = ""
        
        # Monitor the download progress
        while True:
            output = process.stdout.readline()
            error = process.stderr.readline()
            
            if output:
                output_message += output
                # Update progress information
                if progress_bar is not None and '[download]' in output and '%' in output:
                    try:
                        # Extract percentage from yt-dlp output
                        percent = float(output.split('%')[0].split()[-1])
                        progress_bar.progress(min(percent / 100, 1.0))
                    except:
                        pass
            
            if error:
                error_message += error
                
            if output == '' and error == '' and process.poll() is not None:
                break
        
        rc = process.poll()
        if rc == 0:
            return True, output_message
        else:
            return False, f"Error: {error_message}\nOutput: {output_message}"
            
    except Exception as e:
        return False, str(e)

def main():
    st.set_page_config(page_title="YouTube Audio Downloader", page_icon="🎵")
    
    st.title("🎵 YouTube Audio Downloader")
    st.write("Download audio from YouTube videos with custom quality!")
    
    # Debug information section
    with st.expander("Debug Information"):
        st.write(f"Current working directory: {os.getcwd()}")
        ffmpeg_path = r'C:\Users\hebe1\opt\ffmpeg\bin'
        st.write(f"FFmpeg path: {ffmpeg_path}")
        st.write(f"FFmpeg exists: {os.path.exists(ffmpeg_path)}")
    
    # Input for YouTube URL
    url = st.text_input("Enter YouTube Video URL:")
    
    # Bitrate selection
    bitrate_options = {
        "320 kbps (Best Quality)": "320",
        "256 kbps (High Quality)": "256",
        "192 kbps (Good Quality)": "192",
        "128 kbps (Standard Quality)": "128",
        "96 kbps (Low Quality)": "96",
        "64 kbps (Very Low Quality)": "64"
    }
    
    selected_quality = st.select_slider(
        "Select Audio Quality",
        options=list(bitrate_options.keys()),
        value="192 kbps (Good Quality)"
    )
    
    bitrate = bitrate_options[selected_quality]
    
    st.info(f"Selected bitrate: {bitrate} kbps")
    
    # Download button
    if st.button("Download Audio"):
        if url:
            try:
                with st.spinner(f"Downloading and converting to {bitrate}kbps MP3..."):
                    # Create a progress bar
                    progress_bar = st.progress(0)
                    
                    # Start download
                    success, message = download_audio(url, bitrate, progress_bar=progress_bar)
                    
                    if success:
                        # Complete the progress bar
                        progress_bar.progress(1.0)
                        st.success("✅ Download completed successfully!")
                        st.balloons()
                        # Show download location
                        st.info(f"Your file has been saved in the 'downloads' folder with {bitrate}kbps quality.")
                        # Show full output in expander
                        with st.expander("Show download details"):
                            st.code(message)
                    else:
                        st.error("❌ Download failed. Error details:")
                        st.code(message)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("⚠️ Please enter a YouTube URL first!")
    
    # Add some helpful information
    with st.expander("ℹ️ About Audio Quality"):
        st.write("""
        **Audio Quality Guide:**
        - 320 kbps: Best quality, larger file size
        - 256 kbps: Very good quality, good balance
        - 192 kbps: Good quality, moderate file size
        - 128 kbps: Standard quality, smaller file size
        - 96 kbps: Lower quality, very small file size
        - 64 kbps: Lowest quality, smallest file size
        
        Higher bitrates mean better audio quality but larger file sizes. For most music, 192 kbps provides a good balance between quality and file size.
        """)
    
    with st.expander("ℹ️ How to use"):
        st.write("""
        1. Paste a YouTube video URL in the input field above
        2. Select your desired audio quality using the slider
        3. Click the 'Download Audio' button
        4. Wait for the download to complete
        5. Find your downloaded audio in the 'downloads' folder
        """)
    
    # Add footer
    st.markdown("---")
    st.markdown("Made with ❤️ using Streamlit")

if __name__ == "__main__":
    main()