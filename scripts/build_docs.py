import sys
from pathlib import Path

import yaml
from markdown_it import MarkdownIt

docs_dir = Path(__file__).parent.parent / "docs"
sys.path.insert(0, str(docs_dir))

from plugins.code_switch import code_switch_plugin  # type: ignore  # noqa: E402


def load_docs_structure():
    """Load docs structure from YAML"""
    structure_file = Path("docs/structure.yaml")
    with open(structure_file, encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data.get("sections", [])


def validate_docs_structure():
    """Validate that all pages in structure have corresponding markdown files"""
    docs_structure = load_docs_structure()
    docs_content_dir = Path("docs")

    missing_files = []

    for section in docs_structure:
        for page in section["pages"]:
            slug = page["slug"]
            md_file = docs_content_dir / f"{slug}.md"
            if not md_file.exists():
                missing_files.append(f"{slug}.md")

    if missing_files:
        print("❌ Missing markdown files:")
        for file in missing_files:
            print(f"   - {file}")
        return False

    print("✅ All markdown files found")
    return True


def build_docs():
    """Convert markdown files to HTML templates using structure from YAML"""
    if not validate_docs_structure():
        print("Build aborted due to missing files")
        return False

    docs_content_dir = Path("docs")
    templates_dir = Path("app/web/templates/docs")
    templates_dir.mkdir(parents=True, exist_ok=True)

    md = MarkdownIt("commonmark", {"html": True, "linkify": True, "typographer": True})

    md.use(code_switch_plugin)

    docs_structure = load_docs_structure()

    # Get all slugs that should be built
    all_slugs = set()
    for section in docs_structure:
        for page in section["pages"]:
            all_slugs.add(page["slug"])

    # Build each page
    for slug in all_slugs:
        try:
            md_file = docs_content_dir / f"{slug}.md"

            # Read and parse markdown
            content = md_file.read_text(encoding="utf-8")
            html_content = md.render(content)

            # Create Jinja template
            template_content = f"""
{{% extends "docs/base.html" %}}

{{% block content %}}
{html_content}
{{% endblock %}}
"""

            # Write to templates directory
            output_file = templates_dir / f"{slug}.html"
            output_file.write_text(template_content, encoding="utf-8")
            print(f"Built {slug}.md -> {slug}.html")
        except Exception as e:
            print(f"❌ Failed to build page {slug}.md")
            raise e

    print(f"✅ Built {len(all_slugs)} documentation pages")
    return True


if __name__ == "__main__":
    build_docs()
