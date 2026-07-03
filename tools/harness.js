const fs = require('fs');
const content = fs.readFileSync(require('path').join(__dirname,'..','src','content.txt'),'utf8');
let engine = fs.readFileSync(require('path').join(__dirname,'..','src','part3_engine.html'),'utf8');
engine = engine.match(/^<script>\n([\s\S]*?)\n<\/script>/m)[1];
engine = engine.replace(/\}\)\(\);\s*$/,
  'window.__T={LESSONS:LESSONS,MODULES:MODULES,lessonHTML:lessonHTML,homeHTML:homeHTML,playHTML:playHTML,genSeed:genSeed};})();');

// ---- DOM stubs ----
const cache = {};
function mkEl(id){
  return { _h:'', id, addEventListener(){}, classList:{add(){},remove(){},toggle(){}},
    style:{}, focus(){}, close(){}, showModal(){}, select(){}, setSelectionRange(){},
    set innerHTML(v){this._h=v}, get innerHTML(){return this._h},
    textContent: id==='course' ? content : '', hidden:false, disabled:false, value:'',
    setAttribute(){}, getAttribute(){return null}, open:false };
}
global.document = {
  getElementById(id){ return cache[id] || (cache[id]=mkEl(id)); },
  querySelector(){ return null }, querySelectorAll(){ return [] },
  createElement(){ return mkEl('x') },
  head:{appendChild(){}}, body:{appendChild(){},removeChild(){}},
  addEventListener(){}, execCommand(){ return true }
};
global.window = { addEventListener(){}, innerWidth:1200, scrollTo(){} };
global.location = { hash:'' };
global.navigator = { platform:'X11 Linux', userAgent:'node' };

eval(engine);
const T = global.window.__T;

// ---- render tests ----
console.log('LESSONS parsed:', T.LESSONS.length, '| MODULES:', T.MODULES.length);
let renderErrs = 0, quizzes = 0, runBtns = 0;
for(let n=1;n<=T.LESSONS.length;n++){
  const h = T.lessonHTML(n);
  if(!h || h.length < 500){ console.log('L'+n+' suspiciously short:', h.length); renderErrs++; }
  if(/>undefined</.test(h) || /\bNaN\b/.test(h)){ console.log('L'+n+' contains undefined/NaN'); renderErrs++; }
  quizzes += (h.match(/class="quiz"/g)||[]).length;
  runBtns += (h.match(/data-run=/g)||[]).length;
}
console.log('total quizzes rendered:', quizzes, '| Run buttons:', runBtns);
console.log('home OK:', T.homeHTML().includes('modcard'), '| play OK:', T.playHTML().includes('pgSql'));
console.log('render errors:', renderErrs);

// ---- seed database tests ----
const initSqlJs = require('sql.js');
initSqlJs().then(SQL => {
  const db = new SQL.Database();
  const t0 = Date.now();
  db.run(T.genSeed());
  console.log('\nseed built in', Date.now()-t0, 'ms');
  const one = s => db.exec(s)[0].values[0];
  console.log('rows:', ['patients','admissions','vaccinations','lab_results','deaths','lsoa_imd','gp_practices','icd10_lookup','la_population']
    .map(t=>t+'='+one('SELECT COUNT(*) FROM '+t)[0]).join(' '));
  // capstone A
  console.log('A: FY25/26 completed emergency discharges =', one(`SELECT COUNT(*) FROM admissions WHERE admission_method='Emergency' AND discharge_date>='2025-04-01' AND discharge_date<'2026-04-01'`)[0]);
  console.log('A: readmitted within 30d =', one(`WITH c AS (SELECT admission_id,patient_id,discharge_date FROM admissions WHERE admission_method='Emergency' AND discharge_date>='2025-04-01' AND discharge_date<'2026-04-01') SELECT SUM(EXISTS(SELECT 1 FROM admissions r WHERE r.patient_id=c.patient_id AND r.admission_method='Emergency' AND r.admission_date>c.discharge_date AND julianday(r.admission_date)-julianday(c.discharge_date)<=30)) FROM c`)[0]);
  console.log('A: deaths within 30d of a discharge =', one(`SELECT COUNT(*) FROM deaths d JOIN admissions a ON a.patient_id=d.patient_id AND a.discharge_date IS NOT NULL WHERE julianday(d.date_of_death)-julianday(a.discharge_date) BETWEEN 0 AND 30`)[0]);
  // capstone B
  const coh = db.exec(`SELECT COALESCE(v.d,0) AS doses, COUNT(*) FROM patients p LEFT JOIN (SELECT vx.patient_id, COUNT(*) d FROM vaccinations vx JOIN patients p2 ON p2.patient_id=vx.patient_id WHERE vx.vaccine='MMR' AND vx.date_given < date(p2.birth_date,'+2 years') GROUP BY vx.patient_id) v ON v.patient_id=p.patient_id WHERE p.birth_date>='2023-04-01' AND p.birth_date<'2024-04-01' GROUP BY doses ORDER BY doses`);
  console.log('B: cohort dose distribution (doses,count):', JSON.stringify(coh[0].values));
  const grad = db.exec(`SELECT CASE WHEN li.imd_decile<=3 THEN 'deprived1-3' WHEN li.imd_decile>=8 THEN 'affluent8-10' ELSE 'mid' END g, ROUND(AVG(CASE WHEN COALESCE(v.d,0)>=2 THEN 1.0 ELSE 0 END),3) uptake2, COUNT(*) n FROM patients p JOIN lsoa_imd li ON li.lsoa_code=p.lsoa_code LEFT JOIN (SELECT vx.patient_id, COUNT(*) d FROM vaccinations vx JOIN patients p2 ON p2.patient_id=vx.patient_id WHERE vx.vaccine='MMR' AND vx.date_given<date(p2.birth_date,'+2 years') GROUP BY vx.patient_id) v ON v.patient_id=p.patient_id WHERE p.birth_date>='2023-04-01' AND p.birth_date<'2024-04-01' GROUP BY g`);
  console.log('B: uptake gradient:', JSON.stringify(grad[0].values));
  // misc lesson hooks
  console.log('freq attenders (>=3 emerg):', one(`SELECT COUNT(*) FROM (SELECT patient_id FROM admissions WHERE admission_method='Emergency' GROUP BY patient_id HAVING COUNT(*)>=3)`)[0]);
  console.log('HbA1c>=48:', one(`SELECT COUNT(*) FROM lab_results WHERE test='HbA1c' AND value>=48`)[0],
              '| SBP>=140:', one(`SELECT COUNT(*) FROM lab_results WHERE test='Systolic BP' AND value>=140`)[0]);
  console.log('NULL discharges:', one(`SELECT COUNT(*) FROM admissions WHERE discharge_date IS NULL`)[0]);
  console.log('LSOAs with >=15 patients:', one(`SELECT COUNT(*) FROM (SELECT lsoa_code FROM patients GROUP BY lsoa_code HAVING COUNT(*)>=15)`)[0]);
  console.log('la_population rows:', one(`SELECT COUNT(*) FROM la_population`)[0]);
  console.log('J-code respiratory admissions:', one(`SELECT COUNT(*) FROM admissions WHERE primary_diagnosis LIKE 'J%'`)[0]);
  console.log('\nINTEGRATION TEST COMPLETE');
}).catch(e=>{ console.log('SQL TEST FAILED:', e.message); process.exit(1); });
