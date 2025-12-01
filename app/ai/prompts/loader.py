from pathlib import Path


class Prompts:
    def __init__(self):
        prompts_dir = Path(__file__).parent

        for md_file in prompts_dir.glob("*.md"):
            prompt_name = md_file.stem
            with open(md_file, "r", encoding="utf-8") as f:
                setattr(self, prompt_name, f.read())


prompts = Prompts()
