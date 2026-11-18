"""Offline lifecycle tests using local synthetic releases and real project files."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest

SKILL = Path(__file__).resolve().parents[1]
PACKAGE = SKILL
SCRIPT = PACKAGE / 'tools/workflow.py'
RELATIVE = '.'


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
        shutil.copytree(PACKAGE, repo / RELATIVE, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        self.git(repo, 'init', '-b', 'main')
        revisions = []
        for version in ['3.0.0', '3.1.0']:
            (repo / RELATIVE / 'release.txt').write_text(version)
            # The second release adds new installer behavior, proving re-execution.
            if version == '3.1.0':
                script = repo / 'tools/workflow.py'
                script.write_text(script.read_text().replace("    config.setdefault('updates', 'ask')",
                    "    config['new_installer_ran'] = True\n    config.setdefault('updates', 'ask')"))
            self.git(repo, 'add', '.')
            self.git(repo, 'commit', '-m', version)
            self.git(repo, 'tag', 'v' + version)
            revisions.append(self.git(repo, 'rev-parse', 'HEAD'))
        return repo, revisions

    def test_system_install_and_project_adoption(self):
        entry = SKILL / 'workflow.py'
        skills = self.base / 'system-skills'
        command = [sys.executable, str(entry), 'install', '--skills-dir', str(skills)]
        for _ in range(2):
            subprocess.run(command, check=True, capture_output=True)
        installed = skills / 'research-setup'
        self.assertEqual([path.name for path in skills.iterdir()], ['research-setup'])
        self.assertEqual(installed.resolve(), (SKILL / 'skills/research-setup').resolve())
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
        self.assertFalse((self.project / '.agents').exists())

    def test_minimal_initialization_and_on_demand_components(self):
        subprocess.run([sys.executable, str(SKILL / 'tools/init_project.py'), str(self.project),
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
        agents = (self.project / 'AGENTS.md').read_text()
        self.assertTrue(agents.startswith('# Local model\nOnly two models.'))
        # The block routes only to the owned conventions file, so skills can be renamed.
        self.assertIn('.workflow/conventions.md', agents)
        self.assertNotIn('.workflow/skills/', agents)
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

    def test_check_cache_off_and_no_automatic_update(self):
        repo, revisions = self.releases()
        self.run_cli('adopt', '--source', str(repo))
        # A development snapshot is not a release: report it, never offer a downgrade.
        self.assertIn('Unreleased', self.run_cli('check').stdout)
        self.run_cli('update', '--to', 'v3.0.0')
        self.config(pin='')
        self.assertIn('update available', self.run_cli('check', '--force').stdout)
        self.assertTrue((self.project / '.workflow/cache/check.json').exists())
        self.config(source=str(self.base / 'missing'))
        self.assertIn('update available', self.run_cli('check').stdout)
        self.assertIn('unavailable', self.run_cli('check', '--force').stdout)
        self.config(updates='off')
        self.assertIn('disabled', self.run_cli('check').stdout)
        # The removed 'auto' policy no longer installs anything.
        self.config(source=str(repo), updates='auto')
        self.assertIn('update available', self.run_cli('check', '--force').stdout)
        self.assertEqual(self.config()['revision'], revisions[0])
        self.run_cli('update')
        self.assertEqual(self.config()['revision'], revisions[1])
        self.assertIn('v3.1.0: up to date', self.run_cli('check', '--force').stdout)

    def test_clean_release_checkout_is_up_to_date(self):
        repo, revisions = self.releases()
        self.run_cli('adopt', '--source', str(repo), script=repo / 'tools/workflow.py')
        self.assertEqual(self.config()['revision'], revisions[1])
        self.assertIn('v3.1.0: up to date', self.run_cli('check').stdout)

    def test_adoption_metadata_for_later_components(self):
        self.project = self.base / 'My Paper'
        self.project.mkdir()
        self.run_cli('adopt')
        self.assertEqual(self.config()['slug'], 'my-paper')
        # Components never receive empty metadata.
        self.assertIn('workflow.json', self.run_cli('add', 'repository', ok=False).stderr)
        self.assertFalse((self.project / 'repository').exists())
        self.project = self.base / 'with-metadata'
        self.project.mkdir()
        self.run_cli('adopt', '--title', 'Paper', '--author', 'A. Author')
        self.run_cli('add', 'repository')
        manifest = tomllib.loads((self.project / 'repository/pyproject.toml').read_text())
        self.assertEqual(manifest['project']['name'], 'with-metadata')
        self.assertEqual(manifest['project']['authors'], [{'name': 'A. Author'}])

    def test_central_entry_uses_project_snapshot(self):
        self.run_cli('adopt', '--author', 'A. Author')
        readme = self.project / '.workflow/templates/repository/README.md'
        readme.write_text('Pinned project template\n')
        subprocess.run([sys.executable, str(SKILL / 'workflow.py'), 'add', 'repository'],
                       cwd=self.project, check=True, capture_output=True, env=self.env)
        self.assertEqual((self.project / 'repository/README.md').read_text(), 'Pinned project template\n')

    def test_update_handoff_trusts_the_calling_version(self):
        self.run_cli('adopt')
        conventions = self.project / '.workflow/conventions.md'
        conventions.write_text('Changed under older ownership rules')
        self.run_cli('update', ok=False)
        # Only update calls _install, after its own version has checked ownership.
        self.run_cli('_install', str(self.project), '--origin', 'local', '--revision', 'r')
        self.assertEqual(conventions.read_text(), (PACKAGE / 'conventions.md').read_text())

    def test_editable_mode_never_updates_checkout(self):
        self.run_cli('adopt', '--editable', str(PACKAGE), '--author', 'A. Author')
        package = self.project / '.workflow'
        # Only the kit files are linked, not the checkout's history, tests, or docs.
        self.assertFalse(package.is_symlink())
        self.assertTrue((package / 'conventions.md').is_symlink())
        for absent in ['.git', 'tests', 'README.md', 'AGENTS.md']:
            self.assertFalse((package / absent).exists())
        self.run_cli('add', 'repository')
        self.run_cli('update', ok=False)
        self.assertIn('development checkout', self.run_cli('check').stdout)

    def test_optional_files_join_existing_folders(self):
        self.run_cli('adopt', '--author', 'A. Author')
        self.run_cli('add', 'manuscript')
        submission = self.project / 'manuscript/submission'
        submission.mkdir()
        (submission / 'cover-letter.tex').write_text('Existing letter')
        self.run_cli('add', 'response')
        self.assertTrue((submission / 'response.tex').exists())
        self.assertEqual((submission / 'cover-letter.tex').read_text(), 'Existing letter')
        (submission / 'response.tex').write_text('My response')
        self.assertIn('response.tex', self.run_cli('add', 'response', ok=False).stderr)
        self.assertEqual((submission / 'response.tex').read_text(), 'My response')


if __name__ == '__main__':
    unittest.main()
