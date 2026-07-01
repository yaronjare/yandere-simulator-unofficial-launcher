import config
from config import *
import zipfile
import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox
import threading
import io
import base64
import requests
import customtkinter as ctk
from PIL import Image, ImageTk
import webbrowser
import ctypes  
import gc
import time

gc.set_threshold(50, 5, 5)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_custom_font(font_filename):
    font_path = resource_path(font_filename)
    if os.path.exists(font_path):
        ctypes.windll.gdi32.AddFontResourceExW(font_path, 0x10, 0)

def get_system_language():
    try:
        if ctypes.windll.kernel32.GetUserDefaultUILanguage() == 1049:
            return "RU"
    except:
        pass
    return "EN"


try:
    import assets
    POSEMOD_ZIP_BASE64 = getattr(assets, 'POSEMOD_ZIP_BASE64', None)
except ImportError:
    POSEMOD_ZIP_BASE64 = None

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

load_custom_font(FONT_FILE)

class AnimatedButton(ctk.CTkButton):
    def __init__(self, *args, **kwargs):
        if "border_width" not in kwargs:
            kwargs["border_width"] = 1
        if "border_color" not in kwargs:
            kwargs["border_color"] = PASTEL_BORDER
        super().__init__(*args, **kwargs)


class YandereLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Yandere Simulator Launcher")
        self.geometry("560x420") 
        self.resizable(False, False)
        self.configure(fg_color=WHITE_COLOR)
        
        if os.path.exists(resource_path(ICON_NAME)):
            self.iconbitmap(resource_path(ICON_NAME))
        
        self.downloading = False
        self.cancelled = False
        self.current_lang = get_system_language()

        self.font_title = ctk.CTkFont(family=FONT_FAMILY, size=24, weight="bold")
        self.font_ui = ctk.CTkFont(family=FONT_FAMILY, size=11, weight="normal")
        self.font_status = ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")
        self.font_btn = ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")
        self.font_links = ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold")

        self.init_interface()
        self.check_game_status()
        self.update_localization()
        
        self.after(200, self._force_garbage_collection)

    def _force_garbage_collection(self):
        gc.collect()

    def init_interface(self):
        self.canvas = tk.Canvas(self, width=600, height=420, bd=0, highlightthickness=0, bg=WHITE_COLOR)
        self.canvas.pack(fill="both", expand=True)

        bg_path = resource_path(BG_IMAGE_NAME)
        if os.path.exists(bg_path):
            with Image.open(bg_path) as img:
                target_w, target_h = 240, 390  
                img_w, img_h = img.size
                
                ratio = max(target_w / img_w, target_h / img_h)
                new_w = int(img_w * ratio)
                new_h = int(img_h * ratio)
                
                img_resized = img.resize((new_w, new_h), Image.Resampling.BILINEAR)
                left = (new_w - target_w) / 2
                top = (new_h - target_h) / 2
                right = (new_w + target_w) / 2
                bottom = (new_h + target_h) / 2
                
                img_cropped = img_resized.crop((left, top, right, bottom))
                self.ayano_img = ImageTk.PhotoImage(img_cropped)
                self.canvas.create_image(560, 420, image=self.ayano_img, anchor="se")
                
                del img_resized, img_cropped
            gc.collect()

        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.canvas.create_window(280, 25, window=self.top_bar, width=520, height=40)

        self.right_bar = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.right_bar.pack(side="right")

        self.lang_switch = ctk.CTkSegmentedButton(
            self.right_bar, values=["RU", "EN"], command=self.change_language,
            font=self.font_ui, fg_color=PASTEL_BG, selected_color=PINK_MAIN, 
            text_color=BLACK_COLOR, unselected_color=PASTEL_BG, unselected_hover_color=PASTEL_BORDER
        )
        self.lang_switch.set(self.current_lang)
        self.lang_switch.pack(side="top", anchor="e")

        self.content_frame = ctk.CTkFrame(
            self, corner_radius=12, 
            fg_color=PASTEL_BG, 
            border_width=2, 
            border_color=PASTEL_BORDER
        )
        self.canvas.create_window(165, 225, window=self.content_frame, width=290)

        logo_path = resource_path(LOGO_IMAGE_NAME)
        self.has_logo_img = False
        
        if os.path.exists(logo_path):
            try:
                with Image.open(logo_path) as logo_img:
                    logo_img.thumbnail((270, 80), Image.Resampling.BILINEAR) 
                    self.logo_image_tk = ImageTk.PhotoImage(logo_img)
                    
                    self.title_label = tk.Label(
                        self.content_frame, image=self.logo_image_tk, 
                        bg=PASTEL_BG, bd=0, highlightthickness=0
                    )
                    self.title_label.pack(pady=(12, 2))
                    self.has_logo_img = True
            except:
                pass

        if not self.has_logo_img:
            self.title_label = ctk.CTkLabel(self.content_frame, text="Yandere Sim", font=self.font_title, text_color=PINK_RUN)
            self.title_label.pack(pady=(8, 2))

        self.subtitle = ctk.CTkLabel(self.content_frame, text="", font=self.font_ui, text_color=BLACK_COLOR)
        self.subtitle.pack(pady=(0, 2))

        self.status = ctk.CTkLabel(self.content_frame, text="", font=self.font_status, text_color=BLACK_COLOR)
        self.status.pack(pady=1)

        self.progress = ctk.CTkProgressBar(self.content_frame, width=250, height=8, fg_color=WHITE_COLOR, progress_color=PINK_MAIN)
        self.progress.pack(pady=3)
        self.progress.set(0)

        self.btn_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.btn_frame.pack(pady=1)

        self.download_btn = AnimatedButton(
            self.btn_frame, text="", width=160, height=30, font=self.font_btn,
            fg_color=PINK_MAIN, hover_color=PINK_MAIN_HOVER, text_color=BLACK_COLOR, command=self.start_download
        )
        self.download_btn.grid(row=0, column=0, padx=2)

        self.cancel_btn = AnimatedButton(
            self.btn_frame, text="", width=85, height=30, font=self.font_btn,
            fg_color=PASTEL_CANCEL, hover_color=PASTEL_CANCEL_HOVER, text_color=BLACK_COLOR, command=self.cancel_download, state="disabled",
            border_color=PASTEL_CANCEL
        )
        self.cancel_btn.grid(row=0, column=1, padx=2)

        self.check_updates_btn = AnimatedButton(
            self.content_frame, text="", width=250, height=30, font=self.font_btn,
            fg_color=PINK_UP, hover_color=PINK_UP_HOVER, text_color=BLACK_COLOR, command=self.start_check_updates,
            border_color=PINK_UP
        )
        self.check_updates_btn.pack(pady=2)

        self.posemod_btn = AnimatedButton(
            self.content_frame, text="", width=250, height=30, font=self.font_btn,
            fg_color=PINK_MOD, hover_color=PINK_MOD_HOVER, text_color=BLACK_COLOR, command=self.start_posemod_install,
            border_color=PINK_MOD
        )
        self.posemod_btn.pack(pady=2)

        self.run_btn = AnimatedButton(
            self.content_frame, text="", width=250, height=32, font=self.font_btn,
            fg_color=PINK_RUN, hover_color=PINK_RUN_HOVER, text_color=BLACK_COLOR, command=self.run_game,
            border_color=PINK_RUN
        )
        self.run_btn.pack(pady=(2, 4))

        self.links_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.links_frame.pack(pady=(2, 8))

        self.site_btn = AnimatedButton(
            self.links_frame, text="Site", width=78, height=22, font=self.font_links,
            fg_color=PINK_UP, hover_color=PINK_UP_HOVER, text_color=BLACK_COLOR,
            command=lambda: webbrowser.open(URL_SITE), border_color=PINK_UP
        )
        self.site_btn.grid(row=0, column=0, padx=3)

        self.blog_btn = AnimatedButton(
            self.links_frame, text="Blog", width=78, height=22, font=self.font_links,
            fg_color=PINK_UP, hover_color=PINK_UP_HOVER, text_color=BLACK_COLOR,
            command=lambda: webbrowser.open(URL_BLOG), border_color=PINK_UP
        )
        self.blog_btn.grid(row=0, column=1, padx=3)

        self.discord_btn = AnimatedButton(
            self.links_frame, text="Discord", width=78, height=22, font=self.font_links,
            fg_color=PINK_UP, hover_color=PINK_UP_HOVER, text_color=BLACK_COLOR,
            command=lambda: webbrowser.open(URL_DISCORD), border_color=PINK_UP
        )
        self.discord_btn.grid(row=0, column=2, padx=3)

    def change_language(self, lang):
        self.current_lang = lang
        self.update_localization()

    def check_game_status(self):
        return os.path.exists(os.path.join(GAME_DIR, EXE_NAME))

    def update_localization(self):
        lang_data = LOCALIZATION[self.current_lang]
        self.subtitle.configure(text=lang_data["subtitle"])
        self.cancel_btn.configure(text=lang_data["btn_cancel"])
        self.posemod_btn.configure(text=lang_data["btn_posemod"])
        self.check_updates_btn.configure(text=lang_data["btn_check_updates"])
        self.run_btn.configure(text=lang_data["btn_run"])
            
        game_exists = self.check_game_status()
        if game_exists:
            self.download_btn.configure(text=lang_data["btn_redownload"])
        else:
            self.download_btn.configure(text=lang_data["btn_download"])

        if not self.downloading:
            if game_exists:
                self.update_status(lang_data["status_installed"], BLACK_COLOR)
            else:
                self.update_status(lang_data["status_ready"], BLACK_COLOR)

    def update_status(self, text, color=BLACK_COLOR):
        self.status.configure(text=text, text_color=color)
        self.update()

    def start_download(self):
        if self.downloading: return
        self.downloading = True
        self.cancelled = False
        self.download_btn.configure(state="disabled")
        self.posemod_btn.configure(state="disabled")
        self.check_updates_btn.configure(state="disabled")
        self.run_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.progress.set(0)
        threading.Thread(target=self.download_thread, daemon=True).start()

    def download_thread(self):
        lang_data = LOCALIZATION[self.current_lang]
        try:
            self.update_status(lang_data["status_preparing"])
            if not os.path.exists(GAME_DIR): os.makedirs(GAME_DIR, exist_ok=True)

            self.update_status(lang_data["status_downloading"])
            
            fresh_url = f"{ZIP_URL}?t={int(time.time())}"
            downloaded = 0
            total_size = 0
            
            try:
                head_resp = requests.head(fresh_url, timeout=15, allow_redirects=True)
                total_size = int(head_resp.headers.get('content-length', 0))
            except:
                pass

            if os.path.exists(ZIP_FILENAME): 
                os.remove(ZIP_FILENAME)

            max_retries = 10
            retry_count = 0
            chunk_count = 0

            while downloaded < total_size or total_size == 0:
                if self.cancelled: break
                
                headers = {}
                if downloaded > 0:
                    headers['Range'] = f"bytes={downloaded}-"

                try:
                    response = requests.get(fresh_url, headers=headers, stream=True, timeout=30)
                    
                    if response.status_code == 200 and downloaded > 0:
                        downloaded = 0
                        if os.path.exists(ZIP_FILENAME): os.remove(ZIP_FILENAME)

                    response.raise_for_status()
                    
                    if total_size == 0:
                        total_size = int(response.headers.get('content-length', 0))

                    with open(ZIP_FILENAME, 'ab') as f:
                        for data in response.iter_content(1048576):
                            if self.cancelled: break
                            f.write(data)
                            downloaded += len(data)
                            
                            chunk_count += 1
                            if chunk_count % 10 == 0:
                                gc.collect()
                                
                            if total_size > 0:
                                progress = downloaded / total_size
                                self.progress.set(progress)
                                prefix = "Ход" if self.current_lang == "RU" else "Progress"
                                self.update_status(f"{prefix}: {progress*100:.1f}%")
                            self.update()
                            
                    if downloaded >= total_size and total_size > 0:
                        break

                except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
                    retry_count += 1
                    if retry_count > max_retries:
                        raise Exception(f"Слишком много сбоев сети ({retry_count}). Скачивание прервано.")
                    
                    prefix_err = "Обрыв связи. Переподключение" if self.current_lang == "RU" else "Conn lost. Reconnecting"
                    self.update_status(f"{prefix_err} ({retry_count}/{max_retries})...")
                    time.sleep(3)
                    continue

            if self.cancelled:
                if os.path.exists(ZIP_FILENAME): os.remove(ZIP_FILENAME)
                self.update_localization()
                return

            self.update_status(lang_data["status_unpacking"])
            gc.collect()
            with zipfile.ZipFile(ZIP_FILENAME, 'r') as zip_ref:
                zip_ref.extractall(GAME_DIR)
            if os.path.exists(ZIP_FILENAME): os.remove(ZIP_FILENAME)
            
            try:
                head_resp = requests.head(fresh_url, timeout=15, allow_redirects=True)
                server_date = head_resp.headers.get("Last-Modified", "")
                if server_date:
                    with open(VERSION_FILE, "w", encoding="utf-8") as f:
                        f.write(server_date)
            except:
                pass

            self.progress.set(1.0)
            messagebox.showinfo(lang_data["msg_success_title"], lang_data["msg_success_text"])
            
        except Exception as e:
            messagebox.showerror(lang_data["msg_error_title"], f"{lang_data['status_error']}:\n{str(e)}")
        finally:
            self.downloading = False
            self.download_btn.configure(state="normal")
            self.posemod_btn.configure(state="normal")
            self.check_updates_btn.configure(state="normal")
            self.run_btn.configure(state="normal")
            self.cancel_btn.configure(state="disabled")
            self.update_localization()
            gc.collect()

    def start_check_updates(self):
        if self.downloading: return
        self.check_updates_btn.configure(state="disabled")
        threading.Thread(target=self.check_updates_thread, daemon=True).start()

    def check_updates_thread(self):
        lang_data = LOCALIZATION[self.current_lang]
        self.update_status(lang_data["status_checking_updates"])
        try:
            fresh_url = f"{ZIP_URL}?t={int(time.time())}"
            response = requests.head(fresh_url, timeout=15, allow_redirects=True)
            response.raise_for_status()
            server_date = response.headers.get('Last-Modified')
            
            if not server_date:
                server_date = response.headers.get('content-length', '0')

            if not self.check_game_status():
                if messagebox.askyesno(lang_data["msg_update_avail_title"], lang_data["msg_update_avail_text"]):
                    self.after(10, self.start_download)
                return

            local_date = ""
            if not os.path.exists(VERSION_FILE):
                try:
                    with open(VERSION_FILE, "w", encoding="utf-8") as f:
                        f.write(server_date)
                    local_date = server_date
                except:
                    pass
            else:
                try:
                    with open(VERSION_FILE, "r", encoding="utf-8") as f:
                        local_date = f.read().strip()
                except:
                    pass
            
            if server_date == local_date and local_date != "":
                messagebox.showinfo(lang_data["msg_up_to_date_title"], lang_data["msg_up_to_date_text"])
            else:
                if messagebox.askyesno(lang_data["msg_update_avail_title"], lang_data["msg_update_avail_text"]):
                    self.after(10, self.start_download)
        except Exception as e:
            messagebox.showerror(lang_data["msg_error_title"], f"{lang_data['status_error']}:\n{str(e)}")
        finally:
            self.check_updates_btn.configure(state="normal")
            self.update_localization()
            gc.collect()

    def start_posemod_install(self):
        lang_data = LOCALIZATION[self.current_lang]
        if not self.check_game_status():
            messagebox.showwarning(lang_data["msg_warn_title"], lang_data["msg_pm_warn"])
            return
        if POSEMOD_ZIP_BASE64 is None:
            messagebox.showerror(lang_data["msg_error_title"], lang_data["msg_pm_missing"])
            return
            
        self.downloading = True
        self.download_btn.configure(state="disabled")
        self.posemod_btn.configure(state="disabled")
        self.check_updates_btn.configure(state="disabled")
        self.run_btn.configure(state="disabled")
        self.progress.set(0)
        threading.Thread(target=self.posemod_thread, daemon=True).start()

    def posemod_thread(self):
        lang_data = LOCALIZATION[self.current_lang]
        try:
            self.update_status(lang_data["status_pm_unpacking"])
            self.progress.set(0.3)
            self.update()
            
            zip_bytes = base64.b64decode(POSEMOD_ZIP_BASE64)
            zip_buffer = io.BytesIO(zip_bytes)
            
            with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
                top_level_dir = zip_ref.namelist()[0].split('/')[0]
                
                if top_level_dir.lower().startswith("posemod") and len(zip_ref.namelist()) > 1:
                    for member in zip_ref.infolist():
                        if member.filename.startswith(top_level_dir + '/'):
                            parts = member.filename.split('/')
                            new_subpath = os.path.join(*parts[1:])
                            if not new_subpath: continue
                            tgt_path = os.path.join(GAME_DIR, new_subpath)
                            if member.is_dir():
                                os.makedirs(tgt_path, exist_ok=True)
                            else:
                                os.makedirs(os.path.dirname(tgt_path), exist_ok=True)
                                with open(tgt_path, 'wb') as dst:
                                    dst.write(zip_ref.read(member.filename))
                else:
                    zip_ref.extractall(GAME_DIR)
                    
            self.progress.set(1.0)
            messagebox.showinfo("PoseMod", lang_data["status_pm_success"])
        except Exception as e:
            messagebox.showerror(lang_data["msg_error_title"], f"{lang_data['status_error']}:\n{str(e)}")
        finally:
            self.downloading = False
            self.download_btn.configure(state="normal")
            self.posemod_btn.configure(state="normal")
            self.check_updates_btn.configure(state="normal")
            self.run_btn.configure(state="normal")
            self.progress.set(0)
            self.update_localization()
            gc.collect()

    def cancel_download(self):
        lang_data = LOCALIZATION[self.current_lang]
        if messagebox.askyesno(lang_data["msg_cancel_title"], lang_data["msg_cancel_text"]): self.cancelled = True

    def run_game(self):
        lang_data = LOCALIZATION[self.current_lang]
        exe_path = os.path.join(GAME_DIR, EXE_NAME)
        if self.check_game_status():
            try:
                subprocess.Popen([exe_path], cwd=GAME_DIR)
                self.after(1500, self.quit)
            except Exception as e: messagebox.showerror(lang_data["msg_error_title"], str(e))
        else:
            messagebox.showwarning(lang_data["msg_warn_title"], lang_data["msg_warn_text"])

    def run(self): self.mainloop()

if __name__ == "__main__":
    app = YandereLauncher()
    app.pack_propagate(False) 
    app.run()
