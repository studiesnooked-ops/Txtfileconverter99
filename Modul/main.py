import os
import yt_dlp
from pyrogram import Client, filters
from vars import API_ID, API_HASH, BOT_TOKEN

# Initialize the Pyrogram client
app = Client(
    "media_downloader_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        "Hello! Send me a `.txt` file containing a list of video URLs (one per line), "
        "and I will download them and send them back to you."
    )

@app.on_message(filters.document)
async def handle_document(client, message):
    if message.document.mime_type == "text/plain":
        status_msg = await message.reply_text("Processing your text file...")
        
        # Download the text file
        txt_file_path = await message.download()
        
        try:
            with open(txt_file_path, 'r') as file:
                urls = [line.strip() for line in file.readlines() if line.strip()]
            
            if not urls:
                await status_msg.edit_text("The text file is empty or contains no valid URLs.")
                return

            await status_msg.edit_text(f"Found {len(urls)} URLs. Starting process...")
            
            # yt-dlp configuration
            ydl_opts = {
                'format': 'best',
                'outtmpl': 'downloads/%(title)s.%(ext)s', 
                'quiet': True,
                'no_warnings': True
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
                        await message.reply_video(
                            video=video_path,
                            caption=f"**{video_title}**"
                        )
                        
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
