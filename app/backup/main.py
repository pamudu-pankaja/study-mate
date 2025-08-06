import re


def convert_static_paths(html_path, output_path=None):
    with open(html_path, "r", encoding="utf-8") as file:
        html = file.read()

    # Regex pattern to match paths like /app/static/css/..., /app/static/js/..., etc.
    pattern = r'(["\'\(])\/app\/static\/([^"\')]+)(["\'\)])'

    # Replace with Flask's url_for
    replaced_html = re.sub(
        pattern, r"\1{{ url_for(\'static\', filename=\'\2\') }}\3", html
    )

    if not output_path:
        output_path = html_path.replace(".html", "_flask.html")

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(replaced_html)

    print(f"✅ Converted and saved to: {output_path}")


# Example usage
convert_static_paths("app/templates/static_index.html")
