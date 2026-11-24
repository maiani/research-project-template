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

PACKAGE = Path(__file__).resolve().parents[1]
RELATIVE = Path('tools/workflow.py')
CONTENTS = ('workflow.py', 'conventions.md', 'skills', 'tools', 'templates', '.gitignore', 'LICENSE')
# Placeholders that templates may use; `init` fills all of them, `add` all but WORKFLOW_BLOCK.
PLACEHOLDERS = ('PROJECT_SLUG', 'PROJECT_TITLE', 'PAPER_TITLE', 'AUTHOR', 'AUTHORS',
                'DESCRIPTION', 'DATE_ISO', 'WORKFLOW_BLOCK')
TOKEN = re.compile(r'\{\{\s*([A-Z][A-Z0-9_]*)\s*\}\}')
DEFAULT_SOURCE = 'https://github.com/maiani/research-project-template.git'
VERSION = re.compile(r'v?(\d+)\.(\d+)\.(\d+)')
BEGIN = '<!-- BEGIN research-workflow -->'
END = '<!-- END research-workflow -->'
# Written once and never refreshed, so it names no skill or version number: it routes
# to the owned conventions file and to workflow.json, which updates keep current.
BLOCK = BEGIN + '''
## Shared research workflow

This project uses the shared research workflow pinned in `.workflow/`;
`workflow.json` records its version and update settings. Change either only with
`python .workflow/workflow.py`. At the start of each session, read
`.workflow/conventions.md`: it sets the session routine and repository rules and
names the skill for the current task. Local instructions and scientific choices
override it.
''' + END


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
            for p in sorted(files) if p.is_file() and not any(x in {'__pycache__', '.git'}
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


def version_label(package, revision):
    """Name a kit revision for people: its release tag, or the nearest tag plus commits."""
    try:
        if Path(git(package, 'rev-parse', '--show-toplevel')).resolve() == package.resolve():
            label = git(package, 'describe', '--tags', '--always', '--match', 'v[0-9]*')
            return label + ('+modified' if revision.startswith('snapshot:') else '')
    except (OSError, subprocess.SubprocessError):
        pass
    return 'unreleased'


def render(template, values):
    """Return each text file of a template folder, relative to it, with placeholders filled."""
    rendered = {}
    for path in sorted(template.rglob('*')):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(template)
        def replace(match):
            if match[1] not in values:
                raise ValueError(f'unknown placeholder {match[1]} in {template.name}/{relative}')
            if not values[match[1]]:
                raise ValueError(f'{relative} needs {match[1]}; record the project title and '
                                 'authors in workflow.json first.')
            # TOML strings need escaped quotes and backslashes.
            return json.dumps(values[match[1]], ensure_ascii=False)[1:-1] if path.suffix == '.toml' \
                else values[match[1]]
        rendered[relative] = TOKEN.sub(replace, path.read_text(encoding='utf-8'))
    return rendered


def slugify(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-') or 'project'


def runtime(source):
    return Path(source).resolve()


def attach(root):
    path = root / 'AGENTS.md'
    text = path.read_text() if path.exists() else '# Research project\n'
    # Adopt without replacing any existing local rules, even an earlier managed block.
    # New projects already place the block in their scaffold.
    if BEGIN not in text:
        path.write_text(text.rstrip() + '\n\n' + BLOCK + '\n')


def ownership_problem(root):
    """Why an update would refuse to replace `.workflow/`, or None."""
    package = root / '.workflow'
    if package.is_symlink() or read_json(root / 'workflow.json').get('mode') == 'editable':
        return 'Editable installation: manage the development checkout separately.'
    if package.exists():
        metadata = read_json(package / 'installed.json')
        if not metadata or metadata.get('hashes') != digest(package):
            return 'Shared package has local changes or is not managed; preserve them before updating.'
    return None


def ensure_owned(root):
    if problem := ownership_problem(root):
        raise ValueError(problem)


def status(root):
    """Describe the installed workflow without using the network."""
    config = read_json(root / 'workflow.json')
    pin = f', pinned to {config["pin"]}' if config.get('pin') else ''
    print(f'Workflow {config.get("version", "unknown")} ({config.get("mode", "snapshot")}{pin})')
    print(f'Source: {config.get("source", DEFAULT_SOURCE)}')
    print(ownership_problem(root) or '.workflow/ matches the installed revision.')


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
    # An editable install follows its checkout, so any recorded label would go stale.
    version = 'editable' if editable else version_label(source_package, revision)
    config.update(version=version, source=origin, revision=revision, pin=pin,
                  mode='editable' if editable else 'snapshot')
    config.pop('updates', None)  # retired update-check setting
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


def update(root, to=None, unpin=False, source=None, dry_run=False):
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
        if dry_run:
            target = f'{selected}{" (pinned)" if pin else ""} ({revision[:12]})'
            installed = config.get('version', 'unknown')
            if revision == config.get('revision'):
                print(f'Up to date: {target}.')
                return
            print(f'Would update from {installed} to {target}; nothing changed.')
            if not VERSION.fullmatch(installed):
                print('The installed revision is not a release; the selected one may be older.')
            return
        # Install using the selected version, never old logic against new assets.
        subprocess.run([sys.executable, str(script), '_install', str(root),
                        '--origin', origin, '--revision', revision, '--pin', pin], check=True)
        # Installers before 3.1 keep a previous label; name the selected revision here.
        config = read_json(root / 'workflow.json')
        config['version'] = version_label(checkout, revision)
        write_json(root / 'workflow.json', config)
        print(f'Updated shared workflow to {selected} ({revision[:12]}). Project files preserved.')


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
              'DATE_ISO': datetime.now(timezone.utc).date().isoformat()}
    with tempfile.TemporaryDirectory(prefix='research-component-') as temporary:
        stage = Path(temporary) / component
        shutil.copytree(PACKAGE / 'templates' / component, stage)
        for relative, text in render(PACKAGE / 'templates' / component, values).items():
            (stage / relative).write_text(text, encoding='utf-8')
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
    commands.add_parser('status', help='Show the installed version and local changes, offline')
    upgrade = commands.add_parser('update', help='Install the latest release or a selected version')
    group = upgrade.add_mutually_exclusive_group()
    group.add_argument('--to', metavar='REF', help='install and pin a release tag or commit')
    group.add_argument('--unpin', action='store_true', help='follow the latest release again')
    upgrade.add_argument('--source', metavar='URL', help='use another repository URL or local Git repository')
    upgrade.add_argument('--dry-run', action='store_true', help='report what would be installed; change nothing')
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
            status(root)
        elif args.command == 'update':
            update(root, args.to, args.unpin, args.source, args.dry_run)
        elif args.command == 'add':
            add(root, args.component)
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f'ERROR: {error}\n')


if __name__ == '__main__':
    main()
