// Reads a CSV from the repository root at build time, so the page shows
// exactly what data/ holds (single source; the numbers cannot drift).
// astro build runs with cwd = site/, hence the '..'.
import fs from 'node:fs';
import path from 'node:path';

export function readCsv(relPath) {
  const text = fs.readFileSync(path.resolve(process.cwd(), '..', relPath), 'utf-8');
  const rows = [];
  let row = [], field = '', quoted = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') quoted = false;
      else field += c;
    } else if (c === '"') quoted = true;
    else if (c === ',') { row.push(field); field = ''; }
    else if (c === '\n' || c === '\r') {
      if (c === '\r' && text[i + 1] === '\n') i++;
      row.push(field); rows.push(row); row = []; field = '';
    } else field += c;
  }
  if (field || row.length) { row.push(field); rows.push(row); }
  const [header, ...body] = rows.filter((r) => r.length > 1 || r[0] !== '');
  return body.map((r) => Object.fromEntries(header.map((h, i) => [h, r[i] ?? ''])));
}
