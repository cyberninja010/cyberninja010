import itertools
import string
import time
import random
import threading
from rich.console import Console
from rich.progress import Progress
from concurrent.futures import ThreadPoolExecutor

# إعداد واجهة المستخدم
console = Console()

# دالة لتخمين كلمات المرور بالقوة الغاشمة
def guess_password(guess, actual_password, username):
    if guess == actual_password:
        console.print(f"\n\n[green]Password found for Instagram user '{username}': {guess}[/green]")
        return True
    return False

def brute_force_password(actual_password, min_length, max_length, username, stop_event):
    # تعريف مجموعة الأحرف (الحروف الصغيرة، الكبيرة، والأرقام، والرموز)
    characters = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation

    # تجربة جميع التركيبات الممكنة من الطول الأدنى إلى الطول الأقصى
    for password_length in range(min_length, max_length + 1):
        console.print(f"\nTrying passwords of length: {password_length}")
        with Progress() as progress:
            task = progress.add_task("[cyan]Trying passwords...", total=len(characters) ** password_length)

            with ThreadPoolExecutor() as executor:
                futures = []

                for guess in itertools.product(characters, repeat=password_length):
                    if stop_event.is_set():  # تحقق مما إذا تم إيقاف العملية
                        console.print("\n[red]تم إيقاف التخمين بواسطة المستخدم.[/red]")
                        return

                    guess_password_str = ''.join(guess)
                    futures.append(executor.submit(guess_password, guess_password_str, actual_password, username))
                    progress.update(task, advance=1)  # تحديث تقدم المهمة

                    # إضافة تمويه عشوائي (فرصة 20% للعرض)
                    if random.random() < 0.3:  # 30% فرصة لإظهار تمويه
                        console.print(f"[DEBUG] Attempting: {guess_password_str} - Processing...", end="\r")

                    # إضافة نتائج وهمية
                    if random.random() < 0.1:  # 10% فرصة لإظهار نتيجة وهمية
                        fake_password = ''.join(random.choices(characters, k=password_length))
                        console.print(f"[FAKE] Trying non-existing password: {fake_password}", end="\r")

                    # التحقق من نتائج التخمين
                    for future in futures:
                        if future.result():  # إذا كانت الكلمة الصحيحة، اوقف العملية
                            return

    console.print(f"\n[red]Password for Instagram user '{username}' not found.[/red]")

# دالة لإيقاف العملية عند الطلب
def stop_brute_force(stop_event):
    input("\n[blue]اضغط Enter لإيقاف التخمين...[/blue]")
    stop_event.set()

# إدخال اسم المستخدم
username = input("أدخل اسم المستخدم على إنستغرام: ")

# إدخال الطول الأدنى لكلمة المرور
min_length = int(input("أدخل الطول الأدنى لكلمة المرور: "))

# إدخال الطول الأقصى لكلمة المرور
max_length = int(input("أدخل الطول الأقصى لكلمة المرور: "))

# توليد كلمة مرور عشوائية لاستخدامها في التخمين
actual_password_length = random.randint(min_length, max_length)
actual_password = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation, k=actual_password_length))
console.print(f"\n[blue]تم توليد كلمة المرور العشوائية: {actual_password}[/blue] (هذا فقط للاختبار، لن تُستخدم في التخمين الفعلي)")

# إنشاء حدث لإيقاف العملية
stop_event = threading.Event()
stop_thread = threading.Thread(target=stop_brute_force, args=(stop_event,))
stop_thread.start()

# قياس الوقت المستغرق
start_time = time.time()
brute_force_password(actual_password, min_length, max_length, username, stop_event)
# حساب الوقت المستغرق
end_time = time.time()
print(f"\n\n[cyan]الوقت المستغرق: {end_time - start_time:.2f} ثوانٍ[/cyan]")
