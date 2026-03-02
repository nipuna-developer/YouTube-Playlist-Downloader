import customtkinter as ctk
import yt_dlp
import threading
from tkinter import filedialog, messagebox
import os
import sys

# Configure appearance
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Playlist Downloader")
        self.geometry("600x550")
        self.resizable(False, False)

        # Download path variable
        self.download_path = ctk.StringVar(value=os.path.join(os.path.expanduser('~'), 'Downloads'))
        
        # Format and Resolution variables
        self.format_var = ctk.StringVar(value="MP4")
        self.resolution_var = ctk.StringVar(value="Highest")

        # Cancel flag
        self.is_cancelled = False

        self.setup_ui()

    def setup_ui(self):
        # Main Frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title Label
        self.title_label = ctk.CTkLabel(self.main_frame, text="YouTube Playlist Downloader", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(10, 20))

        # URL Input
        self.url_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.url_frame.pack(fill="x", pady=5)
        self.url_label = ctk.CTkLabel(self.url_frame, text="Playlist URL:")
        self.url_label.pack(side="left", padx=(0, 10))
        self.url_entry = ctk.CTkEntry(self.url_frame, placeholder_text="Paste YouTube Playlist Link Here", width=400)
        self.url_entry.pack(side="left", fill="x", expand=True)

        # Path Selection
        self.path_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.path_frame.pack(fill="x", pady=15)
        self.path_label = ctk.CTkLabel(self.path_frame, text="Save To:")
        self.path_label.pack(side="left", padx=(0, 10))
        self.path_entry = ctk.CTkEntry(self.path_frame, textvariable=self.download_path, width=300, state="readonly")
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.browse_btn = ctk.CTkButton(self.path_frame, text="Browse", width=80, command=self.browse_folder)
        self.browse_btn.pack(side="left")

        # Options Frame (Format & Resolution)
        self.options_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.options_frame.pack(fill="x", pady=5)
        
        # Format Selection
        self.format_label = ctk.CTkLabel(self.options_frame, text="Format:")
        self.format_label.pack(side="left", padx=(0, 10))
        self.format_menu = ctk.CTkOptionMenu(self.options_frame, values=["MP4", "MP3"], variable=self.format_var, command=self.format_changed, width=100)
        self.format_menu.pack(side="left", padx=(0, 20))
        
        # Resolution Selection
        self.resolution_label = ctk.CTkLabel(self.options_frame, text="Resolution:")
        self.resolution_label.pack(side="left", padx=(0, 10))
        self.resolution_menu = ctk.CTkOptionMenu(self.options_frame, values=["Highest", "1080p", "720p", "480p", "360p", "Lowest"], variable=self.resolution_var, width=120)
        self.resolution_menu.pack(side="left")

        # Range Selection Frame
        self.range_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.range_frame.pack(fill="x", pady=10)
        
        self.start_label = ctk.CTkLabel(self.range_frame, text="Start Video:")
        self.start_label.pack(side="left", padx=(0, 10))
        self.start_entry = ctk.CTkEntry(self.range_frame, placeholder_text="e.g. 1", width=80)
        self.start_entry.pack(side="left", padx=(0, 20))
        
        self.end_label = ctk.CTkLabel(self.range_frame, text="End Video:")
        self.end_label.pack(side="left", padx=(0, 10))
        self.end_entry = ctk.CTkEntry(self.range_frame, placeholder_text="e.g. 20", width=80)
        self.end_entry.pack(side="left")

        # Progress
        self.progress_label = ctk.CTkLabel(self.main_frame, text="Ready")
        self.progress_label.pack(pady=(10, 0))
        self.progressbar = ctk.CTkProgressBar(self.main_frame)
        self.progressbar.pack(fill="x", pady=(5, 10))
        self.progressbar.set(0)

        # Details text
        self.details_label = ctk.CTkLabel(self.main_frame, text="", text_color="gray")
        self.details_label.pack(pady=(0, 10))

        # Buttons Frame
        self.buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.buttons_frame.pack(pady=10)

        # Download Button
        self.download_btn = ctk.CTkButton(self.buttons_frame, text="Download Playlist", font=ctk.CTkFont(size=16, weight="bold"), height=40, command=self.start_download)
        self.download_btn.pack(side="left", padx=10)

        # Cancel Button
        self.cancel_btn = ctk.CTkButton(self.buttons_frame, text="Cancel", font=ctk.CTkFont(size=16, weight="bold"), height=40, width=100, fg_color="#C62828", hover_color="#8E0000", state="disabled", command=self.cancel_download)
        self.cancel_btn.pack(side="left", padx=10)

        # Footer
        self.footer_label = ctk.CTkLabel(self.main_frame, text="Dev By NIpuna Dilshan", font=ctk.CTkFont(size=10), text_color="gray")
        self.footer_label.pack(side="bottom", pady=5)

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_path.get())
        if folder:
            self.download_path.set(folder)

    def format_changed(self, choice):
        if choice == "MP3":
            self.resolution_menu.configure(state="disabled")
        else:
            self.resolution_menu.configure(state="normal")

    def cancel_download(self):
        if messagebox.askyesno("Cancel Download", "Are you sure you want to cancel the download?"):
            self.is_cancelled = True
            self.cancel_btn.configure(state="disabled", text="Cancelling...")

    def progress_hook(self, d):
        if self.is_cancelled:
            raise Exception("Download cancelled by user")

        if d['status'] == 'downloading':
            try:
                # Update progress bar
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded_bytes = d.get('downloaded_bytes', 0)
                
                if total_bytes > 0:
                    percentage = downloaded_bytes / total_bytes
                    self.progressbar.set(percentage)
                
                # Update labels safely using after
                percent_str = d.get('_percent_str', '0.0%').strip()
                speed_str = d.get('_speed_str', '0 B/s').strip()
                eta_str = d.get('_eta_str', 'Unknown').strip()
                
                playlist_index = d.get('info_dict', {}).get('playlist_index', '?')
                playlist_count = d.get('info_dict', {}).get('playlist_count', '?')
                
                progress_text = f"Downloading Video {playlist_index} of {playlist_count} - {percent_str}"
                details_text = f"Speed: {speed_str} | ETA: {eta_str}"
                
                self.after(0, self.update_labels, progress_text, details_text)
            except Exception as e:
                pass
        
        elif d['status'] == 'finished':
            self.after(0, self.update_labels, "Finished video download, extracting audio/video...", "")
            self.after(0, self.progressbar.set, 1.0)

    def update_labels(self, progress_text, details_text):
        self.progress_label.configure(text=progress_text)
        self.details_label.configure(text=details_text)

    def download_thread(self, url, output_path, format_choice, resolution_choice, start_vid, end_vid):
        try:
            ydl_opts = {
                'outtmpl': os.path.join(output_path, '%(playlist_title)s', '%(playlist_index)s - %(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'ignoreerrors': True, # Skip unavailable videos
                'no_warnings': True,
                'quiet': True,
            }
            
            if start_vid:
                ydl_opts['playliststart'] = start_vid
            if end_vid:
                ydl_opts['playlistend'] = end_vid

            if format_choice == "MP3":
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:
                # MP4
                res_map = {
                    "1080p": "1080",
                    "720p": "720",
                    "480p": "480",
                    "360p": "360"
                }
                if resolution_choice == "Highest":
                    ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                elif resolution_choice == "Lowest":
                    ydl_opts['format'] = 'worstvideo[ext=mp4]+worstaudio[ext=m4a]/worst[ext=mp4]/worst'
                else:
                    res_val = res_map.get(resolution_choice, "1080")
                    ydl_opts['format'] = f'bestvideo[height<={res_val}][ext=mp4]+bestaudio[ext=m4a]/best[height<={res_val}][ext=mp4]/best'
                
                # Ensure mp4 merge if necessary
                ydl_opts['merge_output_format'] = 'mp4'

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.after(0, self.update_labels, "Fetching playlist information...", "")
                ydl.download([url])
                
            if not self.is_cancelled:
                self.after(0, self.download_complete)
            
        except Exception as e:
            if str(e) == "Download cancelled by user" or self.is_cancelled:
                self.after(0, self.download_cancelled)
            else:
                self.after(0, self.download_error, str(e))

    def start_download(self):
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube Playlist URL.")
            return
            
        output_path = self.download_path.get()
        if not output_path or not os.path.exists(output_path):
            messagebox.showerror("Error", "Please select a valid download directory.")
            return

        format_choice = self.format_var.get()
        resolution_choice = self.resolution_var.get()
        
        # Parse Start/End
        start_vid_str = self.start_entry.get().strip()
        end_vid_str = self.end_entry.get().strip()
        
        start_vid = None
        end_vid = None
        
        try:
            if start_vid_str:
                start_vid = int(start_vid_str)
            if end_vid_str:
                end_vid = int(end_vid_str)
        except ValueError:
            messagebox.showerror("Error", "Start and End video indices must be numbers.")
            return

        self.is_cancelled = False

        # Update UI
        self.download_btn.configure(state="disabled", text="Downloading...")
        self.cancel_btn.configure(state="normal", text="Cancel")
        self.url_entry.configure(state="disabled")
        self.start_entry.configure(state="disabled")
        self.end_entry.configure(state="disabled")
        self.browse_btn.configure(state="disabled")
        self.format_menu.configure(state="disabled")
        self.resolution_menu.configure(state="disabled")
        self.progressbar.set(0)
        
        # Start download thread
        thread = threading.Thread(target=self.download_thread, args=(url, output_path, format_choice, resolution_choice, start_vid, end_vid), daemon=True)
        thread.start()

    def download_complete(self):
        self.progress_label.configure(text="Download Complete!")
        self.details_label.configure(text="")
        self.progressbar.set(1.0)
        self.reset_ui()
        messagebox.showinfo("Success", "Playlist downloaded successfully!")

    def download_cancelled(self):
        self.progress_label.configure(text="Download Cancelled.")
        self.details_label.configure(text="")
        self.progressbar.set(0)
        self.reset_ui()
        messagebox.showinfo("Cancelled", "Download was cancelled.")

    def download_error(self, error_msg):
        self.progress_label.configure(text="Error occurred!")
        self.details_label.configure(text=error_msg)
        self.reset_ui()
        messagebox.showerror("Download Error", f"An error occurred during download:\n{error_msg}")

    def reset_ui(self):
        self.download_btn.configure(state="normal", text="Download Playlist")
        self.cancel_btn.configure(state="disabled", text="Cancel")
        self.url_entry.configure(state="normal")
        self.start_entry.configure(state="normal")
        self.end_entry.configure(state="normal")
        self.browse_btn.configure(state="normal")
        self.format_menu.configure(state="normal")
        if self.format_var.get() != "MP3":
            self.resolution_menu.configure(state="normal")


if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
