"""Pure reading projections: complete scope indexes, authored state and history.

No Git, native execution, writes or deployment inference. The workflow caller
supplies captured Markdown, identities and freshness observations.
"""
from __future__ import annotations
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import sys

HISTORY = re.compile(r'^(?:history|historical (?:evidence|notes|records)|verification history|review history|核验历史|archive|archived|历史|历史记录|历史证据|归档|迁出的历史)(?:\s*[（(].*[)）])?$',re.I)
CURRENT = re.compile(r'^(?P<label>current(?: state| status)?|当前(?:状态|现状)?|现状)(?:\s*[（(](?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})[)）])?$',re.I)
QUALIFIER = re.compile(r'未合入|未部署|未上线|待部署|源码候选|not (?:yet )?(?:merged|deployed|released)|branch.only',re.I)
VERIFY = re.compile(r'^>\s*(?:核验|Reviewed|Verification)\s*[:：]\s*(.*)',re.I)
GENERATED_BEGIN = re.compile(r'^\s{0,3}<!--\s*(?:[\w.-]+:begin(?=\W|$)|begin(?=\W|$))',re.I)


def fence_transition(line: str, fence: str | None) -> tuple[bool, str | None]:
    marker=re.match(r'^\s{0,3}(`{3,}|~{3,})(.*)$',line)
    if not marker:return False,fence
    token=marker[1]
    if fence is None:return True,token
    if token[0]==fence[0] and len(token)>=len(fence) and not marker[2].strip():return True,None
    return True,fence


def parse_heading(line):
    match=re.match(r'^ {0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*$',line.rstrip('\r\n'))
    if not match:return None
    title=re.sub(r'[ \t]+#+[ \t]*$','',match[2] or '').strip()
    return len(match[1]),title


def page_projection(text: str) -> dict:
    body=[]; history=[]; notes=[]; state=[]; candidates=[]; headings=[]
    history_level=None; current_level=None; fence=None
    for number,line in enumerate(text.splitlines(keepends=True),1):
        marker,fence=fence_transition(line,fence)
        fenced=marker or fence is not None
        if not fenced and GENERATED_BEGIN.match(line):
            current_level=None; history_level=None
        heading=None if fenced else parse_heading(line)
        if heading:
            level,title=heading
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
            'selected_cards':[{'path':row['path'],'title':row['title']} for row in native['cards']],
            'unregistered_files':[row['file'] for row in native['impact'] if row['unregistered']],
            'preparation':reading.get('preparation',{'reading_before_edits':'not established','status':'older capture; no preparation observation'}),
            'files':[{'file':row['file'],'pages':[page['path'] for page in row['pages']],
                      'unregistered':row['unregistered']} for row in native['impact']],
            'pages':[{'path':name,'current_state_declared':page['authored_current_state'] is not None,
                      'historical_notes':len(page['historical_verification_notes']),
                      'history_present':bool(page['history_markdown'].strip() or page['historical_verification_notes']),
                      'qualifiers_needing_review':len(page['qualifier_review_candidates'])}
                     for name,page in reading.get('pages',{}).items()],
            'path_bases':{'source_root':value['root'],'wiki_root':value['wiki_root'],
                          'peers':{alias:row['root'] for alias,row in value.get('peers',{}).items()}},
            'source_revision':value['base']['head'],
            'observed_revisions':reading.get('observed_revisions',{}),
            'native_exit_code':value['native_exit_code'],
            'reading_state':'Complete scope index only; page bodies and feature records are not delivered or acknowledged as read.',
            'limits':'Caller-supplied revision observations and authored state are separate. No reading, correctness, adoption or runtime acceptance claim.'}


def summary_text(view: dict, artifact: str) -> str:
    files=['FILE → ALL DECLARED OWNER PAGES:']
    files.extend('  '+row['file']+' → '+(', '.join(row['pages']) or 'UNREGISTERED') for row in view['files'])
    if not view['files']:files.append('  no files selected; file owners unknown, not none (prepare with --files for owners)')
    cards=[]
    if 'selected_cards' in view:
        cards.append('SELECTED FEATURE CARDS (query match, not read):')
        cards.extend('  '+row['path']+' — '+row['title'] for row in view['selected_cards'])
        if not view['selected_cards']:cards.append('  none matched')
    # Known-file context must survive the first bounded viewport, even for broad queries.
    # Query-only exploration starts with its actual matches; the complete inventory still follows.
    lines=[f"SCOPE: {len(view['files'])} files; {len(view['unexpanded_candidates'])} unexpanded candidates (not read)"]
    lines.extend(files+cards if view['files'] else cards+files)
    lines.append('UNREGISTERED FILES: '+(', '.join(view['unregistered_files']) or 'none'))
    changes=view['preparation'].get('selected_paths_with_changes',[])
    lines.append('EXISTING SELECTED CHANGES: '+(', '.join(changes) or 'none observed / see preparation record'))
    lines.append('Reading before edits: '+view['preparation']['reading_before_edits'])
    lines.append('NATIVE RESULT: exit '+str(view['native_exit_code'])+'; saved report, not a completion claim')
    bases=view['path_bases']
    lines.append('PATH BASES: source='+bases['source_root']+'; Wiki pages='+bases['source_root']+'/'+bases['wiki_root'])
    if bases['peers']:lines.append('PEER SOURCE BASES: '+', '.join(alias+'='+root for alias,root in bases['peers'].items()))
    if view.get('selected_wiki_pages'):
        lines.append('DIRECTLY SELECTED WIKI PAGES (not owner declarations):')
        lines.extend('  '+row['file']+' → '+row['path']+' ['+row['status']+']' for row in view['selected_wiki_pages'])
    lines.append('UNEXPANDED CANDIDATES (not read):')
    lines.extend('  '+str(row.get('path','?'))+' — '+str(row.get('title','')) for row in view['unexpanded_candidates'])
    if not view['unexpanded_candidates']:lines.append('  none declared')
    lines.append('PAGE STATE (authored, not live verification):')
    lines.extend(f"  {p['path']}: current={'declared' if p['current_state_declared'] else 'unknown'}; history={'present' if p.get('history_present', p['historical_notes'] > 0) else 'none'}; older notes={p['historical_notes']}; qualifiers to review={p['qualifiers_needing_review']}" for p in view['pages'])
    if view['observed_revisions']:
        lines.append('CALLER-DECLARED REVISIONS (not live verification): '+', '.join(label+'='+row['resolved_sha'] for label,row in view['observed_revisions'].items()))
    for key in ('task_scope', 'read_only_baseline'):
        if key in view:
            lines.append(key + ' (saved task data):\n' + json.dumps(view[key], ensure_ascii=False, indent=2))
    lines.extend(['Source: '+view['source_revision'],'Freshness: '+view.get('freshness','capture-time data'),
                  'Complete artifact: '+artifact,
                  'Expand: show --capture <artifact> --view impact --path <file>; --view page|history --path <page> [--section-index lists saved headings with exact open commands]',view['reading_state']])
    text='\n'.join(lines)+'\n'
    return text


def render_summary(view: dict, artifact: str, budget: int=6000, *, cursor=None, command=None, line_budget=60, early_continuation=False) -> str:
    command = command or read_command(artifact, 'summary')
    return text_page(summary_text(view, artifact), 'summary:' + artifact, command,
                     budget=budget, cursor=cursor, line_budget=line_budget, early_continuation=early_continuation)['text']


def locator_summary(view: dict) -> dict:
    """A saved-context locator, not a second delivery of the complete index."""
    return {'selected_files':len(view['files']), 'saved_pages':len(view['pages']),
            'unregistered':len(view['unregistered_files']),
            'unexpanded_candidates':len(view['unexpanded_candidates']),
            'preparation_changes':len(view['preparation'].get('selected_paths_with_changes',[])),
            'source_revision':view['source_revision'], 'native_exit_code':view['native_exit_code'],
            'limits':'Details remain in the saved capture; not redelivered or acknowledged as read.'}


def render_locator(view: dict, artifact: str, budget: int=6000, *, cursor=None, command=None, line_budget=60, snapshot_only=False, early_continuation=False) -> str:
    full=read_command(artifact,'summary')
    continuation=list(command or read_command(artifact,'locator'))
    if snapshot_only:
        full+=['--snapshot-only']
        if '--snapshot-only' not in continuation:continuation+=['--snapshot-only']
    text=('SAVED CONTEXT LOCATOR — complete details are retained, not repeated\n'
          +f"Scope counts: files={view['selected_files']}; saved pages={view['saved_pages']}; unregistered={view['unregistered']}; unexpanded candidates={view['unexpanded_candidates']}; preparation changes={view['preparation_changes']}\n"
          +f"Source: {view['source_revision']}; native result: exit {view['native_exit_code']}\n"
          +'Freshness: '+view.get('freshness','capture-time data')+'\n'
          +view['limits']+'\n'
          +'Read full context: '+shell_command(full)+'\n')
    return text_page(text, 'locator:'+artifact, continuation,
                     budget=budget,cursor=cursor,line_budget=line_budget, early_continuation=early_continuation)['text']


def saved_headings(markdown: str):
    """Headings exactly as --section sees them in one saved projection text."""
    lines=markdown.splitlines(keepends=True);headings=[];fence=None
    for i,line in enumerate(lines):
        marker,fence=fence_transition(line,fence)
        if marker:continue
        m=None if fence else parse_heading(line)
        if m:headings.append((i,*m))
    return lines,headings


def select_section(markdown: str, title: str) -> str:
    lines,headings=saved_headings(markdown)
    hits=[(i,level) for i,level,name in headings if name==title]
    if len(hits)!=1:raise ValueError('Select one exact unique heading; list saved headings and open commands with --section-index')
    start,level=hits[0]
    end=next((i for i,depth,_ in headings if i>start and depth<=level),len(lines))
    return ''.join(lines[start:end])


def section_argv(title: str) -> list[str]:
    # argparse would read a leading-dash value as an option; the joined form is exact.
    return ['--section='+title] if title.startswith('-') else ['--section',title]


def section_outline(view: dict, history: bool, open_base: list[str]) -> dict:
    """Saved heading outline for one page projection; never a live reconstruction.

    Listing comes from saved section_index metadata. Selectability is checked
    against the same saved body/history text --section reads, so only unique
    titled headings get an open command.
    """
    rows=view.get('section_index');source=view.get('history_markdown' if history else 'body_markdown')
    result={'path':view.get('path'),'view':'history' if history else 'page','freshness':view.get('freshness'),
            'limits':'Saved authored headings only; listing or opening a section is not a reading acknowledgement or verification.'}
    if (not isinstance(rows,list) or not isinstance(source,str)
            or any(not isinstance(r,dict) or not isinstance(r.get('title'),str) or type(r.get('history')) is not bool for r in rows)):
        result['section_outline']={'status':'unknown','sections':[],
                                   'meaning':'Saved capture has no usable section metadata; nothing was reconstructed from live files.'}
        return result
    chosen=[r for r in rows if r['history']==history]
    _,parsed=saved_headings(source)
    counts={}
    for _,_,title in parsed:counts[title]=counts.get(title,0)+1
    aligned=[title for _,_,title in parsed]==[r['title'] for r in chosen]
    sections=[]
    for number,row in enumerate(chosen):
        title=row['title'];matches=counts.get(title,0)
        status=('untitled' if not title else 'selectable' if matches==1 else 'ambiguous' if matches>1 else 'not in saved text')
        entry={'title':title,'level':parsed[number][1] if aligned else None,
               'line':row.get('line') if type(row.get('line')) is int else None,
               'status':status,'matches':matches}
        if status=='selectable':entry['open_argv']=[*open_base,*section_argv(title)]
        sections.append(entry)
    result['section_outline']={'status':'recorded' if chosen else 'empty','sections':sections,
                               'other_headings':len(rows)-len(chosen)}
    return result


def render_outline(outline: dict, identity: str, command: list[str], *, budget: int=6000, cursor=None, line_budget: int=60, early_continuation: bool=False) -> str:
    data=outline['section_outline'];history=outline['view']=='history'
    label='HISTORICAL' if history else 'AUTHORED'
    lines=[f"SAVED {label} SECTION OUTLINE — {outline['path']} (headings only; not read, not verified)",
           'Freshness: '+str(outline['freshness'])]
    if data['status']=='unknown':
        lines.append('Section outline: UNKNOWN — '+data['meaning'])
    else:
        rows=data['sections']
        other=('current/body' if history else 'history')
        lines.append(f"Headings: {len(rows)}; openable={sum(r['status']=='selectable' for r in rows)}; "
                     f"{other} headings listed separately={data['other_headings']}"
                     +('' if history else ' (--view history --section-index)'))
        if not rows:lines.append('Saved metadata: no headings recorded in this '+('history' if history else 'body')+' text.')
        for number,row in enumerate(rows,1):
            mark='#'*row['level'] if row['level'] else '#?'
            where=f"L{row['line']} " if row['line'] else ''
            lines.append(f"[{number}] {where}{mark} {row['title']}")
            if row['status']=='ambiguous':lines.append(f"    AMBIGUOUS: {row['matches']} identical headings; --section cannot select one; read the whole view with its cursor")
            elif row['status']=='untitled':lines.append('    UNTITLED: --section cannot select an empty heading')
            elif row['status']!='selectable':lines.append('    NOT OPENABLE: heading absent from saved selectable text')
        # Repeated absolute capture/CLI paths must not bury the compact heading inventory.
        # Preserve every exact open command in the same bounded continuation after it.
        if any(row['status']=='selectable' for row in rows):
            lines.append('EXACT OPEN COMMANDS (for the inventory above; continuation may be needed):')
            for row in rows:
                if row['status']=='selectable':lines.append('    OPEN: '+shell_command(row['open_argv']))
    lines.append(outline['limits'])
    return text_page('\n'.join(lines)+'\n',identity,command,budget=budget,cursor=cursor,line_budget=line_budget, early_continuation=early_continuation)['text']


def render_page(view: dict, artifact: str, history: bool=False, section: str | None=None, budget: int=6000, *, cursor=None, command=None, line_budget=60, early_continuation=False) -> str:
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
            declared=[row['title'] for row in view.get('section_index',[]) if not row['history'] and (match:=CURRENT.fullmatch(row['title'])) and match['date']] if view['authored_current_state'] else []
            declaration=('Declared current section: '+'; '.join(declared)+'\n') if declared else ''
            text=('AUTHORED CURRENT STATE (not independently verified)\n'+declaration+('Declared below in its original section.' if view['authored_current_state'] else 'Not declared; do not infer it from the latest note.')+
                  '\nLATEST LISTED VERIFICATION NOTE (recorded evidence, not deployment)\n'+str(view['latest_verification_note'])+
                  '\nAUTHORED BODY — qualifiers may need owner review\n'+body)
    text += '\nHistorical material is separate: --view history. Freshness: '+view['freshness']+'\n'
    command = command or read_command(artifact, 'history' if history else 'page', view.get('path'), section)
    identity = json.dumps([artifact, 'history' if history else 'page', view.get('path'), section], ensure_ascii=False)
    return text_page(text, identity, command, budget=budget, cursor=cursor, line_budget=line_budget, early_continuation=early_continuation)['text']


def read_command(artifact, view, path=None, section=None):
    command = [sys.executable, str(Path(__file__).with_name('workflow.py')), 'show',
               '--capture', artifact, '--view', view]
    if path is not None: command += ['--path', path]
    if section is not None: command += ['--section', section]
    return command


def shell_command(argv):
    if os.name == 'nt':
        # PowerShell also ends verbatim strings at typographic single quotes.
        return '& ' + ' '.join("'" + re.sub("(['‘’‚‛])", r'\1\1', a) + "'" for a in argv)
    return shlex.join(argv)


# CLI text parts, measured on stdout including print's final newline. Function
# defaults stay 6000/60 for explicit programmatic callers.
CLI_TEXT_BYTES = 4000
CLI_TEXT_LINES = 40


def text_page(text: str, identity: str, command: list[str], *, budget: int=6000, cursor: str | None=None, line_budget: int=60, early_continuation: bool=False) -> dict:
    """Bound every text view, including a single huge Unicode line, without loss.

    Cursors select text, never certify reading. Their digest rejects accidental
    reuse across changed content or a different capture/view/section.
    """
    if type(budget) is not int or budget < 256:
        raise ValueError('Display budget must be at least 256 bytes')
    if type(line_budget) is not int or line_budget < 8:
        raise ValueError('Display line budget must be at least 8')
    digest = hashlib.sha256((identity + '\0' + text).encode('utf-8')).hexdigest()
    start = 0
    if cursor is not None:
        try:
            value = json.loads(base64.urlsafe_b64decode(cursor.encode('ascii')).decode('utf-8'))
            if (not isinstance(value, dict) or value.get('digest') != digest
                    or type(value.get('offset')) is not int or not 0 < value['offset'] < len(text)):
                raise ValueError('mismatch')
            start = value['offset']
        except (ValueError, TypeError, UnicodeError, KeyError) as error:
            raise ValueError('Invalid or changed cursor; restart this exact saved view') from error

    def render(end):
        token = None
        if end < len(text):
            token = base64.urlsafe_b64encode(json.dumps({'digest':digest,'offset':end},separators=(',',':')).encode()).decode()
        header = f'DISPLAY {start}:{end} OF {len(text)} CHARACTERS — '+('PARTIAL; continue below' if token else 'COMPLETE VIEW')+'\n'
        # The same exact command is repeated on line 2 so a caller that keeps only
        # the first lines (head -N) still sees how to continue.
        if token and early_continuation:header += 'NEXT PART: '+shell_command([*command, '--cursor', token])+'\n'
        footer = ('\nNEXT: '+shell_command([*command, '--cursor', token])+'\n' if token else '\nCOMPLETE VIEW; not a reading acknowledgement.\n')
        return header + '--- CONTENT ---\n' + text[start:end] + '\n--- END CONTENT ---' + footer, token

    def fits(end):
        rendered,_=render(end)
        return len(rendered.encode('utf-8'))<=budget and len(rendered.splitlines())<=line_budget
    if fits(len(text)):
        result,token=render(len(text))
        return {'text':result,'content':text[start:],'start':start,'end':len(text),'total':len(text),'next_cursor':token}
    low, high = start, len(text)-1
    while low < high:
        middle = (low + high + 1)//2
        if fits(middle): low = middle
        else: high = middle - 1
    result, token = render(low)
    if (low == start and start < len(text)) or not fits(low):
        raise ValueError('Display budget cannot fit a continuation command; use a shorter artifact path or larger budget')
    return {'text':result,'content':text[start:low],'start':start,'end':low,'total':len(text),'next_cursor':token}


def heading_rows(text):
    rows=[]; fence=None; in_history=None
    lines=text.splitlines(keepends=True)
    for i,line in enumerate(lines):
        marker,fence=fence_transition(line,fence)
        if marker or fence is not None:continue
        m=parse_heading(line)
        if not m:continue
        depth,title=m
        if in_history is not None and depth<=in_history:in_history=None
        if HISTORY.fullmatch(title):in_history=depth
        rows.append((i,depth,title,in_history is not None))
    return lines,rows


def current_body(text):
    lines=text.splitlines(keepends=True)
    while lines and not lines[0].strip():lines.pop(0)
    while lines and not lines[-1].strip():lines.pop()
    return ''.join(lines).rstrip('\r\n')


def replace_current(text: str, current: str, recorded_at: str, verification: str | None=None) -> str:
    """Replace one authored current section; retain source evidence mechanically.

    Existing latest verification remains one recorded note for native compatibility;
    older notes and replaced state are archived. A caller may supply a new single
    verification note. Neither the old nor supplied note is certified as true.
    """
    if not isinstance(recorded_at,str) or not recorded_at or '\n' in recorded_at or '\r' in recorded_at:
        raise ValueError('State record timestamp must be a single nonempty line')
    current=current_body(current)
    if not current.strip():raise ValueError('A nonempty authored current state is required')
    _,new_rows=heading_rows(current)
    if any(depth<=2 or HISTORY.fullmatch(title) or CURRENT.fullmatch(title) for _,depth,title,_ in new_rows):
        raise ValueError('Supply current state body only, without current/history/top-level section headings')
    fence=None
    for line in current.splitlines():
        marker,fence=fence_transition(line,fence)
        if not marker and fence is None and VERIFY.match(line):
            raise ValueError('Verification notes are evidence, not authored current state')
    if fence is not None:raise ValueError('Current state body has an unclosed code fence')
    if verification is not None:
        verification=verification.strip()
        if ('\n' in verification or '\r' in verification or '｜' in verification
                or not VERIFY.fullmatch(verification)):
            raise ValueError('Supply one standalone verification line, without accumulated history')

    lines,rows=heading_rows(text)
    spans=[]
    for i,depth,title,historical in rows:
        if not historical and CURRENT.fullmatch(title):
            end=next((j for j,d,_,_ in rows if j>i and d<=depth),len(lines))
            fence=None
            for j in range(i+1,end):
                marker,fence=fence_transition(lines[j],fence)
                if not marker and fence is None and GENERATED_BEGIN.match(lines[j]):
                    end=j;break
            spans.append((i,end))
    projection=page_projection(text)
    current_note=projection['latest_verification_note']
    if len(spans)==1:
        a,b=spans[0]
        same_body=current_body(''.join(lines[a+1:b]))==current
        same_note=(verification is None or (current_note and VERIFY.fullmatch(verification)[1].strip()==current_note['text']))
        if same_body and same_note and not projection['historical_verification_notes']:
            return text

    removed=set();old=[];rewrites={}
    for a,b in spans:
        removed.update(range(a,b));old.append(''.join(lines[a:b]))
    fence=None;in_history=False;first=True;pending_note=None
    row_by_line={i:historical for i,_,_,historical in rows}
    for i,line in enumerate(lines):
        marker,fence=fence_transition(line,fence)
        if i in row_by_line:in_history=row_by_line[i]
        match=None if marker or fence is not None or in_history else VERIFY.match(line)
        if not match:continue
        if first:
            parts=[part.strip() for part in match[1].split('｜') if part.strip()]
            latest=(verification if verification is not None else line[:match.start(1)]+(parts[0] if parts else ''))
            newline='\r\n' if line.endswith('\r\n') else '\n'
            if i in removed:
                pending_note=latest+newline
            else:
                rewrites[i]=latest+newline
                if verification is not None or len(parts)>1:old.append(line)
            first=False
        elif i not in removed:
            removed.add(i);old.append(line)
    if first and verification is not None:pending_note=verification+'\n'
    kept_lines=[rewrites.get(i,line) for i,line in enumerate(lines) if i not in removed]
    if spans:
        # Replace in place: preamble, keyword/source metadata and introductory prose
        # must not accidentally become part of the new current-state section.
        insert=sum(1 for i in range(spans[0][0]) if i not in removed)
    else:
        _,kept_rows=heading_rows(''.join(kept_lines))
        insert=next((i for i,d,_,_ in kept_rows if d>1),len(kept_lines))
    heading=lines[spans[0][0]].rstrip('\r\n') if spans else '## Current state'
    if spans:
        depth,title=parse_heading(heading)
        match=CURRENT.fullmatch(title)
        if match and match['date']:heading='#'*depth+' '+match['label']
    section='\n'+heading+'\n\n'+current+'\n\n'
    if pending_note:section='\n'+pending_note+section
    kept_lines.insert(insert,section)
    updated=''.join(kept_lines)
    if old:
        archived='\n'.join(old)
        longest=max([len(m[0]) for m in re.finditer(r'`+',archived)]+[2])
        fence='`'*(longest+1)
        updated_lines,updated_rows=heading_rows(updated)
        history_heading=next(((i,d) for i,d,title,_ in reversed(updated_rows) if HISTORY.fullmatch(title)),None)
        if history_heading:
            a,depth=history_heading
            # The next heading can be preceded by its generated-block opener.
            # Inserting there puts authored history inside regenerable content.
            # Place the newest snapshot directly under the authored history heading.
            end=a+1
        else:
            updated_lines.append('\n## History\n');end=len(updated_lines)
        entry='\n### State snapshot '+recorded_at+'\n\n'+fence+'markdown\n'+archived
        if not archived.endswith('\n'):entry+='\n'
        entry+=fence+'\n'
        updated_lines.insert(end,entry)
        updated=''.join(updated_lines)
    return updated
