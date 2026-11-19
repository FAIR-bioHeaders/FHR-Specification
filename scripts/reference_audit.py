#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Audit CURRENT owning declarations with one immutable shared checker; never repin."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = 'FAIR-bioHeaders/FAIR-bioHeaders-Specification'
CONSUMER = 'FAIR-bioHeaders/FHR-Specification'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(root, name):
    data = json.loads((root / name).read_text())
    if not isinstance(data, dict):
        raise ValueError(name + ': expected object')
    return data


def measured_file(local, upstream, sha, **extra):
    if not isinstance(sha, str) or not re.fullmatch('[0-9a-f]{64}', sha):
        raise ValueError(str(local or upstream) + ': unusable recorded digest')
    return dict(local=local, path=upstream, sha256=sha, **extra)


def reference(identity, cls, revision, files, commit=None, **extra):
    if not isinstance(revision, str) or not revision:
        raise ValueError(identity + ': unusable recorded revision')
    if commit is not None and (not isinstance(commit, str) or not re.fullmatch('[0-9a-f]{40}', commit)):
        raise ValueError(identity + ': unusable recorded commit')
    row = dict(id=identity, consumer=CONSUMER, repository=AUTHORITY, **{'class': cls},
               revision=revision, revisionKind='tag' if revision.startswith('v') else 'commit', files=files)
    if commit:
        row['commit'] = commit
    row.update(extra)
    return row


def literal_assignments(root, name, wanted):
    found = {}
    for node in ast.parse((root / name).read_text()).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in wanted:
                    found[target.id] = ast.literal_eval(node.value)
    if set(found) != set(wanted):
        raise ValueError(name + ': missing declared constants')
    return found


def declarations(root):
    name = 'scripts/check_development_tree.py'
    declared = literal_assignments(root, name, {'PUBLISHED', 'SHARED_TAG', 'SHARED_COMMIT'})
    files = [measured_file(p, p, sha) for p, sha in declared['PUBLISHED'].items()]
    groups = []
    for directory in ('examples', 'jsonld'):
        selected = [f for f in files if f['local'].startswith(directory + '/')]
        groups.append(reference(directory, 'copied-tree', declared['SHARED_TAG'], selected,
                                declared['SHARED_COMMIT'], materialStatus='released',
                                sourcePatterns=[directory + '/*'], localTree=directory))
    other = [f for f in files if not f['local'].startswith(('examples/', 'jsonld/'))]
    groups.append(reference('published-contracts', 'released-contract', declared['SHARED_TAG'],
                            other, declared['SHARED_COMMIT']))
    return groups, [name], [
        'All PUBLISHED entries are read from current literal AST declarations, never executed or inferred from filename search.',
        'The two complete published directory sets are compared with the tag and local files. Root schema classification also remains guarded by check_development_tree.py.',
        'Inherited same-repository fixtures and package/action/tool-code dependencies are not cross-repository contract pins.']



def inventory(root=ROOT):
    rows, records, notes = declarations(root)
    if not rows:
        raise ValueError('No references declared')
    return dict(inventoryVersion=1, advisory=True, references=rows,
                generatedFrom=[dict(path=name, sha256=digest((root / name).read_bytes())) for name in records],
                coverageNotes=notes,
                coverageGaps=['Other consumer repositories require their own rollout; this port alone does not close shared #241.'])


def verified_checker(root, source):
    pin = load(root, 'references/checker.json')
    actual = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != pin['commit']:
        raise ValueError('Checker checkout HEAD differs from the reviewed source pin')
    script = (source / pin['path']).resolve()
    if not script.is_relative_to(source.resolve()):
        raise ValueError('Checker path escapes the reviewed source checkout')
    if digest(script.read_bytes()) != pin['sha256']:
        raise ValueError('Checker source digest differs; refusing execution')
    return script


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checker-root', type=Path)
    parser.add_argument('--inventory-only', action='store_true')
    parser.add_argument('--inventory-output', type=Path)
    parser.add_argument('--checkout', action='append', default=[], metavar='OWNER/REPO=PATH')
    parser.add_argument('--strict', action='store_true', help='exit nonzero on findings (advisory by default)')
    args = parser.parse_args(argv)
    try:
        table = inventory()
        if args.inventory_output:
            args.inventory_output.write_text(json.dumps(table, indent=2) + '\n')
        if args.inventory_only:
            print(json.dumps(table, indent=2))
            return 0
        if not args.checker_root:
            parser.error('--checker-root is required for execution')
        script = verified_checker(ROOT, args.checker_root)
        with tempfile.TemporaryDirectory() as directory:
            table_file = Path(directory) / 'inventory.json'
            table_file.write_text(json.dumps(table))
            command = [sys.executable, str(script), '--inventory', str(table_file),
                       '--consumer', CONSUMER, '--consumer-root', str(ROOT)]
            for mapping in args.checkout:
                command += ['--checkout', mapping]
            if args.strict:
                command.append('--exit-on-findings')
            return subprocess.run(command, check=False).returncode
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print(json.dumps(dict(advisory=True, status='UNUSABLE', error=str(error), wrotePins=[])))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
