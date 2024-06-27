from pathlib import Path


def add_to_gitignore(text: str):
    """
    Function to add a file to .gitignore if it is not there.
    """
    desc = "Added using Confhub"

    gitignore_path = Path('.gitignore')
    if not gitignore_path.exists():
        with gitignore_path.open('w') as f:
            f.write(f'\n#{desc}\n{text}\n')
    else:
        with gitignore_path.open('r') as f:
            lines = f.readlines()

        is_write = True
        for line in lines:
            if text in line:
                is_write = False

        if is_write:
            with gitignore_path.open('a') as f:
                f.write(f'\n#{desc}\n{text}\n')
