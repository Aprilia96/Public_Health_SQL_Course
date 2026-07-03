const fs = require('fs');
const full = fs.readFileSync(require('path').join(__dirname,'..','course.html'),'utf8');
let errs = [], warns = [];

// isolate course text region
const m = full.match(/<script type="text\/plain" id="course">\n([\s\S]*?)<\/script>/);
if(!m){ console.log('FATAL: course block not found'); process.exit(1); }
let raw = m[1];
if(raw.includes('</script')) errs.push('content contains </script');
if(raw.includes('<!--')) warns.push('content contains <!-- (script escape state risk)');
raw = raw.replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&amp;/g,'&');

const KNOWN = new Set(['p','h','code','oscode','quiz','ex','key','note','table']);
const lines = raw.split(/\r?\n/);
let i=0, modules=[], lessons=[], cur=null, block=null;
function endBlock(){ if(block&&cur) cur.blocks.push(block); block=null; }
while(i<lines.length && lines[i].trim()!=='#MODULES') i++;
i++;
while(i<lines.length && !/^#LESSON /.test(lines[i])){
  const mm=lines[i].match(/^(\d+)\|(.+)$/); if(mm) modules.push({n:+mm[1],title:mm[2]}); i++;
}
for(;i<lines.length;i++){
  const L=lines[i];
  const lm=L.match(/^#LESSON (\d+)\|(.+)$/);
  if(lm){ endBlock(); cur={n:lessons.length+1,mod:+lm[1],title:lm[2],blocks:[]}; lessons.push(cur); continue; }
  if(/^::/.test(L)){ endBlock(); const p=L.slice(2).split('|'); block={type:p[0].trim(),args:p.slice(1),lines:[]};
    if(!KNOWN.has(block.type)) errs.push(`L${cur?cur.n:'?'} unknown block ::${block.type}`);
    continue; }
  if(block) block.lines.push(L);
  else if(L.trim() && cur) errs.push(`L${cur.n} stray text outside block: "${L.slice(0,40)}"`);
}
endBlock();

console.log(`modules: ${modules.length}, lessons: ${lessons.length}`);
if(modules.length!==10) errs.push('expected 10 modules');
if(lessons.length<100) errs.push('fewer than 100 lessons');

const perMod={};
lessons.forEach(l=>{ perMod[l.mod]=(perMod[l.mod]||0)+1;
  let quizzes=0, hasEx=false, hasKey=false;
  l.blocks.forEach(b=>{
    if(b.type==='quiz'){
      quizzes++;
      const stars=b.lines.filter(x=>/^\* /.test(x)).length;
      const opts=b.lines.filter(x=>/^[-*] /.test(x)).length;
      const why=b.lines.some(x=>/^! /.test(x));
      const hasQ=b.lines.some(x=>/^Q /.test(x));
      if(stars!==1) errs.push(`L${l.n} quiz with ${stars} correct options`);
      if(opts<3) warns.push(`L${l.n} quiz with only ${opts} options`);
      if(!why) errs.push(`L${l.n} quiz missing ! explanation`);
      if(!hasQ) errs.push(`L${l.n} quiz missing Q line`);
    }
    if(b.type==='ex'){ hasEx=true;
      if(!b.lines.some(x=>/^~~~\w*\s*$/.test(x))) errs.push(`L${l.n} exercise missing ~~~ fence`); }
    if(b.type==='key'){ hasKey=true;
      if(!b.lines.some(x=>/^- /.test(x))) errs.push(`L${l.n} key with no bullets`); }
    if(b.type==='oscode'){
      ['@win','@mac','@linux'].forEach(k=>{ if(!b.lines.some(x=>x.trim()===k)) errs.push(`L${l.n} oscode missing ${k}`); });
    }
    if(b.type==='code' && b.lines.join('').trim()==='') errs.push(`L${l.n} empty code block`);
    if(b.type==='table'){
      const rows=b.lines.filter(x=>x.trim()).map(x=>x.split('|').length);
      if(rows.length && new Set(rows).size>1) warns.push(`L${l.n} table ragged cols ${JSON.stringify(rows)}`);
    }
    if(b.type==='note' && !b.args[0]) errs.push(`L${l.n} note missing type`);
    if(b.type==='note' && b.args[0] && !['info','warn','ai','study'].includes(b.args[0])) errs.push(`L${l.n} note bad type ${b.args[0]}`);
  });
  if(quizzes<2) errs.push(`L${l.n} has ${quizzes} quizzes (<2): ${l.title}`);
  if(!hasEx) errs.push(`L${l.n} missing exercise: ${l.title}`);
  if(!hasKey) errs.push(`L${l.n} missing key points: ${l.title}`);
});
console.log('lessons per module:', JSON.stringify(perMod));

// count sqltry blocks
let sqltry=0; lessons.forEach(l=>l.blocks.forEach(b=>{ if(b.type==='code'&&(b.args[0]||'').trim()==='sqltry') sqltry++; }));
console.log('sqltry blocks:', sqltry);

console.log('\n--- WARNINGS ---'); warns.slice(0,40).forEach(w=>console.log('warn:',w));
console.log('\n--- ERRORS ---'); errs.forEach(e=>console.log('ERR:',e));
console.log(errs.length? `\n${errs.length} error(s)` : '\nALL CHECKS PASSED');
