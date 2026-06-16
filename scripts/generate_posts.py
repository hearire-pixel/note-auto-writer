import os
import anthropic
from datetime import date
from pathlib import Path

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
INPUT_MEMO = os.environ.get("INPUT_MEMO", "")
INPUT_PLATFORMS = os.environ.get("INPUT_PLATFORMS", "all").lower()

TODAY = date.today().isoformat()

BASE_DIR = Path(__file__).parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"
DRAFTS_DIR = BASE_DIR / "drafts"


def load_style_prompt() -> str:
    style_file = PROMPTS_DIR / "hiro_note_prompt.md"
    if style_file.exists():
        return style_file.read_text(encoding="utf-8")
    return ""


def build_prompt(platform: str, style_prompt: str, memo: str) -> str:
    memo_section = f"\n\n## Today's memo\n{memo}" if memo else ""
    platform_instructions = {
        "note": "Write a full note article (blog post) in HIRO's style. Include title, body with sections, and closing message.",
        "instagram": "Write 3 Instagram story slides in HIRO's style. Each slide should be short (2-4 lines). Use line breaks and natural spacing.",
        "x": "Write a single X (Twitter) post in HIRO's style. Keep it under 140 characters. Poetic and touching.",
    }
    instruction = platform_instructions.get(platform, "Write content in HIRO's style.")

    return f"""{style_prompt}{memo_section}

## Task

{instruction}

Output only the content for this platform. Do not include explanations or headers about the task itself."""


def generate_content(client: anthropic.Anthropic, prompt: str) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def write_draft(platform: str, content: str) -> Path:
    platform_dir = DRAFTS_DIR / platform
    platform_dir.mkdir(parents=True, exist_ok=True)

    ext = "md" if platform == "note" else "txt"
    filename = platform_dir / f"{TODAY}_{platform}.{ext}"

    metadata = f"配信先: {platform}\n生成日: {TODAY}\n\n"
    filename.write_text(metadata + content, encoding="utf-8")
    print(f"Written: {filename}")
    return filename


def resolve_platforms(platforms_input: str) -> list[str]:
    all_platforms = ["note", "instagram", "x"]
    if platforms_input == "all":
        return all_platforms
    selected = [p.strip() for p in platforms_input.split(",") if p.strip() in all_platforms]
    return selected if selected else all_platforms


def main():
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY is not set")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    style_prompt = load_style_prompt()
    platforms = resolve_platforms(INPUT_PLATFORMS)

    print(f"Generating posts for platforms: {platforms}")
    print(f"Memo: {INPUT_MEMO[:100] if INPUT_MEMO else '(none)'}")

    for platform in platforms:
        print(f"\nGenerating {platform}...")
        prompt = build_prompt(platform, style_prompt, INPUT_MEMO)
        content = generate_content(client, prompt)
        write_draft(platform, content)

    print("\nDone.")


if __name__ == "__main__":
    main()
