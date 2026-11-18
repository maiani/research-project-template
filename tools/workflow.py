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

PACKAGE = Path(__file__).resolve().parents[1]
RELATIVE = Path('tools/workflow.py')
CONTENTS = ('workflow.py', 'conventions.md', 'skills', 'tools', 'templates', 'scaffold', '.gitignore')
DEFAULT_SOURCE = 'https://github.com/maiani/research-project-template.git'
VERSION = re.compile(r'v?(\d+)\.(\d+)\.(\d+)')
BEGIN = '<!-- BEGIN research-workflow -->'
END = '<!-- END research-workflow -->'


def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], text=True,
                                   stderr=subprocess.PIPE, timeout=90).strip()


def read_json(path, default=None):
    return json.loads(path.read_text()) if path.exists() else (default or {})


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def digest(package, selected=False):
    """Hash package files; `selected` limits a source checkout to the kit contents."""
    roots = [package / name for name in CONTENTS] if selected else [package]
    files = [p for root in roots for p in ([root] if root.is_file() else root.rglob('*'))]
    return {str(p.relative_to(package)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(files) if p.is_file() and not any(x in {'__pycache__', 'cache', '.git'}
                for x in p.relative_to(package).parts) and p.name != 'installed.json'}


def source_revision(package):
    """Return the commit of a clean kit checkout, else a hash of its contents."""
    try:
        # Only the kit's own repository counts, not a project repository around a snapshot.
        if (Path(git(package, 'rev-parse', '--show-toplevel')).resolve() == package
                and not git(package, 'status', '--porcelain', '--untracked-files=all', '--', *CONTENTS)):
            return git(package, 'rev-parse', 'HEAD')
    except (OSError, subprocess.SubprocessError):
        pass
    contents = json.dumps(digest(package, selected=True), sort_keys=True).encode()
    return 'snapshot:' + hashlib.sha256(contents).hexdigest()


def slugify(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-') or 'project'


def runtime(source):
    return Path(source).resolve()


def attach(root):
    path = root / 'AGENTS.md'
    text = path.read_text() if path.exists() else '# Research project\n'
    # Adopt without replacing any existing local rules, even an earlier managed block.
    if BEGIN not in text:
        # Keep this block stable: it is written once, so it routes only to the owned
        # conventions file, which names the current skills.
        block = '\n\n' + BEGIN + '''
## Shared research workflow

At the start of each session, read `.workflow/conventions.md`; it routes to the
skill for the current task. Local instructions and scientific choices override it.
''' + END + '\n'
        path.write_text(text.rstrip() + block)


def ensure_owned(root):
    package = root / '.workflow'
    if package.is_symlink() or read_json(root / 'workflow.json').get('mode') == 'editable':
        raise ValueError('Editable installation: manage the development checkout separately.')
    if package.exists():
        metadata = read_json(package / 'installed.json')
        if not metadata or metadata.get('hashes') != digest(package):
            raise ValueError('Shared package has local changes or is not managed; preserve them before updating.')


def install(root, source_package=PACKAGE, origin=DEFAULT_SOURCE, revision='development', pin='',
            editable=False, verified=False, metadata=None):
    root = root.resolve(strict=True)
    source_package = source_package.resolve(strict=True)
    if not (source_package / 'workflow.py').is_file():
        raise ValueError('Source is not a research workflow package')
    if not verified:
        # During an update the calling version already checked the package with the
        # rules that wrote installed.json; this version's rules may differ.
        ensure_owned(root)
    target = root / '.workflow'
    attached = (root / 'workflow.json').exists()
    config = read_json(root / 'workflow.json')
    if revision == 'development':
        revision = source_revision(source_package)
    config.update(source=origin, revision=revision, pin=pin, mode='editable' if editable else 'snapshot')
    config.setdefault('updates', 'ask')
    config.setdefault('slug', slugify(root.name))
    config.setdefault('title', root.name)
    config.setdefault('author', '')
    config.update(metadata or {})
    # Stage before replacing the owned package; retain a recoverable backup on failure.
    with tempfile.TemporaryDirectory(prefix='.workflow-install-', dir=root) as temporary:
        stage = Path(temporary) / 'package'
        stage.mkdir()
        if editable:
            # Link only the kit contents, so a pilot sees what a snapshot contains.
            for name in CONTENTS:
                if (source_package / name).exists():
                    (stage / name).symlink_to(source_package / name)
        else:
            for name in CONTENTS:
                original = source_package / name
                if original.is_dir():
                    shutil.copytree(original, stage / name, ignore=shutil.ignore_patterns('__pycache__'))
                else:
                    shutil.copy2(original, stage / name)
            write_json(stage / 'installed.json', {'revision': revision, 'hashes': digest(stage)})
        backup = Path(temporary) / 'previous'
        if target.exists():
            target.rename(backup)
        try:
            stage.rename(target)
            write_json(root / 'workflow.json', config)
        except Exception:
            if target.exists():
                shutil.rmtree(target)
            if backup.exists():
                backup.rename(target)
            raise
    if not attached:
        attach(root)


def release(tags):
    versions = [(tuple(map(int, match.groups())), tag) for tag in tags if (match := VERSION.fullmatch(tag))]
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
        script = checkout / RELATIVE
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
    try:
        origin = config.get('source', DEFAULT_SOURCE)
        output = subprocess.check_output(['git', 'ls-remote', '--tags', '--', origin],
                                         text=True, stderr=subprocess.PIPE, timeout=20)
        commits = {}
        for line in output.splitlines():
            sha, ref = line.split()
            tag = ref.removeprefix('refs/tags/')
            if tag.endswith('^{}'):
                commits[tag.removesuffix('^{}')] = sha  # commit behind an annotated tag
            else:
                commits.setdefault(tag, sha)
        if config.get('pin'):
            message = f'Workflow pinned to {config["pin"]}; use update --unpin to follow releases.'
        else:
            latest = release(commits)
            installed = [tag for tag, sha in commits.items() if sha == config.get('revision')]
            if latest in installed:
                message = f'{latest}: up to date'
            elif any(VERSION.fullmatch(tag) for tag in installed):
                message = f'{latest}: update available; run python .workflow/workflow.py update'
            else:
                # A development checkout may be newer than every release: never suggest a downgrade.
                message = f'Unreleased workflow revision installed; latest release is {latest}.'
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        message = f'Update check unavailable ({type(error).__name__}); research can continue.'
    cache.parent.mkdir(parents=True, exist_ok=True)
    write_json(cache, {'time': time.time(), 'message': message})
    print(message)


def add(root, component):
    config = read_json(root / 'workflow.json')
    destinations = {'manuscript': 'manuscript', 'repository': 'repository',
                    'outreach': 'manuscript/outreach', 'response': 'manuscript/submission'}
    destination = root / destinations[component]
    if component in {'outreach', 'response'} and not (root / 'manuscript/.git').exists():
        raise ValueError('Set up the authoritative manuscript repository first.')
    if component in {'manuscript', 'repository'} and destination.exists():
        raise ValueError(f'{destination} already exists; preserve it rather than creating a new repository.')
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
                    if not value:
                        raise ValueError(f'{path.name} needs {match[1]}; record the project title and '
                                         'authors in workflow.json first.')
                    return json.dumps(value, ensure_ascii=False)[1:-1] if path.suffix == '.toml' else value
                path.write_text(re.sub(r'\{\{\s*([A-Z][A-Z0-9_]*)\s*\}\}', replace, path.read_text()))
        if component in {'manuscript', 'repository'}:
            git(stage, 'init', '-b', 'main')
        # Optional files may join an existing folder, but never replace a file.
        clashes = [str(path.relative_to(stage)) for path in stage.rglob('*')
                   if path.is_file() and (destination / path.relative_to(stage)).exists()]
        if clashes:
            raise ValueError(f'{destination} already has {", ".join(clashes)}; compare the template manually.')
        shutil.copytree(stage, destination, dirs_exist_ok=True)
    if component in {'manuscript', 'repository'}:
        ignore = root / '.gitignore'
        text = ignore.read_text() if ignore.exists() else ''
        if f'/{component}/' not in text.splitlines():
            ignore.write_text(text.rstrip() + f'\n/{component}/\n')
    print(f'Added {component} in {destination}; no files staged or committed.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    commands = parser.add_subparsers(dest='command', required=True)
    adopt = commands.add_parser('adopt', help='Attach to an existing project without restructuring it')
    adopt.add_argument('--editable', type=Path, help='Link a pilot project to a development checkout or runtime folder')
    adopt.add_argument('--source', default=DEFAULT_SOURCE)
    adopt.add_argument('--title', help='project title, used by optional components')
    adopt.add_argument('--author', help='project authors, used by optional components')
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
            metadata = {key: value for key, value in [('title', args.title), ('author', args.author)] if value}
            install(root, runtime(args.editable) if args.editable else PACKAGE,
                    origin=args.source, editable=bool(args.editable), metadata=metadata)
        elif args.command == '_install':
            install(args.target, origin=args.origin, revision=args.revision, pin=args.pin, verified=True)
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
