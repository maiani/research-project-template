"""Portable initializer tests. Set TEST_LATEX=1 to exercise the manuscript build."""
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch

SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / 'tools/init_project.py'
spec = importlib.util.spec_from_file_location('initializer', SCRIPT)
initializer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(initializer)


class InitializationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='research test ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.target = self.root / 'test-project'
        self.target.mkdir()
        self.env = dict(os.environ, GIT_AUTHOR_NAME='Test Author',
                        GIT_AUTHOR_EMAIL='test@example.invalid',
                        GIT_COMMITTER_NAME='Test Author', GIT_COMMITTER_EMAIL='test@example.invalid')

    def run_init(self, *extra, success=True, commit=False, env=None):
        command = [sys.executable, str(SCRIPT), str(self.target),
                   '--manuscript', '--repository', '--title', 'A test project', '--author', 'Test Author', '--date', '2030-01-02']
        if commit:
            command.append('--commit')
        result = subprocess.run(command + list(extra), env=env or self.env,
                                text=True, capture_output=True)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result

    def git(self, root, *args):
        return subprocess.check_output(['git', '-C', str(root), *args], env=self.env, text=True).strip()

    def test_preflight_and_no_build_tools(self):
        subprocess.run([sys.executable, str(SCRIPT), '--check'], check=True)
        binary = self.root / 'bin'
        binary.mkdir()
        (binary / 'git').symlink_to(shutil.which('git'))
        self.run_init(env=dict(self.env, PATH=str(binary)))
        self.assertTrue((self.target / 'manuscript/.latexmkrc').exists())

    def test_local_project_and_boundaries(self):
        self.run_init(commit=True)
        for name in ['', 'repository', 'manuscript']:
            repo = self.target / name
            self.assertEqual(Path(self.git(repo, 'rev-parse', '--show-toplevel')), repo)
            self.git(repo, 'rev-parse', '--verify', 'HEAD')
            self.assertFalse(self.git(repo, 'remote'))
        self.assertFalse(self.git(self.target, 'ls-files', 'repository', 'manuscript'))
        self.assertFalse((self.target / 'manuscript/outreach').exists())
        self.assertTrue((self.target / 'bibliography/test-project.bib').exists())
        self.assertTrue((self.target / 'journal/2030-01-02.md').exists())
        for name in ['tests', 'scripts', 'bootstrap', 'bootstrap.sh', 'skills', 'CLAUDE.md']:
            self.assertFalse((self.target / name).exists())
        self.assertFalse((self.target / 'journal/YYYY-MM-DD.md').exists())
        manifest = tomllib.loads((self.target / 'repository/pyproject.toml').read_text())
        self.assertEqual(manifest['project']['dependencies'], [])
        self.assertFalse(manifest['tool']['uv']['package'])
        self.assertFalse((self.target / 'repository/uv.lock').exists())
        self.assertFalse((self.target / 'repository/.venv').exists())
        self.assertEqual(self.git(self.target / 'repository', 'check-ignore', '.venv/test'), '.venv/test')
        self.assertEqual(len(self.git(self.target / 'manuscript', 'check-ignore', 'aux/a.aux', 'out/a.pdf').splitlines()), 2)

    def test_rejections_leave_target_untouched(self):
        for flags in [('--rename-to', '../escape'), ('--rename-to', 'Not_Kebab'), ('--date', '../bad'),
                      ('--overleaf-url', 'https://evil.example/overleaf.com/project/12345678'),
                      ('--unknown',)]:
            self.run_init(*flags, success=False)
            self.assertFalse(list(self.target.iterdir()))
        (self.target / '.git').mkdir()
        marker = self.target / '.git/keep'
        marker.write_text('preserve me')
        self.run_init(success=False)
        self.assertEqual(marker.read_text(), 'preserve me')

    def test_rename_and_parent_repository(self):
        self.git(self.root, 'init', '-b', 'main')
        self.git(self.root, 'remote', 'add', 'origin', 'https://example.invalid/parent')
        (self.target / '.git').mkdir()
        (self.target / '.agents').mkdir()
        (self.target / '.claude').mkdir()
        self.run_init('--rename-to', 'renamed-project')
        self.assertFalse(self.target.exists())
        renamed = self.root / 'renamed-project'
        self.assertTrue((renamed / '.git/HEAD').exists())
        self.assertTrue((renamed / '.agents').is_dir())
        self.assertTrue((renamed / '.claude').is_dir())
        self.assertFalse(self.git(renamed, 'ls-files'))  # nothing is staged by default
        self.assertEqual(self.git(self.root, 'remote', 'get-url', 'origin'), 'https://example.invalid/parent')
        self.assertFalse(self.git(self.root, 'ls-files'))

    def test_author_escaping(self):
        author = 'A "quoted" author \\ collaborator'
        self.run_init('--author', author)
        manifest = tomllib.loads((self.target / 'repository/pyproject.toml').read_text())
        self.assertEqual(manifest['project']['authors'], [{'name': author}])
        self.assertIn(author, (self.target / 'project.md').read_text())

    def test_overleaf_preserves_remote_content(self):
        remote = self.root / 'remote'
        remote.mkdir()
        (remote / 'main.tex').write_text('Authoritative source')
        (remote / 'outreach').mkdir()
        (remote / 'outreach/README.md').write_text('Existing outreach guide')
        (remote / '.latexmkrc').write_text('# Existing configuration\n')
        self.git(remote, 'init', '-b', 'main')
        self.git(remote, 'add', '.')
        self.git(remote, 'commit', '-m', 'Original')
        args = type('Args', (), dict(target=str(self.target), check=False, title='Test',
                    author='Test Author', rename_to=None, date='2030-01-02', overleaf_url='12345678',
                    desc=None, status='Initial setup.', commit=False, manuscript=False, repository=False))()
        with patch.object(initializer, 'overleaf_remote', return_value=str(remote)):
            initializer.initialize(args)
        manuscript = self.target / 'manuscript'
        self.assertEqual((manuscript / 'main.tex').read_text(), 'Authoritative source')
        self.assertEqual((manuscript / '.latexmkrc').read_text(), '# Existing configuration\n')
        self.assertEqual(self.git(manuscript, 'remote'), 'overleaf')
        self.assertEqual(self.git(manuscript, 'rev-parse', 'HEAD'), self.git(remote, 'rev-parse', 'HEAD'))
        self.assertTrue((manuscript / 'justfile').exists())
        self.assertEqual((manuscript / 'outreach/README.md').read_text(), 'Existing outreach guide')
        self.assertFalse((manuscript / 'outreach/visuals').exists())
        self.assertFalse((manuscript / 'submission/response.tex').exists())

    def test_complete_kit_copy(self):
        standalone = self.root / 'standalone-kit'
        shutil.copytree(SKILL, standalone, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        subprocess.run([sys.executable, str(standalone / 'tools/init_project.py'),
                        str(self.target), '--title', 'Portable', '--author', 'Test'],
                       check=True, env=self.env, stdout=subprocess.PIPE)
        self.assertTrue((self.target / '.workflow/skills/research-work/figures.md').exists())
        self.assertFalse((self.target / 'scripts').exists())

    def test_clone_failure_preserves_empty_target(self):
        args = type('Args', (), dict(target=str(self.target), check=False, title='Test',
                    author='Test', rename_to='renamed', date='2030-01-02', overleaf_url='12345678',
                    desc=None, status='Initial setup.', commit=False, manuscript=False, repository=False))()
        with patch.object(initializer, 'overleaf_remote', return_value=str(self.root / 'missing')):
            with self.assertRaises(subprocess.CalledProcessError):
                initializer.initialize(args)
        self.assertTrue(self.target.exists())
        self.assertFalse(list(self.target.iterdir()))
        self.assertFalse((self.root / 'renamed').exists())

    @unittest.skipUnless(os.environ.get('TEST_LATEX') == '1', 'set TEST_LATEX=1 for build integration')
    def test_latex_build_and_cleanup(self):
        self.run_init()
        manuscript = self.target / 'manuscript'
        (manuscript / 'test-project.tex').write_text(r'''\documentclass{article}
\begin{document}
See Section~\ref{sec:test} and Ref.~\cite{test}.
\section{Test}\label{sec:test}
\bibliographystyle{plain}\bibliography{references}
\end{document}
''')
        (manuscript / 'references.bib').write_text('@book{test,author={Test},title={Test},year={2026},publisher={Test}}')
        for recipe in ['build', 'clean', 'build', 'clean-all']:
            subprocess.run(['just', recipe], cwd=manuscript, check=True,
                           env=dict(self.env, XDG_RUNTIME_DIR='/tmp'), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.assertEqual((manuscript / 'out/test-project.pdf').exists(), recipe != 'clean-all')
            if recipe == 'build':
                self.assertTrue((manuscript / 'aux/test-project.bbl').exists())
                log = (manuscript / 'aux/test-project.log').read_text()
                self.assertNotIn('undefined references', log)
                self.assertNotIn('Citation `test\' on page 1 undefined', log)
        self.assertTrue((manuscript / 'test-project.tex').exists())
        self.assertTrue((manuscript / 'references.bib').exists())


if __name__ == '__main__':
    unittest.main()
