const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");
const script = fs.readFileSync(path.join(__dirname, "../static/js/projects.js"), "utf8");

// Minimal DOM double: assigning innerHTML fails immediately.
class Node {
  constructor(tag = "div") {
    this.tag = tag; this.children = []; this.events = {}; this.attributes = {};
    this.hidden = false; this.value = ""; this.dataset = {};
    this.classList = { add() {}, toggle() {} };
  }
  set textContent(value) { this.text = String(value); }
  get textContent() { return this.text || ""; }
  set innerHTML(_) { throw Error("Unsafe HTML rendering"); }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  setAttribute(name, value) { this.attributes[name] = value; }
  addEventListener(name, callback) { this.events[name] = callback; }
  focus() {}
}
function setup(owner = false) {
  const ids = ["projects-app", "projects-grid", "project-title-search", "projects-empty",
    "projects-loading", "projects-error", "project-search-form", "clear-search", "retry-projects"];
  const nodes = Object.fromEntries(ids.map(id => [id, new Node()]));
  const base = "/projects/00000000-0000-0000-0000-000000000000/";
  nodes["projects-app"].dataset = {listUrl:"/api/projects/", isOwner:String(owner),
    detailUrl:base, starUrl:base+"star/", deleteUrl:base+"delete/"};
  const requests = [], timers = new Map();
  let timerId = 0;
  vm.runInNewContext(script, {
    document: {getElementById:id=>nodes[id] || null,
      querySelector:()=>({value:"test-csrf"}), createElement:tag=>new Node(tag)},
    window: {location:{href:"http://localhost/projects/"}, history:{replaceState(){}}, confirm:()=>false},
    URL, AbortController,
    setTimeout:(fn,delay)=>{timers.set(++timerId,{fn,delay}); return timerId;},
    clearTimeout:id=>timers.delete(id),
    fetch:(url,options)=>new Promise((resolve,reject)=>requests.push({url,options,resolve,reject})),
  });
  return {nodes,requests,timers};
}
const project = (title="Django") => ({
  pk:"12345678-1234-1234-1234-123456789abc",
  fields:{title,description:"Description",technology:"JS",star_count:2,is_starred:true,
    starred_by_names:'user" onmouseover="alert(1)',
    repository_url:"javascript:alert(1)",project_image_url:"data:text/html,x"},
});
const flush = () => new Promise(resolve=>setImmediate(resolve));
async function respond(request,data,ok=true) {
  request.resolve({ok,status:ok?200:500,json:async()=>data}); await flush();
}
const descendants = node => [node,...node.children.flatMap(descendants)];

test("safe text and URLs; dynamic star/delete forms retain CSRF and cancel confirmation",async()=>{
  const {nodes,requests}=setup(true);
  assert.equal(nodes["projects-loading"].hidden,false);
  const title='<img src=x onerror="alert(1)">';
  await respond(requests[0],[project(title)]);
  assert.equal(nodes["projects-grid"].hidden,false);
  const rendered=descendants(nodes["projects-grid"]);
  assert.ok(rendered.some(n=>n.tag==="a" && n.textContent===title));
  assert.ok(!rendered.some(n=>n.tag==="img" || n.href?.startsWith("javascript:")));
  const forms=rendered.filter(n=>n.tag==="form");
  assert.equal(forms.length,2);
  assert.ok(forms.every(n=>n.children[0].value==="test-csrf"));
  assert.equal(rendered.find(n=>n.attributes["aria-pressed"]).attributes["aria-pressed"],"true");
  let prevented=false;
  forms[1].events.submit({preventDefault(){prevented=true;}});
  assert.equal(prevented,true);
});
test("public visitors get star but no delete controls",async()=>{
  const {nodes,requests}=setup();
  await respond(requests[0],[project()]);
  assert.equal(descendants(nodes["projects-grid"]).filter(n=>n.tag==="form").length,1);
});
test("300ms debounce cancels requests and ignores stale responses",async()=>{
  const {nodes,requests,timers}=setup();
  const search=nodes["project-title-search"];
  search.value="D"; search.events.input();
  search.value="Django & JS"; search.events.input();
  assert.equal(timers.size,1); assert.equal(requests.length,1);
  assert.equal(requests[0].options.signal.aborted,true);
  const timer=[...timers.values()][0];
  assert.equal(timer.delay,300); timer.fn();
  assert.equal(requests[1].url.searchParams.get("title"),"Django & JS");
  await respond(requests[1],[project("Newest")]);
  await respond(requests[0],[project("Stale")]);
  const texts=descendants(nodes["projects-grid"]).map(n=>n.textContent);
  assert.ok(texts.includes("Newest")); assert.ok(!texts.includes("Stale"));
});
test("submit cancels debounce; empty result clears old cards",async()=>{
  const {nodes,requests,timers}=setup();
  await respond(requests[0],[project()]);
  nodes["project-title-search"].value="missing";
  nodes["project-title-search"].events.input();
  let prevented=false;
  nodes["project-search-form"].events.submit({preventDefault(){prevented=true;}});
  assert.equal(prevented,true); assert.equal(timers.size,0);
  await respond(requests[1],[]);
  assert.equal(nodes["projects-grid"].children.length,0);
  assert.equal(nodes["projects-empty"].hidden,false);
  assert.match(nodes["projects-empty"].textContent,/missing/);
});
test("HTTP and network failures show retry and recover",async()=>{
  const {nodes,requests}=setup();
  await respond(requests[0],{},false);
  assert.equal(nodes["projects-error"].hidden,false);
  nodes["retry-projects"].events.click();
  requests[1].reject(Error("Offline")); await flush();
  assert.equal(nodes["projects-error"].hidden,false);
  nodes["retry-projects"].events.click();
  await respond(requests[2],[project()]);
  assert.equal(nodes["projects-grid"].hidden,false);
  assert.equal(nodes["projects-error"].hidden,true);
});
