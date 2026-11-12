
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const src=fs.readFileSync(process.argv[2],'utf8');
const code=src.slice(src.indexOf('function loadFromPractice(data){'),src.indexOf("window.addEventListener('message',e=>{",src.indexOf('function loadFromPractice(data){')));
const ctx={points:{},lines:[],circles:[],functionsData:[],ellipses:[],vectors:[],showOxyAxis:false,
draw(){},updateStats(){},switchMode(){},document:{getElementById(){return {set textContent(v){ctx.message=v}}}}};
vm.createContext(ctx);vm.runInContext(code,ctx);
function check(d){ctx.message='';ctx.loadFromPractice(d);return {points:ctx.points,lines:ctx.lines,circles:ctx.circles,message:ctx.message};}
let a=check({type:'geometry',points:{A:[0,0],B:[3,0],C:[0,4]},segments:[['A','B'],['B','C'],['C','A']]});
assert.equal(a.lines.length,3);assert.equal(a.message,'');
let b=check({type:'geometry',points:{},circles:[{center:[2,3],radius:5}]});
assert.equal(b.circles.length,1);assert.equal(b.message,'');
let c=check({type:'graph',curves:[{points:[[1000,1000],[1001,1002],[1002,1004]]}]});
assert.equal(c.lines.length,2);assert.equal(c.message,'');
let d=check({type:'triangle'});
assert.match(d.message,/chưa có đủ dữ liệu/);assert.equal(Object.keys(d.points).length,0);
let e=check({type:'geometry',points:{A:[0,0],B:[1,0]},polylines:[['A','B']]});
assert.equal(e.lines.length,1);
let bad=check({type:'geometry',points:{A:[0,0]},segments:[['A','MISSING']]});
assert.match(bad.message,/tham chiếu/);assert.equal(Object.keys(bad.points).length,0);
let badCircle=check({type:'geometry',points:{},circles:[{center:[0,0],radius:-2}]});
assert.match(badCircle.message,/bán kính/);assert.equal(Object.keys(badCircle.points).length,0);
console.log('PASS: triangle segments, circle-only, graph, unsupported reset, named polylines');
