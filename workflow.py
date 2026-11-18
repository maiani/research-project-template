#!/usr/bin/env python3
"""Install the setup skill, start a project, or adopt the research workflow."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
SKILL = ROOT / 'skills/research-setup'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    install = commands.add_parser('install', help='Register the setup skill once for your agent')
    install.add_argument('--skills-dir', type=Path, default=Path.home() / '.agents/skills',
                         help='agent skill directory (default: ~/.agents/skills)')
    commands.add_parser('init', help='Initialize an empty project; use init --help for options',
                        add_help=False)
    for name in ['adopt', 'status', 'check', 'update', 'add']:
        commands.add_parser(name, help=f'Run {name} in the current project', add_help=False)
    args, rest = parser.parse_known_args()
    if args.command == 'install':
        if rest:
            parser.error('unrecognized arguments: ' + ' '.join(rest))
        folder = args.skills_dir.expanduser().resolve()
        target = folder / SKILL.name
        if target.is_symlink() and target.resolve() == SKILL.resolve():
            print(f'Already installed: {target}')
            return
        if target.exists() or target.is_symlink():
            parser.error(f'Preserving existing skill at {target}; review it before installing.')
        folder.mkdir(parents=True, exist_ok=True)
        try:
            target.symlink_to(SKILL, target_is_directory=True)
        except OSError as error:
            parser.exit(1, f'Cannot link the skill: {error}\n'
                        f'Keep the complete kit at {ROOT} and ask the agent to read {SKILL / "SKILL.md"}.\n')
        print(f'Installed {target}\nAsk your agent: Use research-setup to start or adopt this project.')
        return
    if args.command == 'init':
        script = ROOT / 'tools/init_project.py'
    else:
        # Commands for an existing project run its own pinned snapshot, not this checkout.
        local = Path.cwd() / '.workflow/tools/workflow.py'
        script = local if args.command != 'adopt' and local.is_file() else ROOT / 'tools/workflow.py'
    command = [sys.executable, str(script)]
    if args.command != 'init':
        command.append(args.command)
    raise SystemExit(subprocess.call(command + rest))


if __name__ == '__main__':
    main()
