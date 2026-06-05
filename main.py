import os
import yt_dlp
from pyrogram import Client, filters

# --- SETUP YOUR BOT CREDENTIALS HERE ---
# (Keep your existing app initialization if you already have it at the top of your file)
API_ID = "34867096"
API_HASH = "03941565a45dea9ff1d5dba90a31069b"
BOT_TOKEN = "8813917698:AAF12-XyoLj1gqWqcFi0-Het6CK66duups8"

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.document & filters.private)
async def process_text_file(client, message):
    status_msg = await message.reply_text("Processing file...")
    txt_file_path = await message.download()
    
    try:
        # Read all raw lines from the text file
        with open(txt_file_path, 'r') as file:
            raw_lines = [line.strip() for line in file.readlines() if line.strip()]
            
        # Filter out lecture names and isolate only the URLs
        urls = []
        for line in raw_lines:
            if "http" in line:
                url_start = line.find("http")
                extracted_url = line[url_start:].strip()
                urls.append(extracted_url)
                
        if not urls:
            await status_msg.edit_text("The text file is empty or contains no valid URLs.")
            return
            
        await status_msg.edit_text(f"Found {len(urls)} URLs. Starting process...")
        
        # yt-dlp configuration (UPDATED with http_headers to fix the empty file error)
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for url in urls:
                try:
                    await status_msg.edit_text(f"Downloading: {url}")
                    
                    # Extract info and download simultaneously
                    info = ydl.extract_info(url, download=True)
                    
                    # Get the exact file path where yt-dlp saved the video
                    video_path = ydl.prepare_filename(info)
                    video_title = info.get('title', 'Downloaded Video')
                    
                    await status_msg.edit_text(f"Uploading **{video_title}** to Telegram...")
                    
                    # Send the video back to the user
                    await message.reply_video(video=video_path, caption=f"**{video_title}**")
                    
                    # Delete the video from the server to save storage
                    if os.path.exists(video_path):
                        os.remove(video_path)
                        
                except Exception as url_error:
                    await message.reply_text(f"Failed to process {url}:\n`{str(url_error)}`")
                    
        await status_msg.edit_text("All URLs have been processed!")
        
    except Exception as e:
        await status_msg.edit_text(f"An error occurred: {str(e)}")
        
    finally:
        # Clean up the original text file
        if os.path.exists(txt_file_path):
            os.remove(txt_file_path)
        else:
            await message.reply_text("Please send a valid plain text (.txt) file.")

if __name__ == "__main__":
    print("Bot is up and running...")
    os.makedirs("downloads", exist_ok=True)
    app.run()
