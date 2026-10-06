const fs=require('fs'), vm=require('vm');
const ctx = vm.createContext({console, globalThis:null});
ctx.globalThis = ctx; ctx.self = ctx; ctx.window = ctx;
vm.runInContext('var GT_RULES = '+fs.readFileSync('gt-rules.json','utf8')+';', ctx);
for (const f of ['lib-pinyin-pro.js','lib-t2cn.js','engine.js']) {
  let code = fs.readFileSync(f,'utf8');
  if (f==='engine.js') code += '\n;this.Engine = Engine;';
  vm.runInContext(code, ctx, {filename:f});
}
const E = ctx.Engine;
module.exports = E;
if (require.main === module) {
  const words = process.argv.slice(2);
  const input = words.length? words : [];
  const tests = fs.readFileSync('words.txt','utf8').split(/\s+/).filter(Boolean);
  const list = input.length? input : tests;
  for (const w of list) {
    const {lines} = E.analyze(w,'',{});
    const u = lines[0];
    console.log(w.padEnd(8,'　'), u.map(x=>x.kind==='han'?x.py:x.text).join(' '));
  }
}
