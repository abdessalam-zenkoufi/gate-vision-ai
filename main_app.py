import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import shutil
import cv2
import face_recognition
import numpy as np
import pygame
from PIL import Image
import time
import datetime
import csv

# 1. التأكد من جميع المجلدات
os.makedirs("students_data/allowed", exist_ok=True)
os.makedirs("students_data/banned", exist_ok=True)
os.makedirs("assets", exist_ok=True)
os.makedirs("logs/images", exist_ok=True)

# 2. تهيئة ملف السجلات (CSV)
csv_file = "logs/access_logs.csv"
if not os.path.exists(csv_file):
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Name", "Status", "Orig_Img", "Sobel_Img", "Canny_Img", "Laplacian_Img"])

pygame.mixer.init()
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ================= حل مشكلة الحروف العربية في OpenCV =================
def imread_utf8(filename):
    im_buf_arr = np.fromfile(filename, dtype=np.uint8)
    return cv2.imdecode(im_buf_arr, cv2.IMREAD_COLOR)

def imwrite_utf8(filename, img):
    is_success, im_buf_arr = cv2.imencode(".jpg", img)
    if is_success:
        im_buf_arr.tofile(filename)

# ====================================================================

class UniversityGateApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("نظام البوابة الذكية للجامعة")
        self.geometry("650x700") 
        self.resizable(False, False)

        self.db_window = None
        self.sim_window = None
        self.logs_window = None 
        self.reg_cam_window = None # نافذة كاميرا التسجيل

        self.allowed_encodings, self.allowed_names = [], []
        self.banned_encodings, self.banned_names = [], []
        self.reload_database()

        self.title_label = ctk.CTkLabel(self, text="لوحة تحكم البوابة الذكية", font=ctk.CTkFont(size=28, weight="bold"))
        self.title_label.pack(pady=20)

        # --- قسم إضافة الطلاب (مسموح) ---
        self.frame_allowed = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_allowed.pack(pady=5)
        
        self.btn_add_allowed_file = ctk.CTkButton(
            self.frame_allowed, text="إضافة طالب (من ملف)", font=("Arial", 14, "bold"), fg_color="#28a745", hover_color="#218838", command=self.add_allowed_person)
        self.btn_add_allowed_file.pack(side="right", padx=5, ipadx=10, ipady=5)

        self.btn_add_allowed_cam = ctk.CTkButton(
            self.frame_allowed, text="إضافة طالب (بالكاميرا)", font=("Arial", 14, "bold"), fg_color="#20c997", hover_color="#17a2b8", command=lambda: self.open_registration_camera("allowed"))
        self.btn_add_allowed_cam.pack(side="left", padx=5, ipadx=10, ipady=5)

        # --- قسم إضافة الممنوعين (القائمة السوداء) ---
        self.frame_banned = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_banned.pack(pady=10)

        self.btn_add_banned_file = ctk.CTkButton(
            self.frame_banned, text="إضافة ممنوع (من ملف)", font=("Arial", 14, "bold"), fg_color="#dc3545", hover_color="#c82333", command=self.add_banned_person)
        self.btn_add_banned_file.pack(side="right", padx=5, ipadx=10, ipady=5)

        self.btn_add_banned_cam = ctk.CTkButton(
            self.frame_banned, text="إضافة ممنوع (بالكاميرا)", font=("Arial", 14, "bold"), fg_color="#e83e8c", hover_color="#d81b60", command=lambda: self.open_registration_camera("banned"))
        self.btn_add_banned_cam.pack(side="left", padx=5, ipadx=10, ipady=5)

        # --- الأزرار الأساسية ---
        self.btn_manage_db = ctk.CTkButton(
            self, text="إدارة قاعدة البيانات (الطلاب والممنوعين)", font=("Arial", 16, "bold"), fg_color="#6c757d", hover_color="#5a6268", command=self.open_database_manager)
        self.btn_manage_db.pack(pady=15, ipadx=20, ipady=8)

        self.btn_view_logs = ctk.CTkButton(
            self, text=" عرض سجلات العبور (مراقبة الحواف) ", font=("Arial", 16, "bold"), fg_color="#17a2b8", hover_color="#138496", command=self.open_logs_manager)
        self.btn_view_logs.pack(pady=10, ipadx=20, ipady=8)

        self.btn_simulate = ctk.CTkButton(
            self, text=" الدخول إلى محاكاة البوابة (بث مباشر) ", font=("Arial", 20, "bold"), fg_color="#007bff", hover_color="#0056b3", height=55, command=self.start_simulation)
        self.btn_simulate.pack(pady=20, ipadx=40)

    def bring_to_front(self, window):
        window.deiconify()   
        window.lift()        
        window.focus_force() 

    # ================= مزامنة وقواعد البيانات =================
    def reload_database(self):
        self.allowed_encodings, self.allowed_names = self.load_encodings("students_data/allowed")
        self.banned_encodings, self.banned_names = self.load_encodings("students_data/banned")

    def load_encodings(self, folder_path):
        encodings, names = [], []
        for filename in os.listdir(folder_path):
            img_path = os.path.join(folder_path, filename)
            img = imread_utf8(img_path) 
            if img is not None:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                encodes = face_recognition.face_encodings(img)
                if len(encodes) > 0:
                    encodings.append(encodes[0])
                    names.append(os.path.splitext(filename)[0])
        return encodings, names

    def add_allowed_person(self):
        filepath = filedialog.askopenfilename(title="اختر صورة الطالب", filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if filepath:
            shutil.copy(filepath, f"students_data/allowed/{os.path.basename(filepath)}")
            self.reload_database()
            if self.db_window and self.db_window.winfo_exists(): self.refresh_db_tabs()
            messagebox.showinfo("نجاح", "تمت الإضافة للمسموح لهم.")

    def add_banned_person(self):
        filepath = filedialog.askopenfilename(title="اختر صورة الممنوع", filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if filepath:
            shutil.copy(filepath, f"students_data/banned/{os.path.basename(filepath)}")
            self.reload_database()
            if self.db_window and self.db_window.winfo_exists(): self.refresh_db_tabs()
            messagebox.showinfo("نجاح", "تمت الإضافة للممنوعين.")

    # ================= إضافة شخص عبر الكاميرا والتحقق =================
    def open_registration_camera(self, person_type):
        if self.sim_window and self.sim_window.winfo_exists():
            messagebox.showwarning("تحذير", "الكاميرا مستخدمة حالياً في المحاكاة. الرجاء إغلاق نافذة المحاكاة أولاً.")
            return

        if self.reg_cam_window is None or not self.reg_cam_window.winfo_exists():
            self.reg_cam_window = ctk.CTkToplevel(self)
            title_ar = "تسجيل وجه مسموح (طالب)" if person_type == "allowed" else "تسجيل وجه ممنوع"
            self.reg_cam_window.title(title_ar)
            self.reg_cam_window.geometry("500x550")
            self.reg_cam_window.resizable(False, False)

            lbl_info = ctk.CTkLabel(self.reg_cam_window, text="يرجى النظر للكاميرا والضغط على زر الالتقاط", font=("Arial", 16))
            lbl_info.pack(pady=10)

            self.reg_lbl_camera = ctk.CTkLabel(self.reg_cam_window, text="")
            self.reg_lbl_camera.pack(pady=10)

            btn_color = "#28a745" if person_type == "allowed" else "#dc3545"
            self.btn_capture = ctk.CTkButton(
                self.reg_cam_window, text="التقاط الصورة والتحقق", font=("Arial", 18, "bold"), 
                fg_color=btn_color, height=45, command=lambda: self.capture_and_validate_face(person_type)
            )
            self.btn_capture.pack(pady=10)

            self.reg_video_capture = cv2.VideoCapture(0)
            self.current_reg_frame = None
            
            self.reg_cam_window.protocol("WM_DELETE_WINDOW", self.close_registration_camera)
            self.update_registration_feed()
        else:
            self.bring_to_front(self.reg_cam_window)

    def update_registration_feed(self):
        if not self.reg_cam_window or not self.reg_cam_window.winfo_exists():
            return
        
        ret, frame = self.reg_video_capture.read()
        if ret:
            self.current_reg_frame = frame.copy()
            cv2_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(cv2_image).resize((400, 300))
            ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(400, 300))
            self.reg_lbl_camera.configure(image=ctk_image)
            self.reg_lbl_camera.image = ctk_image
        
        self.reg_cam_window.after(20, self.update_registration_feed)

    def capture_and_validate_face(self, person_type):
        if self.current_reg_frame is None: return
        frame = self.current_reg_frame

        # 1. التحقق من وجود وجه (Validation)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # تصغير الصورة لتسريع الفحص
        small_rgb = cv2.resize(rgb_frame, (0, 0), fx=0.5, fy=0.5)
        face_locations = face_recognition.face_locations(small_rgb)

        if len(face_locations) == 0:
            messagebox.showerror("خطأ في الالتقاط", "الكاميرا لم تتعرف على أي وجه! يرجى التأكد من الإضاءة والنظر مباشرة للكاميرا.")
            return
        
        # 2. إذا تم إيجاد وجه، نطلب الاسم
        dialog = ctk.CTkInputDialog(text="تم التعرف على الوجه بنجاح.\nالرجاء إدخال اسم الشخص:", title="حفظ الصورة")
        name = dialog.get_input()

        if name and name.strip() != "":
            safe_name = name.replace(" ", "_").strip()
            save_path = f"students_data/{person_type}/{safe_name}.jpg"
            
            # حفظ الصورة بالدالة الداعمة للعربية
            imwrite_utf8(save_path, frame)
            
            # تحديث النظام اللحظي
            self.reload_database()
            if self.db_window and self.db_window.winfo_exists(): 
                self.refresh_db_tabs()
                
            messagebox.showinfo("نجاح", f"تم حفظ وجه '{name}' في قاعدة البيانات بنجاح.")
            self.close_registration_camera()

    def close_registration_camera(self):
        if hasattr(self, 'reg_video_capture') and self.reg_video_capture.isOpened():
            self.reg_video_capture.release()
        if self.reg_cam_window and self.reg_cam_window.winfo_exists():
            self.reg_cam_window.destroy()

    # ================= نافذة إدارة الطلاب =================
    def open_database_manager(self):
        if self.db_window is None or not self.db_window.winfo_exists():
            self.db_window = ctk.CTkToplevel(self)
            self.db_window.title("إدارة قاعدة البيانات")
            self.db_window.geometry("500x500")
            self.db_window.resizable(False, False)
            self.tabview = ctk.CTkTabview(self.db_window, width=450, height=450)
            self.tabview.pack(pady=10, padx=10, fill="both", expand=True)
            self.tabview.add("المسموح لهم")
            self.tabview.add("الممنوعين")
            self.refresh_db_tabs()
        else:
            self.bring_to_front(self.db_window)

    def refresh_db_tabs(self):
        for widget in self.tabview.tab("المسموح لهم").winfo_children(): widget.destroy()
        for widget in self.tabview.tab("الممنوعين").winfo_children(): widget.destroy()
        self.populate_tab("students_data/allowed", self.tabview.tab("المسموح لهم"))
        self.populate_tab("students_data/banned", self.tabview.tab("الممنوعين"))

    def populate_tab(self, folder_path, parent_frame):
        scroll_frame = ctk.CTkScrollableFrame(parent_frame)
        scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        if not os.path.exists(folder_path): return
        files = os.listdir(folder_path)
        for f in files:
            row_frame = ctk.CTkFrame(scroll_frame, fg_color="#333333")
            row_frame.pack(fill="x", pady=5, padx=5)
            ctk.CTkLabel(row_frame, text=os.path.splitext(f)[0], font=("Arial", 16, "bold")).pack(side="left", padx=15, pady=10)
            ctk.CTkButton(row_frame, text="حذف", fg_color="#dc3545", hover_color="#c82333", width=70,
                          command=lambda filepath=os.path.join(folder_path, f): self.delete_person(filepath)).pack(side="right", padx=15, pady=10)

    def delete_person(self, filepath):
        if messagebox.askyesno("تأكيد", "هل أنت متأكد من الحذف؟"):
            os.remove(filepath)
            self.reload_database()
            self.refresh_db_tabs()

    # ================= نافذة السجلات المتقدمة والحذف =================
    def open_logs_manager(self):
        if self.logs_window is None or not self.logs_window.winfo_exists():
            self.logs_window = ctk.CTkToplevel(self)
            self.logs_window.title("سجلات العبور وتحليل الحواف")
            self.logs_window.geometry("1000x600")
            
            lbl = ctk.CTkLabel(self.logs_window, text="سجلات تحليل الوجوه (Feature Extraction)", font=("Arial", 22, "bold"))
            lbl.pack(pady=10)

            scroll_frame = ctk.CTkScrollableFrame(self.logs_window)
            scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

            try:
                with open(csv_file, mode='r', encoding='utf-8') as file:
                    reader = list(csv.reader(file))[1:] 
                    reader.reverse()
            except Exception:
                reader = []

            if len(reader) == 0:
                ctk.CTkLabel(scroll_frame, text="لا توجد سجلات بعد.", font=("Arial", 16)).pack(pady=20)
                return

            for row in reader:
                ts, name, status, orig, sobel, canny, laplacian = row
                
                row_frame = ctk.CTkFrame(scroll_frame, border_width=2, border_color="#555")
                row_frame.pack(fill="x", pady=10, padx=5)

                text_color = "green" if status == "allowed" else "red" if status == "banned" else "orange"
                status_ar = "مسموح" if status == "allowed" else "ممنوع" if status == "banned" else "مجهول"
                
                info_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
                info_frame.pack(side="left", padx=10, pady=10)
                ctk.CTkLabel(info_frame, text=f"الوقت: {ts}", font=("Arial", 14)).pack(anchor="w")
                ctk.CTkLabel(info_frame, text=f"الاسم: {name}", font=("Arial", 16, "bold")).pack(anchor="w")
                ctk.CTkLabel(info_frame, text=f"النتيجة: {status_ar}", font=("Arial", 16, "bold"), text_color=text_color).pack(anchor="w")

                btn_del_log = ctk.CTkButton(
                    row_frame, text="حذف السجل", fg_color="#dc3545", hover_color="#c82333", width=80,
                    command=lambda r=row: self.delete_log_entry(r)
                )
                btn_del_log.pack(side="right", padx=15, pady=20)

                images_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
                images_frame.pack(side="right", padx=10, pady=10)

                paths = [orig, sobel, canny, laplacian]
                titles = ["الأصلية", "Sobel", "Canny", "Laplacian"]

                for i, img_path in enumerate(paths):
                    try:
                        pil_img = Image.open(img_path).resize((80, 80))
                        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(80, 80))
                        img_lbl_frame = ctk.CTkFrame(images_frame, fg_color="transparent")
                        img_lbl_frame.pack(side="left", padx=5)
                        ctk.CTkLabel(img_lbl_frame, image=ctk_img, text="").pack()
                        ctk.CTkLabel(img_lbl_frame, text=titles[i], font=("Arial", 12)).pack()
                    except:
                        pass
        else:
            self.bring_to_front(self.logs_window)

    def delete_log_entry(self, row_data):
        ts, name, status, orig, sobel, canny, laplacian = row_data
        
        if messagebox.askyesno("تأكيد الحذف", "هل أنت متأكد من حذف هذا السجل وصوره المرتبطة نهائياً؟"):
            for img_path in [orig, sobel, canny, laplacian]:
                if os.path.exists(img_path):
                    try:
                        os.remove(img_path)
                    except Exception as e:
                        pass

            try:
                with open(csv_file, mode='r', encoding='utf-8') as file:
                    lines = list(csv.reader(file))
                
                with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    for line in lines:
                        if len(line) > 0 and line[0] != ts:
                            writer.writerow(line)
            except PermissionError:
                messagebox.showerror("خطأ", "الرجاء إغلاق ملف access_logs.csv في Excel قبل محاولة الحذف.")
                return

            if self.logs_window and self.logs_window.winfo_exists():
                self.logs_window.destroy()
                self.open_logs_manager()

    # ================= منطق السجلات والفلاتر =================
    def save_log_and_filters(self, name, action, frame, face_location):
        top, right, bottom, left = face_location
        h, w, _ = frame.shape
        top, bottom = max(0, top), min(h, bottom)
        left, right = max(0, left), min(w, right)

        face_crop = frame[top:bottom, left:right]
        if face_crop.size == 0: return 

        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = name.replace(" ", "_")
        base_path = f"logs/images/{timestamp_str}_{safe_name}"

        orig_path = f"{base_path}_orig.jpg"
        sobel_path = f"{base_path}_sobel.jpg"
        canny_path = f"{base_path}_canny.jpg"
        laplacian_path = f"{base_path}_laplacian.jpg"

        imwrite_utf8(orig_path, face_crop)
        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)

        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel_combined = np.uint8(np.absolute(cv2.magnitude(sobelx, sobely)))
        imwrite_utf8(sobel_path, sobel_combined)

        canny = cv2.Canny(gray, 100, 200)
        imwrite_utf8(canny_path, canny)

        laplacian = np.uint8(np.absolute(cv2.Laplacian(gray, cv2.CV_64F)))
        imwrite_utf8(laplacian_path, laplacian)

        pretty_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([pretty_time, name, action, orig_path, sobel_path, canny_path, laplacian_path])

        if self.logs_window and self.logs_window.winfo_exists():
            self.logs_window.destroy()
            self.open_logs_manager()

    # ================= محاكاة البوابة =================
    def start_simulation(self):
        if self.reg_cam_window and self.reg_cam_window.winfo_exists():
            messagebox.showwarning("تحذير", "كاميرا التسجيل مفتوحة حالياً. الرجاء إغلاقها قبل بدء المحاكاة.")
            return

        if self.sim_window is None or not self.sim_window.winfo_exists():
            self.sim_window = ctk.CTkToplevel(self)
            self.sim_window.title("محاكاة البوابة - بث حي")
            self.sim_window.geometry("1000x650")
            self.sim_window.resizable(False, False)
            
            self.lbl_status = ctk.CTkLabel(self.sim_window, text="النظام في وضع الاستعداد...", font=("Arial", 20, "bold"), text_color="white")
            self.lbl_status.pack(pady=10)

            self.btn_scan = ctk.CTkButton(
                self.sim_window, text="محاولة العبور (فحص الوجه)", font=("Arial", 20, "bold"),
                fg_color="#ffc107", hover_color="#e0a800", text_color="black", height=50, command=self.trigger_scan
            )
            self.btn_scan.pack(pady=10)

            self.main_frame = ctk.CTkFrame(self.sim_window, fg_color="transparent")
            self.main_frame.pack(pady=10, padx=20, fill="both", expand=True)

            self.lbl_camera = ctk.CTkLabel(self.main_frame, text="")
            self.lbl_camera.pack(side="left", padx=10)

            try:
                self.gate_img_closed = ctk.CTkImage(Image.open("assets/gate_closed.jpg"), size=(450, 450))
                self.gate_img_opened = ctk.CTkImage(Image.open("assets/gate_opened.jpg"), size=(450, 450))
            except:
                messagebox.showerror("خطأ", "صورتي البوابة مفقودة من مجلد assets")
                self.sim_window.destroy()
                return

            self.lbl_gate_image = ctk.CTkLabel(self.main_frame, image=self.gate_img_closed, text="")
            self.lbl_gate_image.pack(side="right", padx=10)

            self.video_capture = cv2.VideoCapture(0)
            self.is_scanning = False 
            self.gate_open = False
            self.last_action_time = 0

            self.update_video_feed()
        else:
            self.bring_to_front(self.sim_window)

    def trigger_scan(self):
        self.is_scanning = True
        self.lbl_status.configure(text="جاري تحليل الوجه... يرجى النظر للكاميرا", text_color="cyan")

    def update_video_feed(self):
        if not self.sim_window.winfo_exists():
            self.video_capture.release()
            return

        ret, frame = self.video_capture.read()
        if ret:
            if self.is_scanning:
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_small_frame)
                
                if face_locations:
                    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                    encoding = face_encodings[0] 
                    
                    top, right, bottom, left = face_locations[0]
                    real_face_loc = (top*4, right*4, bottom*4, left*4)

                    name = "مجهول"
                    action = "unknown"

                    if len(self.banned_encodings) > 0:
                        banned_matches = face_recognition.compare_faces(self.banned_encodings, encoding, tolerance=0.5)
                        if True in banned_matches:
                            name = self.banned_names[banned_matches.index(True)]
                            action = "banned"

                    if action == "unknown" and len(self.allowed_encodings) > 0:
                        allowed_matches = face_recognition.compare_faces(self.allowed_encodings, encoding, tolerance=0.5)
                        if True in allowed_matches:
                            name = self.allowed_names[allowed_matches.index(True)]
                            action = "allowed"

                    self.execute_gate_action(action, name, frame, real_face_loc)
                    self.is_scanning = False 
                else:
                    self.lbl_status.configure(text="لم يتم العثور على وجه، يرجى المحاولة مجدداً", text_color="orange")
                    self.is_scanning = False 

            cv2_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(cv2_image).resize((450, 350))
            ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(450, 350))
            self.lbl_camera.configure(image=ctk_image)
            self.lbl_camera.image = ctk_image

        if self.gate_open and (time.time() - self.last_action_time > 4):
            self.lbl_gate_image.configure(image=self.gate_img_closed)
            self.lbl_status.configure(text="النظام في وضع الاستعداد...", text_color="white")
            self.gate_open = False

        self.sim_window.after(20, self.update_video_feed)

    def execute_gate_action(self, action_type, name, frame, face_location):
        self.last_action_time = time.time()
        
        self.save_log_and_filters(name, action_type, frame, face_location)

        if action_type == "allowed":
            self.lbl_gate_image.configure(image=self.gate_img_opened)
            self.lbl_status.configure(text=f"تم التعرف عليك: {name}. البوابة مفتوحة.", text_color="green")
            self.gate_open = True
        elif action_type == "banned":
            self.lbl_status.configure(text=f"إنذار! شخص ممنوع: {name} !!", text_color="red")
            try:
                pygame.mixer.music.load("assets/alarm.wav")
                pygame.mixer.music.play()
            except:
                pass
        else:
            self.lbl_status.configure(text="عذراً، شخص غير معروف. لا يمكن الدخول.", text_color="orange")

if __name__ == "__main__":
    app = UniversityGateApp()
    app.mainloop()