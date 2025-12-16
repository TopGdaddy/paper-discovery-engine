import sys
import os

print("="*40)
print(f"🐍 Python Location: {sys.executable}")
print(f"📂 Current Directory: {os.getcwd()}")
print("="*40)

def test_import(module_name):
    try:
        __import__(module_name)
        print(f"✅ {module_name:<20} ... INSTALLED")
    except ImportError as e:
        print(f"❌ {module_name:<20} ... MISSING ({e})")

print("\nTesting your 'Basic Stack' libraries:")
test_import("requests")
test_import("feedparser")
test_import("bs4")
test_import("sqlalchemy")
test_import("dotenv")

print("\nTesting your Project Structure:")
try:
    import src.scraper
    print(f"✅ {'src.scraper':<20} ... FOUND")
except ImportError as e:
    print(f"❌ {'src.scraper':<20} ... NOT FOUND ({e})")

print("="*40)
