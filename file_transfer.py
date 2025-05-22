import os
import shutil

# Paths
src_html = "app/templates/static_index.html"
dst_html = "docs/index.html"
src_static = "app/static"
dst_static = "docs/static"

# Step 1: Copy and fix HTML
with open(src_html, "r", encoding="utf-8") as f:
    html = f.read()

# Replace /app/static/ with static/
html = html.replace("/app/static/", "static/")

# Create docs folder if it doesn't exist
os.makedirs("docs", exist_ok=True)

# Write the updated HTML to docs/index.html
with open(dst_html, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Copied and updated HTML to {dst_html}")

# Step 2: Copy static files
if os.path.exists(dst_static):
    shutil.rmtree(dst_static)  # Clean old static files

shutil.copytree(src_static, dst_static)
print(f"✅ Copied static files from {src_static} to {dst_static}")
