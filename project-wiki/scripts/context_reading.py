"""Pure reading projections: complete scope indexes, authored state and history.

No Git, native execution, writes or deployment inference. The workflow caller
supplies captured Markdown, identities and freshness observations.
"""
from __future__ import annotations
import json
import re

HISTORY = re.compile(r'^(?:history|historical (?:evidence|notes|records)|verification history|review history|核验历史|archive|archived|历史|历史记录|历史证据|归档|迁出的历史)(?:\s*[（(].*[)）])?$',re.I)
CURRENT = re.compile(r'^(current(?: state| status)?|当前(?:状态|现状)?|现状)$',re.I)
QUALIFIER = re.compile(r'未合入|未部署|未上线|待部署|源码候选|not (?:yet )?(?:merged|deployed|released)|branch.only',re.I)
VERIFY = re.compile(r'^>\s*(?:核验|Reviewed|Verification)\s*[:：]\s*(.*)',re.I)


def fence_transition(line: str, fence: str | None) -> tuple[bool, str | None]:
    marker=re.match(r'^\s{0,3}(`{3,}|~{3,})(.*)$',line)
    if not marker:return False,fence
    token=marker[1]
    if fence is None:return True,token
    if token[0]==fence[0] and len(token)>=len(fence) and not marker[2].strip():return True,None
    return True,fence


def page_projection(text: str) -> dict:
    body=[]; history=[]; notes=[]; state=[]; candidates=[]; headings=[]
    history_level=None; current_level=None; fence=None
    for number,line in enumerate(text.splitlines(keepends=True),1):
        marker,fence=fence_transition(line,fence)
        fenced=marker or fence is not None
        heading=None if fenced else re.match(r'^(#{1,6})\s+(.+?)\s*$',line)
        if heading:
            level=len(heading[1]);title=heading[2]
            if history_level is not None and level<=history_level:history_level=None
            if current_level is not None and level<=current_level:current_level=None
            if HISTORY.fullmatch(title):history_level=level
            elif CURRENT.fullmatch(title.strip()):current_level=level
            headings.append({'title':title,'line':number,'history':history_level is not None})
        if not fenced and (match:=VERIFY.match(line)):
            if history_level is not None:
                history.append(line)  # Explicit history stays readable, never a current note.
            else:
                notes.extend({'line':number,'text':part.strip()} for part in match[1].split('｜') if part.strip())
            continue
        if history_level is not None:
            history.append(line);continue
        body.append(line)
        if current_level is not None and not heading:state.append(line)
        if not fenced and QUALIFIER.search(line):
            candidates.append({'line':number,'text':line.rstrip(),'status':'needs owner review; no automatic promotion'})
    return {'authored_current_state':''.join(state).strip() or None,
            'currentness':'authored claims; not independently verified',
            'latest_verification_note':notes[0] if notes else None,
            'historical_verification_notes':notes[1:],
            'body_markdown':''.join(body),'history_markdown':''.join(history),
            'section_index':headings,'qualifier_review_candidates':candidates,
            'limits':'First listed note is a recorded verification, not current deployment. History is projected, never rewritten. Body qualifiers stay visible for review.'}


def collect_pages(report: dict, read_page, selected_pages=()) -> dict:
    names={row['path'] for row in report['cards']}
    names.update(selected_pages)
    names.update(page['path'] for row in report['impact'] for page in row['pages'])
    return {name:page_projection(read_page(name)) for name in sorted(names)}


def summary(value: dict) -> dict:
    native=value['native_report'];reading=value.get('prepared_reading',{})
    return {'selected_wiki_pages':reading.get('selected_wiki_pages',[]),
            'unexpanded_candidates':native['omitted'],
            'unregistered_files':[row['file'] for row in native['impact'] if row['unregistered']],
            'preparation':reading.get('preparation',{'reading_before_edits':'not established','status':'older capture; no preparation observation'}),
            'files':[{'file':row['file'],'pages':[page['path'] for page in row['pages']],
                      'unregistered':row['unregistered']} for row in native['impact']],
            'pages':[{'path':name,'current_state_declared':page['authored_current_state'] is not None,
                      'historical_notes':len(page['historical_verification_notes']),
                      'qualifiers_needing_review':len(page['qualifier_review_candidates'])}
                     for name,page in reading.get('pages',{}).items()],
            'path_bases':{'source_root':value['root'],'wiki_root':value['wiki_root'],
                          'peers':{alias:row['root'] for alias,row in value.get('peers',{}).items()}},
            'source_revision':value['base']['head'],
            'observed_revisions':reading.get('observed_revisions',{}),
            'native_exit_code':value['native_exit_code'],
            'reading_state':'Complete scope index only; page bodies and feature records are not delivered or acknowledged as read.',
            'limits':'Caller-supplied revision observations and authored state are separate. No reading, correctness, adoption or runtime acceptance claim.'}


def render_summary(view: dict, artifact: str, budget: int=6000) -> str:
    lines=['UNEXPANDED CANDIDATES (not read):']
    lines.extend('  '+str(row.get('path','?'))+' — '+str(row.get('title','')) for row in view['unexpanded_candidates'])
    if not view['unexpanded_candidates']:lines.append('  none declared')
    lines.append('UNREGISTERED FILES: '+(', '.join(view['unregistered_files']) or 'none'))
    changes=view['preparation'].get('selected_paths_with_changes',[])
    lines.append('EXISTING SELECTED CHANGES: '+(', '.join(changes) or 'none observed / see preparation record'))
    lines.append('Reading before edits: '+view['preparation']['reading_before_edits'])
    bases=view['path_bases']
    lines.append('PATH BASES: source='+bases['source_root']+'; Wiki pages='+bases['source_root']+'/'+bases['wiki_root'])
    if bases['peers']:lines.append('PEER SOURCE BASES: '+', '.join(alias+'='+root for alias,root in bases['peers'].items()))
    lines.append('FILE → ALL DECLARED OWNER PAGES:')
    lines.extend('  '+row['file']+' → '+(', '.join(row['pages']) or 'UNREGISTERED') for row in view['files'])
    if view.get('selected_wiki_pages'):
        lines.append('DIRECTLY SELECTED WIKI PAGES (not owner declarations):')
        lines.extend('  '+row['file']+' → '+row['path']+' ['+row['status']+']' for row in view['selected_wiki_pages'])
    lines.append('PAGE STATE (authored, not live verification):')
    lines.extend(f"  {p['path']}: current={'declared' if p['current_state_declared'] else 'unknown'}; history={p['historical_notes']}; qualifiers to review={p['qualifiers_needing_review']}" for p in view['pages'])
    if view['observed_revisions']:
        lines.append('CALLER-DECLARED REVISIONS (not live verification): '+', '.join(label+'='+row['resolved_sha'] for label,row in view['observed_revisions'].items()))
    lines.extend(['Source: '+view['source_revision'],'Freshness: '+view.get('freshness','capture-time data'),
                  'Complete artifact: '+artifact,
                  'Expand: show --capture <artifact> --view impact --path <file>; --view page|history --path <page>',view['reading_state']])
    text='\n'.join(lines)+'\n'
    if len(text.encode('utf-8'))>budget:
        return (f"Context summary not delivered: {len(view['files'])} files, {len(view['unexpanded_candidates'])} unexpanded candidates; "
                f"complete summary needs {len(text.encode('utf-8'))} bytes (budget {budget}). No partial index is presented.\n"
                f"Complete artifact: {artifact}\nUse show --capture <artifact> --view impact --path <exact-file>, or --format json for the complete index.\n")
    return text


def select_section(markdown: str, title: str) -> str:
    lines=markdown.splitlines(keepends=True);headings=[];fence=None
    for i,line in enumerate(lines):
        marker,fence=fence_transition(line,fence)
        if marker:continue
        m=None if fence else re.match(r'^(#{1,6})\s+(.+?)\s*$',line)
        if m:headings.append((i,len(m[1]),m[2]))
    hits=[(i,level) for i,level,name in headings if name==title]
    if len(hits)!=1:raise ValueError('Select one exact unique heading from section_index')
    start,level=hits[0]
    end=next((i for i,depth,_ in headings if i>start and depth<=level),len(lines))
    return ''.join(lines[start:end])


def render_page(view: dict, artifact: str, history: bool=False, section: str | None=None, budget: int=6000) -> str:
    if history:
        text='HISTORICAL EVIDENCE (not current state)\n'+(select_section(view['history_markdown'],section) if section else view['history_markdown'])+'\n'+ '\n'.join(n['text'] for n in view['historical_verification_notes'])
    else:
        body=select_section(view['body_markdown'],section) if section else view['body_markdown']
        if section:
            # A requested body section must remain readable even when separate
            # state or verification fields are large. Full metadata stays saved.
            text=('SELECTED AUTHORED SECTION (not independently verified)\n'
                  +'Current state: '+('declared; read its section separately' if view['authored_current_state'] else 'unknown')
                  +'; recorded verification metadata is available with --format json.\n'+body)
        else:
            text=('AUTHORED CURRENT STATE (not independently verified)\n'+(view['authored_current_state'] or 'Not declared; do not infer it from the latest note.')+
                  '\nLATEST LISTED VERIFICATION NOTE (recorded evidence, not deployment)\n'+str(view['latest_verification_note'])+
                  '\nAUTHORED BODY — qualifiers may need owner review\n'+body)
    if len(text.encode('utf-8'))>budget:
        headings='\n'.join('  '+row['title'] for row in view['section_index'] if row['history']==history)
        return ('Page body not delivered: exceeds display budget. Authored current state: '+('declared' if view['authored_current_state'] else 'unknown')+'; verification notes are recorded evidence, not current deployment. Captured text is preserved in '+artifact+
                '\nChoose --section <exact-heading> or --format json. Section index:\n'+headings+'\n')
    return text+'\nHistorical material is separate: --view history. Freshness: '+view['freshness']+'\n'
