#!/usr/bin/env python3
"""Initialize an empty research project using the bundled project files."""
import argparse
import importlib.util
from datetime import date
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from urllib.parse import urlparse

WORKFLOW = Path(__file__).resolve().parents[1]
TEMPLATE = WORKFLOW / 'templates/project'
spec = importlib.util.spec_from_file_location('workflow', WORKFLOW / 'tools/workflow.py')
workflow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workflow)
RESERVED = {'.git', '.agents', '.codex', '.claude', '.aws'}


def git(path, *args):
    return subprocess.run(['git', '-C', str(path), *args], check=True,
                          text=True, stdout=subprocess.PIPE).stdout.strip()


def overleaf_remote(value):
    value = value.strip()
    if value.startswith('git@git.overleaf.com:'):
        project = value.split(':', 1)[1].removesuffix('.git')
        if re.fullmatch(r'[A-Za-z0-9]{8,}', project):
            return f'git@git.overleaf.com:{project}'
    elif re.fullmatch(r'[A-Za-z0-9]{8,}', value):
        return f'https://git.overleaf.com/{value}'
    else:
        url = urlparse(value)
        if url.scheme == 'https' and url.netloc in {'overleaf.com', 'www.overleaf.com', 'git.overleaf.com'}:
            project = url.path.removeprefix('/project/').strip('/').removesuffix('.git')
            if re.fullmatch(r'[A-Za-z0-9]{8,}', project):
                return f'https://git.overleaf.com/{project}'
    raise ValueError('expected an Overleaf project URL or project ID')


def check_templates():
    """Validate every template folder: required files, no development artifacts, known placeholders."""
    for name in ['AGENTS.md', 'project.md', 'journal/YYYY-MM-DD.md']:
        if not (TEMPLATE / name).is_file():
            raise ValueError(f'missing template file: {name}')
    for name in ['workflow.py', 'conventions.md', 'templates/manuscript/justfile',
                 'templates/repository/pyproject.toml']:
        if not (WORKFLOW / name).is_file():
            raise ValueError(f'missing workflow file: {name}')
    for folder in sorted(p for p in (WORKFLOW / 'templates').iterdir() if p.is_dir()):
        for path in folder.rglob('*'):
            if path.name in {'.git', '.venv', '__pycache__'}:
                raise ValueError(f'development artifact in template: {path}')
        # Only init supplies the AGENTS.md block; optional components must not use it.
        keys = [k for k in workflow.PLACEHOLDERS if folder == TEMPLATE or k != 'WORKFLOW_BLOCK']
        workflow.render(folder, dict.fromkeys(keys, 'check'))


def initialize(args):
    check_templates()
    if args.check:
        print('Template check passed.')
        return
    if not args.target or not args.title or not args.author:
        raise ValueError('target, --title, and --author are required')
    if not shutil.which('git'):
        raise ValueError('Git is required for initialization')
    target = Path(args.target).resolve(strict=True)
    if not target.is_dir():
        raise ValueError('target must be an existing empty directory')
    for entry in target.iterdir():
        if (entry.name in RESERVED and entry.is_dir() and not entry.is_symlink()
                and not any(entry.iterdir())):
            continue
        raise ValueError(f'target directory is not empty: {target}')
    slug = args.rename_to or target.name
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', slug):
        raise ValueError('directory name must be lowercase kebab-case')
    destination = target.with_name(slug)
    if destination != target and destination.exists():
        raise ValueError(f'renamed target already exists: {destination}')
    day = date.fromisoformat(args.date).isoformat()
    remote = overleaf_remote(args.overleaf_url) if args.overleaf_url else None
    values = dict(PROJECT_SLUG=slug, PROJECT_TITLE=args.title, PAPER_TITLE=args.title,
                  AUTHORS=args.author, AUTHOR=args.author, DESCRIPTION=args.desc or args.title,
                  STATUS=args.status, DATE_ISO=day, WORKFLOW_BLOCK=workflow.BLOCK)
    rendered = workflow.render(TEMPLATE, values)
    # Prepare everything before touching the target, including any network clone.
    with tempfile.TemporaryDirectory(prefix='research-init-') as temporary:
        stage = Path(temporary) / 'project'
        shutil.copytree(TEMPLATE, stage, symlinks=True)
        for name, text in rendered.items():
            (stage / name).write_text(text, encoding='utf-8')
        (stage / 'journal/YYYY-MM-DD.md').rename(stage / f'journal/{day}.md')
        (stage / 'bibliography').mkdir(exist_ok=True)
        (stage / f'bibliography/{slug}.bib').write_text('% Project bibliography.\n', encoding='utf-8')
        workflow.install(stage, metadata=dict(slug=slug, title=args.title, author=args.author))
        if args.repository:
            workflow.add(stage, 'repository')
        if remote or args.manuscript:
            workflow.add(stage, 'manuscript')
        if remote:
            checkout = Path(temporary) / 'overleaf'
            subprocess.run(['git', 'clone', '--origin', 'overleaf', remote, str(checkout)], check=True)
            # Preserve all remote files; supply only missing workflow configuration.
            for name in ['.latexmkrc', 'justfile', '.gitattributes', '.gitignore',
                         '.pre-commit-config.yaml', 'badness.toml']:
                if not (checkout / name).exists():
                    shutil.copy2(stage / 'manuscript' / name, checkout / name)
            shutil.rmtree(stage / 'manuscript')
            shutil.move(str(checkout), stage / 'manuscript')
        if destination != target:
            target.rename(destination)
            target = destination
        shutil.copytree(stage, target, dirs_exist_ok=True, symlinks=True)
    for name in ['repository', 'manuscript', '']:
        if name == 'manuscript' and remote:
            continue  # Never commit into the authoritative Overleaf checkout.
        repo = target / name
        if not repo.exists():
            continue
        git(repo, 'init', '-b', 'main')
        if args.commit:
            git(repo, 'add', '-A')
            git(repo, 'commit', '-m', f'Initialize {slug}' + (f' {name}' if name else ''))
    print(f'Initialized {target}. Edit project.md; develop privately in workspace/.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target', nargs='?')
    parser.add_argument('--check', action='store_true', help='validate the bundled template only')
    parser.add_argument('--rename-to')
    parser.add_argument('--title')
    parser.add_argument('--author')
    parser.add_argument('--desc')
    parser.add_argument('--status', default='Initial setup.')
    parser.add_argument('--overleaf-url')
    parser.add_argument('--commit', action='store_true', help='explicitly create initial local commits')
    parser.add_argument('--manuscript', action='store_true', help='create a manuscript repository now')
    parser.add_argument('--repository', action='store_true', help='create a shared artifact repository now')
    parser.add_argument('--date', default=os.environ.get('BOOTSTRAP_DATE', date.today().isoformat()))
    args = parser.parse_args()
    try:
        initialize(args)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'ERROR: {error}\n')


if __name__ == '__main__':
    main()
