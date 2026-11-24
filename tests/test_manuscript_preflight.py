"""Behavioral checks for manuscript preflight, including use outside the kit."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

KIT = Path(__file__).resolve().parents[1]
SKILL = KIT / 'skills/manuscript-preflight'
CHECKER = SKILL / 'scripts/check_manuscript.py'
FIXTURE = KIT / 'tests/fixtures/manuscript-preflight'
MAIN = r'\documentclass{article}\begin{document}Text.\end{document}'


class ManuscriptPreflightTests(unittest.TestCase):
    def run_checker(self, *args, cwd=None, checker=CHECKER):
        result = subprocess.run([sys.executable, str(checker), *map(str, args), '--json'],
                                cwd=cwd, text=True, capture_output=True)
        self.assertIn(result.returncode, (0, 1), result.stderr)
        return result.returncode, json.loads(result.stdout)

    def log_findings(self, report):
        return [f for f in report['findings'] if f['category'] == 'log']

    def test_imported_fixture_reports_errors_and_skips_backup(self):
        code, report = self.run_checker(FIXTURE)
        self.assertEqual(code, 1)
        self.assertEqual(report['roots'], [str(FIXTURE / 'main.tex')])
        self.assertIn(str(FIXTURE / 'main_backup.tex'), report['skipped_roots'])
        errors = '\n'.join(f['message'] for f in report['findings']
                           if f['severity'] == 'ERROR')
        self.assertIn('nonexistent2024', errors)
        self.assertIn('sec:model', errors)

    def test_explicit_build_log_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'main.tex').write_text(MAIN)
            (root / 'aux').mkdir()
            (root / 'aux/main.log').write_text('Overfull \\hbox (5.0pt too wide)\n')
            # A stale log beside the source must not override the selected directory.
            (root / 'main.log').write_text('')
            code, report = self.run_checker('.', '--log-dir', 'aux', cwd=root)
            self.assertEqual(code, 0)
            logs = self.log_findings(report)
            self.assertTrue(any('overfull' in f['message'] for f in logs), logs)
            self.assertTrue(any(f['file'] == 'aux/main.log' for f in logs), logs)
            _, missing = self.run_checker('.', '--log-dir', 'missing', cwd=root)
            self.assertTrue(any('no build log' in f['message']
                                for f in missing['findings']))
            _, adjacent = self.run_checker('.', cwd=root)
            self.assertFalse(any('no build log' in f['message']
                                 for f in adjacent['findings']))

    def test_build_log_directory_from_latexmkrc(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            manuscript = project / 'manuscript'
            (manuscript / 'aux').mkdir(parents=True)
            (manuscript / 'main.tex').write_text(MAIN)
            (manuscript / 'aux/main.log').write_text('Overfull \\hbox (5.0pt too wide)\n')
            (manuscript / 'main.log').write_text('')  # stale, beside the source
            (manuscript / '.latexmkrc').write_text(
                "# $aux_dir = 'ignored';\n$aux_dir = 'aux';\n$out_dir = 'out';\n")
            # The kit's layout, audited from the project root, by directory or by file.
            for target in ['manuscript', 'manuscript/main.tex']:
                _, report = self.run_checker(target, cwd=project)
                logs = self.log_findings(report)
                self.assertTrue(any(f['file'] == 'manuscript/aux/main.log' for f in logs), logs)
            # Only an output directory: latexmk writes the log there.
            (manuscript / '.latexmkrc').write_text("$out_dir = 'aux';\n")
            _, report = self.run_checker('.', cwd=manuscript)
            self.assertTrue(any(f['file'] == 'aux/main.log' for f in self.log_findings(report)))

    def test_skill_folder_works_without_the_kit(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / 'manuscript-preflight'
            shutil.copytree(SKILL, copy, ignore=shutil.ignore_patterns('__pycache__'))
            text = (copy / 'SKILL.md').read_text()
            for link in re.findall(r'\]\(([^)#]+)\)', text):
                if '://' not in link:
                    self.assertTrue((copy / link).exists(), f'{link} is outside the skill folder')
            code, report = self.run_checker(FIXTURE, checker=copy / 'scripts/check_manuscript.py')
            self.assertEqual(code, 1)
            self.assertEqual(report['roots'], [str(FIXTURE / 'main.tex')])
