#!/usr/bin/env python3
"""Export user/assistant dialogue to Markdown and JSONL; never export tool/reasoning logs.

Reads the two explicitly named RV32 sessions in the original machine. Outputs
ordinary archive files under conversations/rv32, not editor state databases.
"""
import argparse
import base64
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re

SESSIONS = [
    ('RV32', '01a072c8-89a8-7710-a44d-6c5db46dcb14',
     'sessions/2026/09/05/rollout-2026-09-05T20-15-40-01a072c8-89a8-7710-a44d-6c5db46dcb14.jsonl'),
    ('RV32 Q&A', '01a0fac6-cb70-7592-ac85-0ba8d77920db',
     'sessions/2026/10/02/rollout-2026-10-02T06-02-07-01a0fac6-cb70-7592-ac85-0ba8d77920db.jsonl'),
]
SECRET_PATTERNS = {
    'private-key': re.compile(r'-----BEGIN (?:OPENSSH |RSA |EC |DSA |ENCRYPTED )?PRIVATE KEY-----.*?-----END (?:OPENSSH |RSA |EC |DSA |ENCRYPTED )?PRIVATE KEY-----', re.S),
    'github-token': re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b'),
    'openai-key': re.compile(r'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}\b'),
    'aws-key': re.compile(r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    'google-key': re.compile(r'\bAIza[A-Za-z0-9_-]{30,}\b'),
    'credential-url': re.compile(r'https?://[^\s/:@]+:[^\s/@]{4,}@'),
    'bearer-token': re.compile(r'(?i)\bBearer\s+[A-Za-z0-9_.+/=-]{24,}'),
}
ASSIGNMENT = re.compile(r'''(?im)(\b[\w.\-]*(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)["']?\s*[=:]\s*["']?)([^\s"',#;]{8,})''')

def phase(value):
    if value in ['final', 'final_answer', 'FinalAnswer']:
        return 'final'
    if value in ['commentary', 'Commentary']:
        return 'commentary'
    return value

def redact(text, counts):
    for label, regex in SECRET_PATTERNS.items():
        text, n = regex.subn('[REDACTED:' + label + ']', text)
        counts[label] += n
    def assigned(match):
        value = match.group(2)
        if value.startswith(('$', '<', '[REDACTED', 'os.', 'getenv', 'process.env',
                             'YOUR_', 'your_', 'example', 'EXAMPLE')):
            return match.group(0)
        counts['assigned-secret'] += 1
        return match.group(1) + '[REDACTED:assigned-secret]'
    return ASSIGNMENT.sub(assigned, text)

def content_parts(parts, output, assets):
    texts = []; images = []
    if isinstance(parts, str):
        return parts, images
    for item in parts or []:
        if not isinstance(item, dict):
            continue
        if isinstance(item.get('text'), str):
            texts.append(item['text'])
        url = item.get('image_url', '')
        if isinstance(url, dict):
            url = url.get('url', '')
        if isinstance(url, str) and url.startswith('data:image/'):
            header, encoded = url.split(',', 1)
            data = base64.b64decode(encoded)
            sha = hashlib.sha256(data).hexdigest()
            extension = '.png' if 'image/png' in header else '.jpg'
            name = 'assets/' + sha[:16] + extension
            (output / 'assets').mkdir(exist_ok=True)
            (output / name).write_bytes(data)
            assets[name] = {'sha256': sha, 'bytes': len(data)}
            images.append(name)
        elif isinstance(url, str) and url:
            texts.append('[图片引用：' + url + ']')
    return '\n'.join(texts), images

def fingerprint(message):
    text = message['text']
    if message['role'] == 'assistant':
        text = re.sub(r'<oai-mem-citation>.*?</oai-mem-citation>', '', text, flags=re.S)
    return (message['role'], message['phase'], text.strip(), tuple(message['images']))

def timestamp_label(value):
    # All source timestamps are UTC. Keep that explicit in the public archive.
    if not value:
        return '时间未知'
    label = value.replace('T', ' ')
    return (label[:-1] if label.endswith('Z') else label) + ' UTC'

def export_session(title, session_id, source, output):
    event_messages = []; response_messages = []; bad = []; stats = Counter()
    assets = {}; total_records = 0; sha = hashlib.sha256(); first = None; last = None
    with source.open('rb') as stream:
        for line_number, raw in enumerate(stream, 1):
            sha.update(raw)
            try:
                record = json.loads(raw)
            except (json.JSONDecodeError, UnicodeDecodeError):
                fields = re.findall(rb'(?<!\\)"(?:type|role)"\s*:\s*"([^"\\]*)"', raw[:700])
                bad.append({'line': line_number, 'bytes': len(raw),
                            'record_kinds': [x.decode('utf-8', errors='replace') for x in fields]})
                continue
            total_records += 1
            stamp = record.get('timestamp'); first = first or stamp; last = stamp
            payload = record.get('payload', {})
            role = None; parts = None; stage = None; origin = None
            if record.get('type') == 'event_msg' and payload.get('type') == 'item_completed':
                item = payload.get('item', {})
                if item.get('type') in ['UserMessage', 'AgentMessage']:
                    role = 'user' if item['type'] == 'UserMessage' else 'assistant'
                    parts = item.get('content'); stage = phase(item.get('phase')); origin = 'completed-item'
            elif record.get('type') == 'response_item' and payload.get('type') == 'message':
                if payload.get('role') in ['user', 'assistant']:
                    role = payload['role']; parts = payload.get('content')
                    stage = phase(payload.get('phase') or payload.get('channel')); origin = 'message'
            if role is None or stage in ['analysis', 'summary']:
                continue
            text, images = content_parts(parts, output, assets)
            if not text and not images:
                continue
            msg = {'timestamp': stamp, 'role': role, 'phase': stage, 'text': text,
                   'images': images, 'source_line': line_number, 'source_kind': origin}
            if origin == 'completed-item':
                event_messages.append(msg)
            else:
                response_messages.append(msg)

    # Keep all completed messages and any additional occurrences present only
    # in the response stream; duplicated persisted copies are not printed twice.
    available = Counter(fingerprint(x) for x in event_messages)
    completed_by_key = {}
    for message in event_messages:
        completed_by_key.setdefault(fingerprint(message), []).append(message)
    used = Counter(); merged = list(event_messages)
    for message in response_messages:
        key = fingerprint(message); used[key] += 1
        if used[key] > available[key]:
            merged.append(message)
        else:
            chosen = completed_by_key[key][used[key] - 1]
            if len(message['text']) > len(chosen['text']):
                # Keep visible citation footnotes without duplicating the reply.
                chosen['text'] = message['text']
    merged.sort(key=lambda x: (x['timestamp'] or '', x['source_line']))
    redactions = Counter()
    for number, message in enumerate(merged, 1):
        message['number'] = number
        message['text'] = redact(message['text'], redactions)
        message['text'] = re.sub('[\x00-\x08\x0b\x0c\x0e-\x1f]', '', message['text'])
        stats[message['role']] += 1

    stem = 'rv32' if title == 'RV32' else 'rv32-qa'
    folder = output / stem; folder.mkdir(exist_ok=True)
    files = []
    # Daily pages stay readable on GitHub, with further splitting at 80 messages.
    groups = []
    for message in merged:
        date = (message['timestamp'] or 'unknown')[:10]
        if not groups or groups[-1][0] != date or len(groups[-1][1]) >= 80:
            groups.append((date, []))
        groups[-1][1].append(message)
    date_parts = Counter()
    for date, messages in groups:
        date_parts[date] += 1
        filename = date + '-{:02d}.md'.format(date_parts[date])
        lines = ['# ' + title + ' · ' + date, '', '[返回归档目录](../README.md)', '',
                 '原始时间统一标为 UTC；正文保留当时讨论，不作为当前设计或测量结论。', '']
        for message in messages:
            label = '用户' if message['role'] == 'user' else '助手'
            if message['phase'] == 'commentary':
                label += '（进度）'
            lines += ['---', '', '## {:04d} · {}'.format(message['number'], label), '',
                      timestamp_label(message['timestamp']), '', message['text'], '']
            for name in message['images']:
                lines += ['![原对话图片](../' + name + ')', '']
        (folder / filename).write_text('\n'.join(lines), encoding='utf-8')
        files.append({'path': stem + '/' + filename, 'messages': len(messages),
                      'first_message': messages[0]['number'], 'last_message': messages[-1]['number']})
    archive = output / (stem + '.messages.jsonl.gz')
    with gzip.open(archive, 'wt', encoding='utf-8') as stream:
        for message in merged:
            stream.write(json.dumps(message, ensure_ascii=False) + '\n')
    result = {'title': title, 'session_id': session_id, 'source_basename': source.name,
              'source_bytes': source.stat().st_size, 'source_sha256': sha.hexdigest(),
              'source_records_parsed': total_records, 'first_record': first, 'last_record': last,
              'completed_messages': len(event_messages), 'response_messages': len(response_messages),
              'exported_messages': len(merged), 'by_role': dict(stats), 'pages': files,
              'invalid_non_dialogue_records': bad, 'redactions': dict(redactions),
              'image_assets': assets, 'structured_archive': archive.name}
    print(json.dumps({k: result[k] for k in ['title', 'exported_messages', 'by_role', 'redactions',
                                           'invalid_non_dialogue_records']}, ensure_ascii=False), flush=True)
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex-home', type=Path, default=Path.home() / '.codex')
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1] / 'conversations/rv32')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if any(args.output.iterdir()):
        raise SystemExit('Output must be empty to avoid mixing different exports')
    sessions = [export_session(title, sid, args.codex_home / relative, args.output)
                for title, sid, relative in SESSIONS]
    manifest = {'export_date': '2026-11-16', 'format': 'user/assistant dialogue archive',
                'sessions': sessions,
                'excluded': ['system/developer messages', 'reasoning records', 'tool raw output',
                             'session state databases', 'credentials', 'other unrelated conversations']}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = ['# RV32 对话归档', '',
             '归档日期：2026-11-16。保存两段实际命名为 **RV32** 和 **RV32 Q&A** 的对话。', '',
             '按日期、消息顺序保存逐条提问与助手答复，包括进度回复；不是内容摘要。原时间使用 UTC。', '',
             '同一消息在日志中的重复副本会合并，保留两种消息流中额外存在的内容。', '',
             '工具执行原始输出、推理记录、系统/开发者消息、登录状态与密钥不公开上传。', '',
             '这是可阅读的 Markdown 和结构化 JSONL 文本归档，不会自动写入新机的聊天列表或会话数据库。', '',
             '更早的 riscv32 core 及其多个巨型恢复副本不在本次两个命名会话的范围内。', '',
             '正文中的旧机绝对路径和当时的设计/测试结论均为历史记录。当前源码请查阅 '
             '[ysyx 迁移快照](https://github.com/roundeodo/ysyx/tree/migration-2026-11-16)。', '']
    for session in sessions:
        lines += ['## ' + session['title'], '',
                  '- 会话 ID：`' + session['session_id'] + '`',
                  '- 导出消息：{}（用户 {}，助手 {}）。'.format(session['exported_messages'],
                      session['by_role'].get('user', 0), session['by_role'].get('assistant', 0)),
                  '- 结构化归档：[' + session['structured_archive'] + '](' + session['structured_archive'] + ')', '']
        if session['invalid_non_dialogue_records']:
            lines += ['原始日志有 {} 条损坏记录，属于推理/命令执行日志，不是用户或助手正文；'
                      '这些记录不进入本归档。行号与类型见 manifest.json。'.format(len(session['invalid_non_dialogue_records'])), '']
        for page in session['pages']:
            lines.append('- [{}]({}) · 消息 {}–{}'.format(Path(page['path']).stem,
                page['path'], page['first_message'], page['last_message']))
        lines.append('')
    (args.output / 'README.md').write_text('\n'.join(lines), encoding='utf-8')
    checksums = []
    for path in sorted(args.output.rglob('*')):
        if path.is_file():
            checksums.append(hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + str(path.relative_to(args.output)))
    (args.output / 'SHA256SUMS.txt').write_text('\n'.join(checksums) + '\n', encoding='utf-8')

if __name__ == '__main__':
    main()
