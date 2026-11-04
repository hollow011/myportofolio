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
function setup(owner = false, authenticated = owner) {
  const ids = ["projects-app", "projects-grid", "project-title-search", "projects-empty",
    "projects-loading", "projects-error", "project-search-form", "clear-search", "retry-projects"];
  const nodes = Object.fromEntries(ids.map(id => [id, new Node()]));
  const base = "/projects/00000000-0000-0000-0000-000000000000/";
  const api = "/api/v1" + base;
  nodes["projects-app"].dataset = {listUrl:"/api/v1/projects/", isOwner:String(owner),
    authenticated:String(authenticated), loginUrl:"/login/", detailUrl:base, starUrl:api+"star/", deleteUrl:api};
  const form = new Node("form"), submit = new Node("button"), modal = new Node("div");
  if (owner) Object.assign(nodes, {"project-form":form, "add-project-modal":modal, "project-form-error":new Node()});
  modal.showPopover = () => {};
  modal.hidePopover = () => {modal.hidden = true;};
  form.querySelector = () => submit;
  form.reset = () => form.fields.clear();
  form.fields = new Map();
  const notices = [];
  const requests = [], timers = new Map();
  let timerId = 0;
  vm.runInNewContext(script, {
    document: {getElementById:id=>nodes[id] || null,
      querySelector:()=>({value:"test-csrf"}), createElement:tag=>new Node(tag)},
    window: {location:{href:"http://localhost/projects/"}, history:{replaceState(){}}, confirm:()=>nodes.confirmDelete},
    URL, AbortController, FormData:class {constructor(element) {return element.fields;}},
    showToast:(...args)=>notices.push(args),
    setTimeout:(fn,delay)=>{timers.set(++timerId,{fn,delay}); return timerId;},
    clearTimeout:id=>timers.delete(id),
    fetch:(url,options)=>new Promise((resolve,reject)=>requests.push({url,options,resolve,reject})),
  });
  return {nodes,requests,timers,form,modal,submit,notices};
}
const project = (title="Django") => ({
  id:"12345678-1234-1234-1234-123456789abc",
  title,description:"Description",tech_stack:"JS",star_count:2,is_starred:true,
    starred_by_names:'user" onmouseover="alert(1)',
    project_url:"javascript:alert(1)",project_image_url:"data:text/html,x",
});
const flush = () => new Promise(resolve=>setImmediate(resolve));
async function respond(request,data,ok=true) {
  request.resolve({ok,status:ok?200:500,json:async()=>data}); await flush();
}
const descendants = node => [node,...node.children.flatMap(descendants)];

test("safe text and URLs; deletion requires confirmation and accepts an empty 204",async()=>{
  const {nodes,requests}=setup(true);
  assert.equal(nodes["projects-loading"].hidden,false);
  const title='<img src=x onerror="alert(1)">';
  await respond(requests[0],[project(title)]);
  assert.equal(nodes["projects-grid"].hidden,false);
  const rendered=descendants(nodes["projects-grid"]);
  assert.ok(rendered.some(n=>n.tag==="a" && n.textContent===title));
  assert.ok(!rendered.some(n=>n.tag==="img" || n.href?.startsWith("javascript:")));
  assert.equal(rendered.find(n=>n.attributes["aria-pressed"]).attributes["aria-pressed"],"true");
  const remove = rendered.find(n=>n.dataset.action==="delete");
  const click = () => nodes["projects-grid"].events.click({target:{closest:()=>remove}});
  await click();
  assert.equal(requests.length,1);
  nodes.confirmDelete = true;
  const finished = click();
  assert.equal(requests[1].url,"/api/v1/projects/"+project().id+"/");
  assert.equal(requests[1].options.method,"DELETE");
  assert.equal(requests[1].options.headers["X-CSRFToken"],"test-csrf");
  requests[1].resolve({ok:true,status:204});
  await flush();
  await respond(requests[2],[]);
  await finished;
  assert.equal(nodes["projects-empty"].hidden,false);
});
test("guest can log in to star; member can toggle once while preserving the filter",async()=>{
  const {nodes,requests}=setup();
  await respond(requests[0],[project()]);
  const guest = descendants(nodes["projects-grid"]);
  assert.ok(guest.some(n=>n.href==="/login/"));
  assert.ok(!guest.some(n=>n.dataset.action));
  const member = setup(false,true);
  await respond(member.requests[0],[project()]);
  const grid = member.nodes["projects-grid"];
  const buttons = descendants(grid).filter(n=>n.tag==="button");
  assert.equal(buttons.length,1);
  member.nodes["project-title-search"].value = "Django";
  const event = {target:{closest:()=>buttons[0]}};
  const finished = grid.events.click(event);
  await grid.events.click(event);
  assert.equal(member.requests.length,2);
  assert.equal(member.requests[1].options.method,"POST");
  assert.equal(member.requests[1].url,"/api/v1/projects/"+project().id+"/star/");
  await respond(member.requests[1],project());
  assert.equal(member.requests[2].url.searchParams.get("title"),"Django");
  await respond(member.requests[2],[{...project(),is_starred:false}]);
  await finished;
  assert.equal(descendants(grid).find(n=>n.dataset.action==="star").attributes["aria-pressed"],"false");
});

test("create maps form fields to JSON, keeps failed drafts, clears only on success",async()=>{
  const {nodes,requests,form,modal,submit,notices}=setup(true);
  await respond(requests[0],[]);
  form.fields = new Map(Object.entries({title:"   ", description:"Description", technology:"JS",
    repository_url:"https://example.com",project_image_url:"",is_featured:"on",csrfmiddlewaretoken:"private"}));
  form.events.submit({preventDefault(){}});
  const {url,options} = requests[1];
  assert.equal(url,"/api/v1/projects/");
  assert.equal(options.method,"POST");
  assert.equal(options.headers["Content-Type"],"application/json");
  assert.equal(options.headers["X-CSRFToken"],"test-csrf");
  assert.deepEqual(JSON.parse(options.body),{title:"   ",description:"Description",tech_stack:"JS",
    project_url:"https://example.com",project_image_url:"",is_featured:true});
  requests[1].resolve({ok:false,status:400,json:async()=>({title:["Required."]})});
  await flush();
  assert.equal(nodes["project-form-error"].textContent,"Required.");
  assert.equal(form.fields.get("description"),"Description");
  assert.equal(submit.disabled,false);
  form.fields.set("title","Corrected");
  form.events.submit({preventDefault(){}});
  requests[2].resolve({ok:true,status:201,json:async()=>project("Corrected")});
  await flush();
  assert.equal(form.fields.size,0);
  assert.equal(modal.hidden,true);
  assert.equal(notices.at(-1)[2],"success");
  await respond(requests[3],[project("Corrected")]);
  assert.ok(descendants(nodes["projects-grid"]).some(n=>n.textContent==="Corrected"));
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
