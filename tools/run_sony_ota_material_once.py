# SPDX-License-Identifier: GPL-2.0-or-later
"""Frozen SK1 live entry. No communication without separate explicit approval."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
HERE = REPO / 'build/m10/sk1-preparation-20261015-01'
sys.path[:0] = [str(REPO / 'tools'), str(HERE)]
import acquire_sony_ota_material as sk
import characterization_plan as cp


def save_new(path, value):
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2); f.write('\n')


def main(argv):
    if not argv:
        print(json.dumps({'stage':'SK1','execution':False,'requires':'separate human approval and fresh owner readiness'}))
        return 0
    if argv != ['--run-approved']: raise cp.Refusal('fixed invocation required')
    bundle = cp.load_json(HERE / 'execution-bundle.json')
    for name, digest in bundle['files'].items():
        path = REPO / name
        if any(p.is_symlink() or getattr(p,'is_junction',lambda:False)() for p in (path,*path.parents)) or cp.sha(path.read_bytes()) != digest:
            raise cp.Refusal('frozen execution input changed')
    if cp.load_json(HERE / 'reviewed-plan.json') != sk.plan(): raise cp.Refusal('reviewed plan changed')
    profile = cp.load_json(REPO / 'build/m10/authorizations/expected-nwa306-20261014-01.json')
    approval = cp.load_json(HERE / 'approval.json')
    proposal = cp.load_json(HERE / 'approval-proposal.json')
    if approval != dict(proposal, approved=True): raise cp.Refusal('approval differs from frozen proposal')
    if approval['bundle_sha256'] != cp.sha((HERE/'execution-bundle.json').read_bytes()):
        raise cp.Refusal('approved execution bundle changed')
    owner = cp.load_json(HERE / 'owner-readiness.json')
    cp.exact_keys(owner, ('confirmed','utc','authorization_text','same_unit','normal_stock_android',
                          'debugging_already_authorized','idle_no_update_or_transfer'))
    for key in ('confirmed','same_unit','normal_stock_android','debugging_already_authorized','idle_no_update_or_transfer'):
        if owner[key] is not True: raise cp.Refusal('owner readiness missing')
    if not isinstance(owner['authorization_text'],str) or not owner['authorization_text'].strip():
        raise cp.Refusal('direct human authorization record missing')
    stamp = datetime.fromisoformat(owner['utc'])
    if stamp.tzinfo is None or not 0 <= (datetime.now(timezone.utc)-stamp).total_seconds() <= 900:
        raise cp.Refusal('fresh owner readiness required')
    out = Path(approval['output'])
    if out.exists() or (HERE/'live-attempt.json').exists(): raise cp.Refusal('attempt already reserved; no retry')
    # Host preflight failure also consumes the single attempt.
    save_new(HERE/'live-attempt.json', {'stage':'SK1','utc':datetime.now(timezone.utc).isoformat(),
             'approval_sha256':cp.sha(cp.canonical(approval)), 'owner_sha256':cp.sha(cp.canonical(owner)),
             'bundle_sha256':cp.sha((HERE/'execution-bundle.json').read_bytes()), 'automatic_retry':False})
    from host_guard import check
    check('before')  # Windows host only; never starts/contacts an ADB server.
    result = sk.run(approval, out, profile)
    try:
        check('after')  # No device requests after the adapter returns.
    except (cp.Refusal, OSError, ValueError):
        result.update(complete=False, stop='host_postflight_failed', material_promoted=False)
    else:
        result['host_guard_pending'] = False
        result['host_prerequisites_passed'] = True
        if result['complete']:
            result['artifact'] = result.pop('candidate_artifact')
            result['material_promoted'] = True
    # Keep every raw capture even when final host continuity fails. Manifest is
    # finalized in place; its previous bytes are retained in an exclusive file.
    manifest = out/'manifest.json'
    with (out/'adapter-manifest.json').open('xb') as f: f.write(manifest.read_bytes())
    manifest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    summary = {k:result[k] for k in ('stage','complete','stop','wire_bytes','material_promoted')}
    summary['observations_attempted'] = len(result['observations'])
    summary['physical_evidence_requires_independent_review'] = True
    save_new(HERE/'live-result.json', summary)
    print(json.dumps(summary))
    return 0 if result['complete'] else 1


if __name__ == '__main__':
    try: raise SystemExit(main(sys.argv[1:]))
    except (cp.Refusal, OSError, ValueError) as exc:
        print('SK1 wrapper refused: '+(str(exc) if isinstance(exc,cp.Refusal) else type(exc).__name__))
        raise SystemExit(2)
