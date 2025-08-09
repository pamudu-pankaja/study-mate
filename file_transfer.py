import os
import re
import shutil
import argparse

def flask_to_static(src_html, dst_html):
    with open(src_html, "r", encoding="utf-8") as f:
        html = f.read()

    html = re.sub(r"\{\{\s*url_for\('static',\s*filename='(.*?)'\)\s*\}\}", r"static/\1", html)
    os.makedirs(os.path.dirname(dst_html), exist_ok=True)

    with open(dst_html, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Converted Flask ➜ Static: {dst_html}")


def static_to_flask(src_html, dst_html):
    with open(src_html, "r", encoding="utf-8") as f:
        html = f.read()

    html = re.sub(r'static/([a-zA-Z0-9_\-./]+)', r"{{ url_for('static', filename='\1') }}", html)
    os.makedirs(os.path.dirname(dst_html), exist_ok=True)

    with open(dst_html, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Converted Static ➜ Flask: {dst_html}")


def copy_static(src_static, dst_static):
    if os.path.exists(dst_static):
        shutil.rmtree(dst_static)
    shutil.copytree(src_static, dst_static)
    print(f"✅ Copied static files from {src_static} to {dst_static}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert between Flask-style and static HTML paths.")
    parser.add_argument("--to-static", action="store_true", help="Convert Flask ➜ Static")
    parser.add_argument("--to-flask", action="store_true", help="Convert Static ➜ Flask")
    args = parser.parse_args()

    # HTML paths
    flask_input_html = "app/templates/index.html"
    flask_output_html = "app/templates/static_index.html"
    static_output_html = "docs/index.html"
    static_input_html = "docs/index.html"

    # Static asset paths
    flask_static = "app/static"
    static_static = "docs/static"

    if args.to_static:
        flask_to_static(flask_input_html, static_output_html)
        copy_static(flask_static, static_static)
    elif args.to_flask:
        static_to_flask(static_input_html, flask_output_html)
        copy_static(static_static, flask_static)
    else:
        print("⚠️ Please use either --to-static or --to-flask")