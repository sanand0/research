// @ts-check
/** Compare showcase actor identity and post results with the rendered LinkedIn page. */
import assert from 'node:assert/strict';
import {mkdtemp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {Client,evaluate,run,render} from '../linkedin';
const directory=await mkdtemp(join(tmpdir(),'linkedin-showcase-'));
const client=new Client({log:message=>console.error(message)});
const checks={timeZone:Intl.DateTimeFormat().resolvedOptions().timeZone,variants:[]};
try{
 await client.open();
 const member=await client.profile('claude'),organization=await client.company('claude');
 assert.equal(organization.url,'https://www.linkedin.com/showcase/claude/');
 checks.identities={member:{name:member.name,url:member.url},organization:{name:organization.name,id:organization.id,url:organization.url}};
 const page=await client.background(organization.url);
 await client.wait(page,`document.querySelector('main a[href*="urn:li:activity:"]')`,'Showcase posts did not render');
 const ui=await evaluate(page,`({title:document.title,ids:[...new Set([...document.querySelectorAll('main a[href*="urn:li:activity:"]')].map(a=>a.href.match(/urn:li:activity:\\d+/)?.[0]).filter(Boolean))]})`);
 assert.match(ui.title,/Claude/);
 const db=join(directory,'cache.sqlite');
 for(const target of ['showcase:claude',organization.url]){
  const args=['activity',target,'--limit','3','--db',db];
  const online=await run([...args,'--refresh'],{log:message=>console.error(message)});
  assert.ok(online.result.data.length);
  assert.ok(online.result.data.every(post=>post.author.name==='Claude'));
  assert.equal(online.result.meta.resolved_actors[0].id,organization.id);
  const matches=online.result.data.filter(post=>ui.ids.includes(post.id));assert.ok(matches.length);
  const offline=await run([...args,'--offline'],{clientFactory(){throw Error('Must stay offline');}});
  assert.deepEqual(offline.result.data.map(post=>post.id),online.result.data.map(post=>post.id));
  const post=online.result.data[0];const markdown=render({ok:true,data:post},'md',undefined,{operation:'post'});
  assert.doesNotMatch(markdown.split('\n')[1],/from activity ID|UTC/);
  checks.variants.push({target,postIds:online.result.data.map(post=>post.id),uiMatches:matches.map(post=>post.id),offlineMatches:true,header:markdown.split('\n').slice(0,3)});
 }
 checks.ui={title:ui.title,postIds:ui.ids};
 process.stdout.write(JSON.stringify(checks,null,2)+'\n');
}finally{await client.close();await rm(directory,{recursive:true,force:true});}
