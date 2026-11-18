#!/usr/bin/env python3
"""Manage a project's shared research method; never migrate its scientific files."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

PACKAGE = Path(__file__).resolve().parent
RELATIVE = Path('skills/init-research-workflow/assets/workflow')
DEFAULT_SOURCE = 'https://github.com/maiani/research-project-template.git'
BEGIN = '<!-- BEGIN research-workflow -->'
END = '<!-- END research-workflow -->'


def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], text=True,
                                   stderr=subprocess.PIPE, timeout=90).strip()


def read_json(path, default=None):
    return json.loads(path.read_text()) if path.exists() else (default or {})


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def digest(package):
    return {str(p.relative_to(package)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(package.rglob('*')) if p.is_file()
            and not any(x in {'__pycache__', 'cache'} for x in p.relative_to(package).parts)
            and p.name != 'installed.json'}


def runtime(source):
    path = Path(source).resolve()
    return path / RELATIVE if (path / RELATIVE).is_dir() else path


def link_skills(root):
    folder = root / '.agents/skills'
    folder.mkdir(parents=True, exist_ok=True)
    for skill in (root / '.workflow/skills').iterdir():
        target = folder / skill.name
        expected = root / '.workflow/skills' / skill.name
        if target.is_symlink() and target.resolve() == expected.resolve():
            continue
        if target.exists() or target.is_symlink():
            print(f'Preserved existing skill: {target}')
            continue
        try:
            target.symlink_to(Path('../../.workflow/skills') / skill.name, target_is_directory=True)
        except OSError:
            print(f'Skill links unavailable; read {expected / "SKILL.md"} explicitly.')


def attach(root):
    path = root / 'AGENTS.md'
    text = path.read_text() if path.exists() else '# Research project\n'
    # Adopt without replacing any existing local rules, even an earlier managed block.
    if BEGIN not in text:
        block = '\n\n' + BEGIN + '''
## Shared research workflow

Local instructions and scientific choices override shared defaults.
Read `.workflow/conventions.md` for shared boundaries and session continuity.
Use only the relevant skill:

- Research: `.workflow/skills/research-work/SKILL.md`
- Manuscript and referee work: `.workflow/skills/research-manuscript/SKILL.md`
- Shared artifacts and outreach: `.workflow/skills/research-release/SKILL.md`

Check updates: `python .workflow/workflow.py check`.
Create optional structure only for a current task: `python .workflow/workflow.py add --help`.
''' + END + '\n'
        path.write_text(text.rstrip() + block)
    link_skills(root)


def ensure_owned(root):
    package = root / '.workflow'
    if package.is_symlink():
        raise ValueError('Editable installation: manage the development checkout separately.')
    if package.exists():
        metadata = read_json(package / 'installed.json')
        if not metadata or metadata.get('hashes') != digest(package):
            raise ValueError('Shared package has local changes or is not managed; preserve them before updating.')


def install(root, source_package=PACKAGE, origin=DEFAULT_SOURCE, revision='development', pin='', editable=False):
    root = root.resolve(strict=True)
    source_package = source_package.resolve(strict=True)
    if not (source_package / 'workflow.py').is_file():
        raise ValueError('Source is not a research workflow package')
    ensure_owned(root)
    target = root / '.workflow'
    attached = (root / 'workflow.json').exists()
    config = read_json(root / 'workflow.json')
    if revision == 'development':
        revision = 'snapshot:' + hashlib.sha256(json.dumps(digest(source_package), sort_keys=True).encode()).hexdigest()
    config.update(source=origin, revision=revision, pin=pin, mode='editable' if editable else 'snapshot')
    config.setdefault('updates', 'ask')
    config.setdefault('slug', root.name)
    config.setdefault('title', root.name)
    config.setdefault('author', '')
    # Stage before replacing the owned package; retain a recoverable backup on failure.
    with tempfile.TemporaryDirectory(prefix='.workflow-install-', dir=root) as temporary:
        stage = Path(temporary) / 'package'
        if editable:
            stage.symlink_to(source_package, target_is_directory=True)
        else:
            shutil.copytree(source_package, stage, ignore=shutil.ignore_patterns('__pycache__', 'cache', 'installed.json'))
            write_json(stage / 'installed.json', {'revision': revision, 'hashes': digest(stage)})
        backup = Path(temporary) / 'previous'
        if target.exists():
            target.rename(backup)
        try:
            stage.rename(target)
            write_json(root / 'workflow.json', config)
        except Exception:
            if target.is_symlink():
                target.unlink()
            elif target.exists():
                shutil.rmtree(target)
            if backup.exists():
                backup.rename(target)
            raise
    if attached:
        link_skills(root)
    else:
        attach(root)


def release(tags):
    versions = []
    for tag in tags:
        match = re.fullmatch(r'v?(\d+)\.(\d+)\.(\d+)', tag)
        if match:
            versions.append((tuple(map(int, match.groups())), tag))
    if not versions:
        raise ValueError('No stable release tags available; use update --to REF explicitly.')
    return max(versions)[1]


def update(root, to=None, unpin=False, source=None):
    config = read_json(root / 'workflow.json')
    ensure_owned(root)
    origin = source or config.get('source', DEFAULT_SOURCE)
    pin = '' if unpin else config.get('pin', '')
    if to:
        pin = to
    with tempfile.TemporaryDirectory(prefix='research-update-') as temporary:
        checkout = Path(temporary) / 'source'
        subprocess.run(['git', 'clone', '--quiet', '--no-checkout', '--', origin, str(checkout)],
                       check=True, timeout=120)
        selected = pin or release(git(checkout, 'tag', '--list').splitlines())
        revision = git(checkout, 'rev-parse', '--verify', '--end-of-options', selected + '^{commit}')
        git(checkout, 'checkout', '--quiet', '--detach', revision)
        script = checkout / RELATIVE / 'workflow.py'
        if not script.is_file():
            raise ValueError('Selected revision predates the updateable workflow package.')
        # Install using the selected version, never old logic against new assets.
        subprocess.run([sys.executable, str(script), '_install', str(root),
                        '--origin', origin, '--revision', revision, '--pin', pin], check=True)
        print(f'Updated shared workflow to {selected} ({revision[:12]}). Project files preserved.')


def check(root, force=False):
    config = read_json(root / 'workflow.json')
    if config.get('updates') == 'off':
        print('Update checks disabled.')
        return
    if config.get('mode') == 'editable':
        print('Editable workflow: updates are managed in the development checkout.')
        return
    cache = root / '.workflow/cache/check.json'
    prior = read_json(cache)
    if not force and time.time() - prior.get('time', 0) < 86400:
        print(prior['message'])
        return
    available = False
    try:
        origin = config.get('source', DEFAULT_SOURCE)
        output = subprocess.check_output(['git', 'ls-remote', '--tags', '--', origin],
                                         text=True, stderr=subprocess.PIPE, timeout=20)
        refs = dict(line.split()[::-1] for line in output.splitlines())
        if config.get('pin'):
            message = f'Workflow pinned to {config["pin"]}; use update --unpin to follow releases.'
        else:
            latest = release([ref.removeprefix('refs/tags/') for ref in refs if not ref.endswith('^{}')])
            sha = refs.get(f'refs/tags/{latest}^{{}}', refs[f'refs/tags/{latest}'])
            available = sha != config.get('revision')
            message = f'{latest}: ' + ('update available; run python .workflow/workflow.py update' if available else 'up to date')
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        message = f'Update check unavailable ({type(error).__name__}); research can continue.'
    cache.parent.mkdir(parents=True, exist_ok=True)
    write_json(cache, {'time': time.time(), 'message': message})
    print(message)
    if available and config.get('updates') == 'auto':
        update(root)


def add(root, component):
    config = read_json(root / 'workflow.json')
    destinations = {'manuscript': 'manuscript', 'repository': 'repository',
                    'outreach': 'manuscript/outreach', 'response': 'manuscript/submission'}
    destination = root / destinations[component]
    if component in {'outreach', 'response'} and not (root / 'manuscript/.git').exists():
        raise ValueError('Set up the authoritative manuscript repository first.')
    if destination.exists():
        raise ValueError(f'{destination} already exists; compare templates manually, without overwriting local files.')
    values = {'PROJECT_SLUG': config.get('slug', root.name), 'PROJECT_TITLE': config.get('title', root.name),
              'PAPER_TITLE': config.get('title', root.name), 'AUTHOR': config.get('author', ''),
              'AUTHORS': config.get('author', ''), 'DESCRIPTION': config.get('title', root.name),
              'DATE_ISO': datetime.now(timezone.utc).date().isoformat(), 'STATUS': 'Initial setup.'}
    with tempfile.TemporaryDirectory(prefix='research-component-') as temporary:
        stage = Path(temporary) / component
        shutil.copytree(PACKAGE / 'templates' / component, stage)
        for path in stage.rglob('*'):
            if path.is_file():
                def replace(match):
                    value = values[match[1]]
                    return json.dumps(value, ensure_ascii=False)[1:-1] if path.suffix == '.toml' else value
                path.write_text(re.sub(r'\{\{\s*([A-Z][A-Z0-9_]*)\s*\}\}', replace, path.read_text()))
        if component in {'manuscript', 'repository'}:
            git(stage, 'init', '-b', 'main')
        shutil.copytree(stage, destination)
    if component in {'manuscript', 'repository'}:
        ignore = root / '.gitignore'
        text = ignore.read_text() if ignore.exists() else ''
        if f'/{component}/' not in text.splitlines():
            ignore.write_text(text.rstrip() + f'\n/{component}/\n')
    print(f'Created {destination}; no files staged or committed.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    commands = parser.add_subparsers(dest='command', required=True)
    adopt = commands.add_parser('adopt', help='Attach to an existing project without restructuring it')
    adopt.add_argument('--editable', type=Path, help='Link a pilot project to a development checkout or runtime folder')
    adopt.add_argument('--source', default=DEFAULT_SOURCE)
    commands.add_parser('status')
    check_parser = commands.add_parser('check')
    check_parser.add_argument('--force', action='store_true')
    upgrade = commands.add_parser('update')
    group = upgrade.add_mutually_exclusive_group()
    group.add_argument('--to')
    group.add_argument('--unpin', action='store_true')
    upgrade.add_argument('--source', help='Use a repository URL or local Git repository')
    create = commands.add_parser('add', help='Create an optional component only when needed')
    create.add_argument('component', choices=['manuscript', 'repository', 'outreach', 'response'])
    internal = commands.add_parser('_install', help=argparse.SUPPRESS)
    internal.add_argument('target', type=Path)
    internal.add_argument('--origin', required=True)
    internal.add_argument('--revision', required=True)
    internal.add_argument('--pin', default='')
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.command == 'adopt':
            if (root / 'workflow.json').exists() or (root / '.workflow').exists():
                raise ValueError('Workflow already attached; use update or preserve it before switching modes.')
            install(root, runtime(args.editable) if args.editable else PACKAGE,
                    origin=args.source, editable=bool(args.editable))
        elif args.command == '_install':
            install(args.target, origin=args.origin, revision=args.revision, pin=args.pin)
        elif not (root / 'workflow.json').is_file():
            raise ValueError('No workflow.json found; run from the project root or use --root.')
        elif args.command == 'status':
            print(json.dumps(read_json(root / 'workflow.json'), indent=2))
        elif args.command == 'check':
            check(root, args.force)
        elif args.command == 'update':
            update(root, args.to, args.unpin, args.source)
        elif args.command == 'add':
            add(root, args.component)
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f'ERROR: {error}\n')


if __name__ == '__main__':
    main()
