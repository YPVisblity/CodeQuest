"""Rebuild ID-aware references from saved teacher solutions and topic tests.
Run from mysite: python tools/rebuild_id_references.py [--topic TOPIC]
"""
from pathlib import Path
import argparse, json, sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import nbformat
from pages.id_reference import build_reference

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--topic')
    args = parser.parse_args()
    manifest_path = ROOT/'docs/id-tests/manifest.json'
    items = json.loads(manifest_path.read_text(encoding='utf-8'))
    if args.topic and not any(i['topic']==args.topic for i in items):
        parser.error('Unknown topic')
    for item in items:
        if args.topic and item['topic']!=args.topic:
            continue
        topic = item['topic']
        notebook_path = ROOT/item['teacher']
        nb = nbformat.read(notebook_path,as_version=4)
        solution = nb.cells[1].source
        matches = list((ROOT/'levels').rglob(topic+'/test.py'))
        if len(matches)!=1:
            raise ValueError(f'Ambiguous test file: {topic}')
        tests = matches[0].read_text(encoding='utf-8-sig')
        reference = build_reference(topic,solution,tests)
        target = ROOT/'references'/f'{topic}.pkl'
        temporary = target.with_suffix('.pkl.pending')
        reference.dump(str(temporary))
        temporary.replace(target)
        nb.cells[2].source = 'std_id3n = 0\n'+tests
        nb.cells[3].source = f"from pages.id_reference import build_reference\nreference = build_reference({topic!r}, {solution!r}, {tests!r})\n"
        nbformat.write(nb,notebook_path)
        item.update(solution=solution,test=tests,checkpoints=len(reference.annotations))
        print(f'{topic}: {len(reference.annotations)} checkpoints')
    manifest_path.write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':
    main()
