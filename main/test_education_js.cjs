const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");
const script = fs.readFileSync(path.join(__dirname, "../static/js/education.js"), "utf8");

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
function setup(owner = false, editor = false, authenticated = owner || editor) {
  const ids = ["education-app", "education-grid", "institution-search", "education-empty",
    "education-loading", "education-error", "education-search-form", "clear-education-search", "retry-education", "education-results", "education-json-link"];
  const nodes = Object.fromEntries(ids.map(id => [id, new Node()]));
  const base = "/education/00000000-0000-0000-0000-000000000000/";
  nodes["education-app"].dataset = {listUrl:"/api/education/", canEdit:String(owner || editor), canDelete:String(owner), authenticated:String(authenticated), createUrl:"/education/add-ajax/", editUrl:base+"edit/",
    detailUrl:base, starUrl:base+"star/", deleteUrl:base+"delete/"};
  const requests = [], timers = new Map(), toasts = [];
  const submit = new Node("button");
  const field = new Node("input");
  if (owner) {
    const form = nodes["education-form"] = new Node("form");
    form.querySelector = selector => selector === '[type="submit"]' ? submit : field;
    form.reset = () => { form.resets = (form.resets || 0) + 1; };
    const modal = nodes["add-education-modal"] = new Node();
    modal.showPopover = () => {};
    modal.hidePopover = () => { modal.closed = true; };
    nodes["education-form-error"] = new Node();
  }
  let timerId = 0;
  vm.runInNewContext(script, {
    document: {getElementById:id=>nodes[id] || null,
      querySelector:()=>({value:"test-csrf"}), createElement:tag=>new Node(tag)},
    window: {location:{href:"http://localhost/education/"}, history:{replaceState(){}}, confirm:()=>false},
    URL, AbortController,
    FormData: class { constructor(form) { this.form = form; } },
    showToast: (...args) => toasts.push(args),
    setTimeout:(fn,delay)=>{timers.set(++timerId,{fn,delay}); return timerId;},
    clearTimeout:id=>timers.delete(id),
    fetch:(url,options)=>new Promise((resolve,reject)=>requests.push({url,options,resolve,reject})),
  });
  return {nodes,requests,timers,submit,toasts};
}
const project = (title="Django") => ({
  pk:"12345678-1234-1234-1234-123456789abc",
  fields:{institution:title,description:"Description",field_of_study:"CS",degree_display:"Bachelor",star_count:2,is_starred:true,
    starred_by_names:'user" onmouseover="alert(1)',
    website:"javascript:alert(1)"},
});
const flush = () => new Promise(resolve=>setImmediate(resolve));
async function respond(request,data,ok=true) {
  request.resolve({ok,status:ok?200:500,json:async()=>data}); await flush();
}
const descendants = node => [node,...node.children.flatMap(descendants)];

test("safe text and URLs; dynamic star/delete forms retain CSRF and cancel confirmation",async()=>{
  const {nodes,requests}=setup(true);
  assert.equal(nodes["education-loading"].hidden,false);
  const title='<img src=x onerror="alert(1)">';
  await respond(requests[0],[project(title)]);
  assert.equal(nodes["education-grid"].hidden,false);
  const rendered=descendants(nodes["education-grid"]);
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
  assert.equal(descendants(nodes["education-grid"]).filter(n=>n.tag==="form").length,1);
});
test("300ms debounce cancels requests and ignores stale responses",async()=>{
  const {nodes,requests,timers}=setup();
  const search=nodes["institution-search"];
  search.value="D"; search.events.input();
  search.value="Django & JS"; search.events.input();
  assert.equal(timers.size,1); assert.equal(requests.length,1);
  assert.equal(requests[0].options.signal.aborted,true);
  const timer=[...timers.values()][0];
  assert.equal(timer.delay,300); timer.fn();
  assert.equal(requests[1].url.searchParams.get("institution"),"Django & JS");
  await respond(requests[1],[project("Newest")]);
  await respond(requests[0],[project("Stale")]);
  const texts=descendants(nodes["education-grid"]).map(n=>n.textContent);
  assert.ok(texts.includes("Newest")); assert.ok(!texts.includes("Stale"));
});
test("submit cancels debounce; empty result clears old cards",async()=>{
  const {nodes,requests,timers}=setup();
  await respond(requests[0],[project()]);
  nodes["institution-search"].value="missing";
  nodes["institution-search"].events.input();
  let prevented=false;
  nodes["education-search-form"].events.submit({preventDefault(){prevented=true;}});
  assert.equal(prevented,true); assert.equal(timers.size,0);
  await respond(requests[1],[]);
  assert.equal(nodes["education-grid"].children.length,0);
  assert.equal(nodes["education-empty"].hidden,false);
  assert.match(nodes["education-empty"].textContent,/missing/);
});
test("HTTP and network failures show retry and recover",async()=>{
  const {nodes,requests}=setup();
  await respond(requests[0],{},false);
  assert.equal(nodes["education-error"].hidden,false);
  nodes["retry-education"].events.click();
  requests[1].reject(Error("Offline")); await flush();
  assert.equal(nodes["education-error"].hidden,false);
  nodes["retry-education"].events.click();
  await respond(requests[2],[project()]);
  assert.equal(nodes["education-grid"].hidden,false);
  assert.equal(nodes["education-error"].hidden,true);
});

test("Editor sees edit, member does not; neither sees create/delete", async()=>{
  for (const editor of [true,false]) {
    const {nodes,requests}=setup(false,editor,true);
    await respond(requests[0],[project()]);
    const rendered=descendants(nodes["education-grid"]);
    assert.equal(rendered.some(n=>n.textContent==="Edit education"),editor);
    assert.equal(rendered.some(n=>n.textContent==="Delete education"),false);
    assert.equal(nodes["education-form"],undefined);
  }
});
test("creation sends CSRF, prevents double submit, resets and refreshes active search",async()=>{
  const {nodes,requests,submit,toasts}=setup(true);
  await respond(requests[0],[]);
  nodes["institution-search"].value="Example";
  const form=nodes["education-form"];
  const pending=form.events.submit({preventDefault(){}});
  assert.equal(submit.disabled,true);
  await form.events.submit({preventDefault(){}});
  assert.equal(requests.length,2);
  const post=requests[1];
  assert.equal(post.options.method,"POST");
  assert.equal(post.options.headers["X-CSRFToken"],"test-csrf");
  assert.equal(post.options.body.form,form);
  post.resolve({ok:true,status:201,json:async()=>({pk:project().pk})});
  await pending;
  assert.equal(form.resets,1);
  assert.equal(nodes["add-education-modal"].closed,true);
  assert.equal(submit.disabled,false);
  assert.equal(toasts[0][2],"success");
  assert.equal(requests[2].url.searchParams.get("institution"),"Example");
});
test("validation failure preserves modal and exposes server text safely",async()=>{
  const {nodes,requests,submit,toasts}=setup(true);
  const form=nodes["education-form"];
  const pending=form.events.submit({preventDefault(){}});
  const message='<img src=x onerror="alert(1)">';
  requests[1].resolve({ok:false,status:400,json:async()=>({errors:{institution:[{message}]}})});
  await pending;
  assert.equal(nodes["education-form-error"].textContent,message);
  assert.equal(form.resets,undefined);
  assert.equal(nodes["add-education-modal"].closed,undefined);
  assert.equal(submit.disabled,false);
  assert.equal(toasts[0][2],"error");
});
test("HTML 403, login redirect, malformed success and network failure are not successes",async()=>{
  for (const mode of ["csrf","redirect","malformed","offline"]) {
    const {nodes,requests,submit,toasts}=setup(true);
    const form=nodes["education-form"];
    const pending=form.events.submit({preventDefault(){}});
    if (mode==="offline") requests[1].reject(Error("Offline"));
    else requests[1].resolve({
      ok:mode!=="csrf",status:mode==="csrf"?403:200,redirected:mode==="redirect",
      json:async()=>{throw Error("Not JSON");},
    });
    await pending;
    assert.equal(nodes["education-form-error"].hidden,false);
    assert.equal(form.resets,undefined);
    assert.equal(submit.disabled,false);
    assert.equal(toasts[0][2],"error");
    assert.equal(requests.length,2);
  }
});
test("malformed UUID cannot inject a URL or partly render a list",async()=>{
  const {nodes,requests}=setup();
  await respond(requests[0],[{...project(),pk:'../login/?bad="'}]);
  assert.equal(nodes["education-error"].hidden,false);
  assert.equal(nodes["education-grid"].children.length,0);
});
