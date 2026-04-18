import json
import os

# حذف كل الملفات
if os.path.exists("data"):
    import shutil
    shutil.rmtree("data")
    print("✅ تم حذف مجلد data")

# إنشاء مجلد جديد
os.makedirs("data", exist_ok=True)

# اختبار الكتابة
test_data = {"test": "hello"}
with open("data/test.json", "w") as f:
    json.dump(test_data, f)

# اختبار القراءة
with open("data/test.json", "r") as f:
    data = json.load(f)
    print(f"✅ القراءة成功: {data}")

print("🎉 كل شيء يعمل بشكل طبيعي")