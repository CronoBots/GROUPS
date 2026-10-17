#!/usr/bin/env python3
"""Le QR code du guide d'installation, à la manière de celui de Pino
(le client, le 17/10/2026). Il mène au site avec #installer : le guide
s'ouvre seul à l'arrivée. Points ronds bleu nuit sur blanc, yeux arrondis
au cœur cyan foncé : un cyan clair, le lecteur le prenait pour du blanc et
le code ne se lisait plus (jsQR, le 17/10/2026).

    python3 tools/qr-installer.py      # réécrit qr-installer.svg
Dépendance : pip install qrcode
"""
import os, qrcode
URL = "https://cronobots.github.io/groups/#installer"
FOND, ENCRE, VIF = "#FFFFFF", "#111727", "#1F6F8B"
q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=0)
q.add_data(URL); q.make(fit=True)
M = q.get_matrix(); N = len(M); QZ = 4; T = N + 2 * QZ; u = 10
def oeil(r, c): return (r < 7 and c < 7) or (r < 7 and c >= N - 7) or (r >= N - 7 and c < 7)
out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {T*u} {T*u}" width="{T*u}" height="{T*u}">',
       f'<rect width="100%" height="100%" rx="{2*u}" fill="{FOND}"/>', f'<g fill="{ENCRE}">']
for r in range(N):
    for c in range(N):
        if M[r][c] and not oeil(r, c):
            out.append(f'<circle cx="{(QZ+c+.5)*u:g}" cy="{(QZ+r+.5)*u:g}" r="{.46*u:g}"/>')
out.append('</g>')
for r0, c0 in [(0, 0), (0, N - 7), (N - 7, 0)]:
    x, y = (QZ + c0) * u, (QZ + r0) * u
    out.append(f'<rect x="{x}" y="{y}" width="{7*u}" height="{7*u}" rx="{2.2*u:g}" fill="{ENCRE}"/>')
    out.append(f'<rect x="{x+u}" y="{y+u}" width="{5*u}" height="{5*u}" rx="{1.4*u:g}" fill="{FOND}"/>')
    out.append(f'<rect x="{x+2*u}" y="{y+2*u}" width="{3*u}" height="{3*u}" rx="{.9*u:g}" fill="{VIF}"/>')
out.append('</svg>')
dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "qr-installer.svg")
open(dest, "w").write("\n".join(out) + "\n")
print(f"{dest} : {N}×{N} modules, {URL}")
