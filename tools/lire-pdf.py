import zlib, re, sys
def streams(data):
    for m in re.finditer(rb'stream\r?\n', data):
        s=m.end(); e=data.find(b'endstream', s)
        if e<0: continue
        try: yield zlib.decompress(data[s:e])
        except Exception: pass
def unescape(b):
    out=bytearray(); i=0
    mp={0x6e:10,0x72:13,0x74:9,0x62:8,0x66:12,0x28:40,0x29:41,0x5c:92}
    while i<len(b):
        c=b[i]
        if c==0x5c and i+1<len(b):
            n=b[i+1]
            if n in mp: out.append(mp[n]); i+=2; continue
            if 0x30<=n<=0x37:
                j=i+1; o=b''
                while j<len(b) and 0x30<=b[j]<=0x37 and len(o)<3: o+=bytes([b[j]]); j+=1
                out.append(int(o,8)&0xFF); i=j; continue
            out.append(n); i+=2; continue
        out.append(c); i+=1
    return bytes(out)
LET=set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZéèêàçùûôîï")
def score(s):
    if not s: return -1
    return sum(1 for c in s if c in LET or c in " ,.:;-'()%/0123456789")/len(s)
def shift(s,k):
    return ''.join(chr(((ord(c)+k)%256)) if 32<=ord(c)<256 else c for c in s)
def best(s):
    cands=[s, shift(s,29), shift(s,-29)]
    return max(cands, key=score)
TOK=re.compile(rb'\((?:\\.|[^\\()])*\)|<[0-9A-Fa-f\s]*>|TJ|Tj|Td|TD|T\*|Tm|BT|ET')
def text_of(s):
    lines=[]; cur=[]
    for m in TOK.finditer(s):
        t=m.group()
        if t in (b'Td',b'TD',b'T*',b'Tm',b'ET',b'BT'):
            if cur: lines.append(''.join(cur)); cur=[]
            continue
        if t in (b'TJ',b'Tj'): continue
        if t.startswith(b'('): cur.append(unescape(t[1:-1]).decode('latin-1'))
        elif t.startswith(b'<'):
            h=re.sub(rb'\s',b'',t[1:-1])
            try:
                raw=bytes.fromhex(h.decode())
                cur.append(raw.decode('utf-16-be') if raw.count(0)>len(raw)//3 else raw.decode('latin-1'))
            except Exception: pass
    if cur: lines.append(''.join(cur))
    return [best(l) for l in lines]
for path in sys.argv[1:]:
    data=open(path,'rb').read()
    for i,s in enumerate(streams(data)):
        ls=[l.strip() for l in text_of(s) if l.strip() and score(l)>0.55]
        if not ls: continue
        print(f"\n########## flux {i} ##########")
        buf=""
        for l in ls:
            if re.fullmatch(r'(fr-BE|nl-NL|en-US|[A-Z]|)', l): continue
            buf += (" " if buf and not buf.endswith("-") else "") + l
            if len(buf)>110: print(buf); buf=""
        if buf: print(buf)
