import re, os, sys, json

ROOT = os.path.join(os.path.dirname(__file__), '..', 'HelloSpireCode')

VFX_MARKERS = [
    'WithHitFx', 'WithAttackerFx', 'WithHitVfxNode', 'VfxCmd.', 'PlaySplashVfx',
    'CombatVfxContainer', '.Create(', 'NCombatRoom.Instance', 'PlayFullScreenInCombat',
    'PlayOnCreature', 'TriggerAnim',
    # Shared helpers already known (verified by hand) to carry their own hit vfx end-to-end.
    'Revolver.Fire(', 'Revolver.FireTimes(', 'Revolver.FireAtAll(', 'Revolver.FireAtRandom(',
    'Revolver.FireUntilClick(', 'Revolver.SelfFire(',
]

class_re = re.compile(
    r'public\s+sealed\s+class\s+(\w+)(?:\([^)]*\))?\s*:\s*(\w+)\(([^\n]*?)\)\s*\n',
)

def find_classes(text):
    # Find all "class NAME(...) : BASE(args)" or "class NAME : BASE(args)" declarations
    results = []
    for m in re.finditer(r'(?:public|internal)\s+(?:sealed\s+|abstract\s+)?class\s+(\w+)\s*(?:\([^\n\)]*\))?\s*:\s*(\w+)\s*\(([^\n]*)\)', text):
        results.append((m.start(), m.group(1), m.group(2), m.group(3)))
    return results

def main():
    rows = []
    for dirpath, _, filenames in os.walk(ROOT):
        for fn in filenames:
            if not fn.endswith('.cs'):
                continue
            path = os.path.join(dirpath, fn)
            with open(path, encoding='utf-8') as f:
                text = f.read()
            classes = find_classes(text)
            if not classes:
                continue
            # determine boundaries between classes (next class start or EOF)
            for i, (start, name, base, ctorargs) in enumerate(classes):
                end = classes[i+1][0] if i+1 < len(classes) else len(text)
                body = text[start:end]
                # Only care about card-like classes (base contains 'Card' somewhere up the chain -- heuristic: ctorargs contains CardType.)
                m_type = re.search(r'CardType\.(\w+)', ctorargs) or re.search(r'CardType\.(\w+)', body[:400])
                if not m_type:
                    continue
                cardtype = m_type.group(1)
                has_onplay = 'OnPlay(' in body
                # extract OnPlay body roughly (from OnPlay( to next "protected override" after it, or end)
                op_idx = body.find('OnPlay(')
                if op_idx == -1:
                    onplay_body = ''
                else:
                    rest = body[op_idx:]
                    # cut at next method start after depth returns to 0 -- simplistic: cut at "\n    protected override" occurring after some content
                    m2 = re.search(r'\n\s*protected override (?!async Task OnPlay)', rest[10:])
                    onplay_body = rest[:m2.start()+10] if m2 else rest
                has_vfx = any(marker in onplay_body for marker in VFX_MARKERS)
                rows.append({
                    'file': os.path.relpath(path, os.path.join(ROOT, '..')).replace('\\','/'),
                    'class': name,
                    'base': base,
                    'cardtype': cardtype,
                    'has_onplay': has_onplay,
                    'has_vfx': has_vfx,
                })
    out_path = os.path.join(os.path.dirname(__file__), 'vfx_audit.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=1)

if __name__ == '__main__':
    main()
