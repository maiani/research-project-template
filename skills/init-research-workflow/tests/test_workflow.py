"""Offline lifecycle tests using local synthetic releases and real project files."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
PACKAGE = SKILL / 'assets/workflow'
SCRIPT = PACKAGE / 'workflow.py'
RELATIVE = 'skills/init-research-workflow/assets/workflow'


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.project = self.base / 'paper'
        self.project.mkdir()
        self.env = dict(os.environ, GIT_AUTHOR_NAME='Test', GIT_AUTHOR_EMAIL='test@example.invalid',
                        GIT_COMMITTER_NAME='Test', GIT_COMMITTER_EMAIL='test@example.invalid')

    def run_cli(self, *args, script=SCRIPT, ok=True):
        result = subprocess.run([sys.executable, str(script), '--root', str(self.project), *args],
                                text=True, capture_output=True, env=self.env)
        self.assertEqual(result.returncode == 0, ok, result.stdout + result.stderr)
        return result

    def git(self, path, *args):
        return subprocess.check_output(['git', '-C', str(path), *args], text=True,
                                       stderr=subprocess.PIPE, env=self.env).strip()

    def config(self, **values):
        path = self.project / 'workflow.json'
        config = json.loads(path.read_text())
        config.update(values)
        path.write_text(json.dumps(config))
        return config

    def releases(self):
        repo = self.base / 'upstream'
        shutil.copytree(PACKAGE, repo / RELATIVE)
        self.git(repo, 'init', '-b', 'main')
        revisions = []
        for version in ['3.0.0', '3.1.0']:
            (repo / RELATIVE / 'release.txt').write_text(version)
            # The second release adds new installer behavior, proving re-execution.
            if version == '3.1.0':
                script = repo / RELATIVE / 'workflow.py'
                script.write_text(script.read_text().replace("    config.setdefault('updates', 'ask')",
                    "    config['new_installer_ran'] = True\n    config.setdefault('updates', 'ask')"))
            self.git(repo, 'add', '.')
            self.git(repo, 'commit', '-m', version)
            self.git(repo, 'tag', 'v' + version)
            revisions.append(self.git(repo, 'rev-parse', 'HEAD'))
        return repo, revisions

    def test_system_install_and_project_adoption(self):
        entry = SKILL.parents[1] / 'workflow.py'
        skills = self.base / 'system-skills'
        command = [sys.executable, str(entry), 'install', '--skills-dir', str(skills)]
        for _ in range(2):
            subprocess.run(command, check=True, capture_output=True)
        installed = skills / 'init-research-workflow'
        self.assertEqual(installed.resolve(), SKILL.resolve())
        installed.unlink()
        installed.mkdir()
        (installed / 'SKILL.md').write_text('User-owned skill')
        result = subprocess.run(command, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((installed / 'SKILL.md').read_text(), 'User-owned skill')
        subprocess.run([sys.executable, str(entry), 'adopt'], cwd=self.project,
                       check=True, capture_output=True)
        self.assertTrue((self.project / 'workflow.json').exists())
        self.assertFalse((self.project / 'repository').exists())

    def test_minimal_initialization_and_on_demand_components(self):
        subprocess.run([sys.executable, str(SKILL / 'scripts/init_project.py'), str(self.project),
                        '--title', 'Paper', '--author', 'A "quoted" author'], check=True, env=self.env,
                       stdout=subprocess.PIPE)
        for absent in ['manuscript', 'repository', 'guides', 'workspace/scratch', 'slides']:
            self.assertFalse((self.project / absent).exists())
        self.assertFalse(self.git(self.project, 'ls-files'))
        for component in ['manuscript', 'repository', 'response', 'outreach']:
            self.run_cli('add', component)
        self.assertTrue((self.project / 'manuscript/submission/response.tex').exists())
        self.assertTrue((self.project / 'manuscript/outreach/README.md').exists())
        self.assertNotIn('{{', (self.project / 'repository/pyproject.toml').read_text())
        for name in ['manuscript', 'repository']:
            self.assertEqual(self.git(self.project / name, 'rev-parse', '--show-toplevel'), str(self.project / name))
            self.assertFalse(self.git(self.project / name, 'ls-files'))
        self.run_cli('add', 'manuscript', ok=False)

    def test_adoption_preserves_local_files_and_foreign_skills(self):
        (self.project / 'AGENTS.md').write_text('# Local model\nOnly two models.\n')
        (self.project / 'project.md').write_text('Scientific evidence')
        foreign = self.project / '.agents/skills/research-work'
        foreign.mkdir(parents=True)
        (foreign / 'SKILL.md').write_text('My own skill')
        self.run_cli('adopt')
        self.assertTrue((self.project / 'AGENTS.md').read_text().startswith('# Local model\nOnly two models.'))
        self.assertEqual((self.project / 'project.md').read_text(), 'Scientific evidence')
        self.assertEqual((foreign / 'SKILL.md').read_text(), 'My own skill')
        self.assertFalse((self.project / 'manuscript').exists())
        self.assertFalse((self.project / '.git').exists())
        self.run_cli('adopt', ok=False)

    def test_release_pin_rollback_and_dirty_protection(self):
        repo, revisions = self.releases()
        self.run_cli('adopt', '--source', str(repo))
        self.config(custom={'preserve': True})
        (self.project / 'AGENTS.md').write_text('Local instructions stay exactly unchanged\n')
        (self.project / 'model.py').write_text('MODEL = "fixed"\n')
        self.run_cli('update', '--to', 'v3.0.0')
        self.assertEqual(self.config()['revision'], revisions[0])
        self.run_cli('update')
        self.assertEqual(self.config()['revision'], revisions[0])
        self.run_cli('update', '--unpin')
        self.assertEqual(self.config()['revision'], revisions[1])
        self.assertTrue(self.config()['new_installer_ran'])
        self.run_cli('update', '--to', 'v3.0.0')
        self.assertEqual(self.config()['custom'], {'preserve': True})
        self.assertEqual((self.project / 'model.py').read_text(), 'MODEL = "fixed"\n')
        self.assertEqual((self.project / 'AGENTS.md').read_text(), 'Local instructions stay exactly unchanged\n')
        conventions = self.project / '.workflow/conventions.md'
        conventions.write_text('Local work')
        self.run_cli('update', '--unpin', ok=False)
        self.assertEqual(conventions.read_text(), 'Local work')

    def test_check_cache_off_and_explicit_auto(self):
        repo, revisions = self.releases()
        self.run_cli('adopt', '--source', str(repo))
        self.run_cli('check')
        self.assertTrue((self.project / '.workflow/cache/check.json').exists())
        self.config(source=str(self.base / 'missing'))
        self.assertIn('update available', self.run_cli('check').stdout)
        self.assertIn('unavailable', self.run_cli('check', '--force').stdout)
        self.config(updates='off')
        self.assertIn('disabled', self.run_cli('check').stdout)
        self.config(source=str(repo), updates='auto')
        self.run_cli('check', '--force')
        self.assertEqual(self.config()['revision'], revisions[1])

    def test_editable_mode_never_updates_checkout(self):
        self.run_cli('adopt', '--editable', str(PACKAGE))
        self.assertTrue((self.project / '.workflow').is_symlink())
        self.run_cli('update', ok=False)
        self.assertIn('development checkout', self.run_cli('check').stdout)


if __name__ == '__main__':
    unittest.main()
