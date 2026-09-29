from flask import Flask, request, jsonify
import sqlite3
from datetime import date

app = Flask(__name__)
DB = "database.db"

HTML = r"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NEXA Smart Tracker</title>
<style>
*{box-sizing:border-box}body{margin:0;font:14px Arial;background:#070a12;color:#f5f7fb}.wrap{display:flex;min-height:100vh}.side{width:220px;padding:24px;border-right:1px solid #242b38;background:#090c14}.logo{width:40px;height:40px;border-radius:12px;display:grid;place-items:center;background:linear-gradient(135deg,#8b7cff,#39d7ff);font-weight:900}.brand{display:flex;gap:10px;align-items:center;margin-bottom:35px}.brand b{letter-spacing:3px}.muted,.ey{color:#8d97aa}.ey{font-size:10px;letter-spacing:2px}.nav button{display:block;width:100%;margin:6px 0;padding:12px;border:0;border-radius:10px;background:transparent;color:#8d97aa;text-align:left;cursor:pointer}.nav button.active,.nav button:hover{background:#171c2c;color:#fff}.main{flex:1;padding:35px}.top{display:flex;justify-content:space-between;gap:20px}.btn{padding:12px 17px;border:0;border-radius:11px;background:linear-gradient(135deg,#8b7cff,#639cff);color:#fff;font-weight:800;cursor:pointer}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:24px}.card,.panel{background:#101625;border:1px solid #252c39;border-radius:16px;padding:18px}.num{font-size:30px;font-weight:900;margin-top:8px}.row{display:grid;grid-template-columns:2fr 1fr;gap:12px;margin-top:12px}.bars{height:190px;display:flex;align-items:end;gap:10px}.bar{flex:1;min-height:30px;background:linear-gradient(#39d7ff,#8b7cff);border-radius:8px 8px 2px 2px}table{width:100%;border-collapse:collapse}th,td{padding:11px 7px;border-bottom:1px solid #252c39;text-align:left}th{font-size:10px;color:#8d97aa}.tag{padding:5px 8px;border-radius:20px;font-size:10px}.p{background:#123326;color:#48e6a2}.a{background:#34151b;color:#ff6b7a}.q{background:#342c14;color:#ffc957}.modal{position:fixed;inset:0;background:#000b;display:grid;place-items:center}.hide{display:none}.box{width:400px;background:#101625;border:1px solid #252c39;border-radius:18px;padding:24px}.box input,.box select{width:100%;padding:11px;margin:6px 0 13px;background:#080c15;color:#fff;border:1px solid #252c39;border-radius:9px}.close{float:right;background:none;border:0;color:#aaa;font-size:24px}@media(max-width:800px){.side{width:170px}.grid{grid-template-columns:repeat(2,1fr)}.row{grid-template-columns:1fr}}@media(max-width:600px){.wrap{display:block}.side{width:auto}.main{padding:18px}.grid{grid-template-columns:1fr}.top{display:block}}
</style></head><body><div class="wrap"><aside class="side"><div class="brand"><div class="logo">N</div><div><b>NEXA</b><div class="muted" style="font-size:10px">SMART TRACKER</div></div></div><nav><button class="active" onclick="show('dash',this)">▦ Dashboard</button><button onclick="show('records',this)">◫ Records</button><button onclick="show('analytics',this)">◒ Analytics</button></nav></aside>
<main class="main"><div class="top"><div><div class="ey">CONTROL CENTER</div><h1>Good morning, team ✦</h1><p class="muted">Turn raw records into useful insights.</p></div><button class="btn" onclick="openM()">+ Add record</button></div>
<section id="dash"><div class="grid"><div class="card"><div class="ey">TOTAL RECORDS</div><div class="num" id="t">0</div></div><div class="card"><div class="ey">PRESENT / DONE</div><div class="num" id="p">0</div></div><div class="card"><div class="ey">ABSENT / OPEN</div><div class="num" id="a">0</div></div><div class="card"><div class="ey">SUCCESS RATE</div><div class="num" id="r">0%</div></div></div>
<div class="row"><div class="panel"><div class="ey">ACTIVITY</div><h2>Recent momentum</h2><div class="bars" id="bars"></div></div><div class="panel"><div class="ey">QUICK ACTION</div><h2>Move faster</h2><button class="btn" onclick="openM()">Add a record</button><p class="muted">Search and manage records from the Records tab.</p></div></div>
<div class="panel" style="margin-top:12px"><div class="ey">LATEST</div><h2>Recent records</h2><div id="recent"></div></div></section>
<section id="records" style="display:none"><div style="display:flex;justify-content:space-between;gap:10px;align-items:end"><div><div class="ey">DATA HUB</div><h2>All records</h2></div><input id="search" placeholder="Search..." style="background:#080c15;color:#fff;border:1px solid #252c39;border-radius:9px;padding:11px"></div><div class="panel" style="margin-top:12px" id="all"></div></section>
<section id="analytics" style="display:none"><div class="ey">INSIGHTS</div><h2>Analytics</h2><div class="grid"><div class="card"><div class="ey">POSITIVE</div><div class="num" id="ap">0</div></div><div class="card"><div class="ey">ATTENTION</div><div class="num" id="aa">0</div></div><div class="card"><div class="ey">PENDING</div><div class="num" id="aq">0</div></div><div class="card"><div class="ey">TOTAL</div><div class="num" id="at">0</div></div></div><div class="panel" style="margin-top:12px"><h2>Jury explanation</h2><p class="muted">“The frontend captures structured data, JavaScript handles interaction, and SQLite stores the records for analysis.”</p></div></section></main></div>
<div id="m" class="modal hide"><div class="box"><button class="close" onclick="closeM()">×</button><h2>Add a record</h2><form id="f"><input id="name" required placeholder="Name"><input id="cat" required placeholder="Category"><select id="status"><option>Present</option><option>Absent</option><option>Pending</option></select><input id="record_date" type="date"><button class="btn" style="width:100%">Save</button></form></div></div>
<script>
async function get(){return (await fetch('/api/records')).json()} async function refresh(){let x=await get(); let t=x.length,p=x.filter(v=>v.status==='Present').length,a=x.filter(v=>v.status==='Absent').length,q=x.filter(v=>v.status==='Pending').length;document.getElementById('t').textContent=t;document.getElementById('p').textContent=p;document.getElementById('a').textContent=a;document.getElementById('r').textContent=(t?Math.round(p/t*100):0)+'%';document.getElementById('ap').textContent=p;document.getElementById('aa').textContent=a;document.getElementById('aq').textContent=q;document.getElementById('at').textContent=t;document.getElementById('all').innerHTML=table(x);document.getElementById('recent').innerHTML=table(x.slice(0,5));document.getElementById('bars').innerHTML=x.slice(0,7).map((v,i)=>'<div class="bar" style="height:'+(55+i*18)+'px"></div>').join('')}
function table(x){return x.length?'<table><tr><th>NAME</th><th>CATEGORY</th><th>STATUS</th><th>DATE</th><th></th></tr>'+x.map(v=>'<tr><td><b>'+v.name+'</b></td><td>'+v.category+'</td><td><span class="tag '+(v.status==='Present'?'p':v.status==='Absent'?'a':'q')+'">'+v.status+'</span></td><td>'+v.record_date+'</td><td><button onclick="del('+v.id+')">Delete</button></td></tr>').join('')+'</table>':'<p class="muted">No records.</p>'}
async function del(id){await fetch('/api/records/'+id,{method:'DELETE'});refresh()}function openM(){m.classList.remove('hide')}function closeM(){m.classList.add('hide')}function show(id,b){['dash','records','analytics'].forEach(x=>document.getElementById(x).style.display=x===id?'block':'none');document.querySelectorAll('nav button').forEach(x=>x.classList.remove('active'));if(b)b.classList.add('active')}
f.onsubmit=async e=>{e.preventDefault();await fetch('/api/records',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:name.value,category:cat.value,status:status.value,record_date:record_date.value})});closeM();e.target.reset();refresh()}search.oninput=async e=>{let x=await (await fetch('/api/records?search='+encodeURIComponent(e.target.value))).json();all.innerHTML=table(x)};refresh()
</script></body></html>"""

def init():
    c=sqlite3.connect(DB); c.execute('CREATE TABLE IF NOT EXISTS records(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,category TEXT NOT NULL,status TEXT NOT NULL,record_date TEXT NOT NULL)'); n=c.execute('SELECT COUNT(*) FROM records').fetchone()[0]
    if n==0:
        c.executemany('INSERT INTO records(name,category,status,record_date) VALUES(?,?,?,?)',[
            ('Rahul','Mathematics','Present','2026-09-29'),('Priya','English','Present','2026-09-29'),('Arjun','Hindi','Absent','2026-09-29'),('Ananya','Mathematics','Present','2026-09-28')])
    c.commit();c.close()

@app.route('/')
def home(): return HTML

@app.get('/api/records')
def records():
    s=request.args.get('search','').strip()
    c=sqlite3.connect(DB);c.row_factory=sqlite3.Row
    if s: rows=c.execute("SELECT * FROM records WHERE name LIKE ? OR category LIKE ? OR status LIKE ? ORDER BY id DESC",(f'%{s}%',f'%{s}%',f'%{s}%')).fetchall()
    else: rows=c.execute('SELECT * FROM records ORDER BY id DESC').fetchall()
    c.close();return jsonify([dict(r) for r in rows])

@app.post('/api/records')
def add():
    d=request.get_json() or {}
    if not d.get('name') or not d.get('category') or not d.get('status'): return jsonify(error='Missing fields'),400
    c=sqlite3.connect(DB);c.execute('INSERT INTO records(name,category,status,record_date) VALUES(?,?,?,?)',(d['name'],d['category'],d['status'],d.get('record_date') or date.today().isoformat()));c.commit();c.close();return jsonify(ok=True),201

@app.delete('/api/records/<int:i>')
def delete(i):
    c=sqlite3.connect(DB);c.execute('DELETE FROM records WHERE id=?',(i,));c.commit();c.close();return jsonify(ok=True)

if __name__=='__main__':
    init();app.run(debug=True)
