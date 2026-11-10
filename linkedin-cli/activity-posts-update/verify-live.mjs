// @ts-check
/** Bounded read-only checks against the API and independently rendered post pages. */
import assert from 'node:assert/strict';
import {Client, evaluate, run, render} from '../linkedin';
import {mkdtemp, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';

const client = new Client({log: message => console.error(message)});
const folder = await mkdtemp(join(tmpdir(),'linkedin-activity-check-'));
const checks = {posts:[], activities:[], repost:null};
const normalize = value => value.replace(/\s+/g,' ').trim();
await client.open();
try {
  for (const id of ['7525629644318879744','7525540464230461440','7525680542780944385','7525498889613877249']) {
    console.error('Checking post '+id);
    const post = await client.post(id);
    const page = await client.background(post.url);
    await client.wait(page,`document.querySelector('[data-testid="expandable-text-box"]')`,'Post text did not render');
    const body = await evaluate(page,`(()=>{const copy=document.querySelector('[data-testid="expandable-text-box"]').cloneNode(true);copy.querySelectorAll('button').forEach(b=>b.remove());copy.querySelectorAll('br').forEach(b=>b.replaceWith('\\n'));return copy.textContent.trim()})()`);
    assert.equal(normalize(post.text),normalize(body));
    assert.equal(post.textTruncated,false);
    assert.doesNotMatch(render({ok:true,data:post},'md',undefined,{operation:'post'}),/text is incomplete/);
    checks.posts.push({id,apiCharacters:post.text.length,domCharacters:body.length,textMatches:true,warning:false});
  }
  const repost = await client.post('7521206725807419393');
  assert.ok(repost.text.length>600);assert.ok(repost.resharedPost.text.length>200);
  const original = await client.post(repost.resharedPost.id);
  assert.equal(repost.resharedPost.text,original.text);
  checks.repost={id:repost.id,originalId:original.id,commentCharacters:repost.text.length,originalCharacters:original.text.length,independentOriginalMatches:true};

  for (const args of [['activity','sanand0'],['activity','sanand0','ramar'],['activity','openai'],['activity','https://www.linkedin.com/company/openai/home'],['activity','urn:li:company:11130470'],['activity','Rama Ramakrishnan']]) {
    console.error('Checking '+args.join(' '));
    const argv=[...args,'--refresh','--limit','5','--db',join(folder,'cache.sqlite')];
    const live=await run(argv,{log:message=>console.error(message)});
    assert.ok(live.result.data.length);
    const dates=live.result.data.map(post=>Date.parse(post.publishedAt));
    assert.ok(dates.every((date,i)=>!i||dates[i-1]>=date));
    const offline=await run([...argv.filter(arg=>arg!=='--refresh'),'--offline'],{clientFactory(){throw Error('Offline must not open a browser');}});
    assert.deepEqual(offline.result.data.map(post=>post.id),live.result.data.map(post=>post.id));
    checks.activities.push({targets:args.slice(1),posts:dates.length,authors:[...new Set(live.result.data.map(post=>post.author?.name))],latestFirst:true,offlineMatches:true});
  }
} finally {await client.close();await rm(folder,{recursive:true,force:true});}
for(let i=0;i<2;i++) {
  const source=new Client();
  try {await source.open();assert.ok((await source.whoami()).id);}
  finally {const ids=source.owned.map(item=>item.id);await source.close();assert.ok(!(await source.json('/json/list')).some(tab=>ids.includes(tab.id)));}
}
checks.sequentialCleanup=true;
process.stdout.write(JSON.stringify(checks,null,2)+'\n');
