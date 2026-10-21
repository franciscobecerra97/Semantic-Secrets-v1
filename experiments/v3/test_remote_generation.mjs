import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir, mkdtemp } from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { validatePlan, requestData, parseEvent, callGradio, pngDimensions, generateBatch, hash } from './generate_remote_dataset.mjs';

const cfg=JSON.parse(await readFile(new URL('./config/remote_generation_v3_4.json',import.meta.url),'utf8'));
const images=[];
for(let f=1;f<=24;f++) for(let i=1;i<=5;i++) images.push({image_id:`cap-v3-B-F${String(f).padStart(2,'0')}-${String(i).padStart(2,'0')}`,family_id:`F${String(f).padStart(2,'0')}`,prompt:'Public test fixture',seed:925031+100*f+i,split:f<=12?'development':'validation'});
const plan={model_id:cfg.requested_model_id,space_id:cfg.space_id,requested_parameters:cfg.requested_parameters,images};

test('reject duplicated IDs, wrong split, altered model or seed before requests',()=>{
  validatePlan(plan,cfg);
  for(const mutate of [p=>p.images[1]=p.images[0],p=>p.images[0].split='validation',p=>p.model_id='stabilityai/sdxl-turbo',p=>p.images[0].seed=0]) {
    const p=structuredClone(plan); mutate(p); assert.throws(()=>validatePlan(p,cfg));
  }
});
test('API positional settings match the user Gradio example, with SD-Turbo selected',()=>{
  assert.deepEqual(requestData(images[0],cfg),['Public test fixture','stabilityai/sd-turbo','',925132,512,512,0,1]);
});
test('SSE handles heartbeat, completion and server errors',()=>{
  assert.equal(parseEvent('event: heartbeat\ndata: null').data,null);
  assert.deepEqual(parseEvent('event: complete\ndata: [{"path":"x"}]').data,[{path:'x'}]);
  assert.throws(()=>parseEvent('event: error\ndata: "quota exceeded"'),/quota exceeded/);
});
test('mock REST call downloads only the returned image from the selected host',async()=>{
  const bytes=Buffer.alloc(24); Buffer.from('89504e470d0a1a0a','hex').copy(bytes);bytes.writeUInt32BE(512,16);bytes.writeUInt32BE(512,20);
  const calls=[];
  const fake=async(u,o)=>{calls.push([u,o]);if(calls.length===1)return Response.json({event_id:'abc'});
    if(calls.length===2)return new Response('event: complete\ndata: [{"url":"'+cfg.host+'/image.png"}]\n\n');
    return new Response(bytes);};
  const result=await callGradio(images[0],cfg,fake);
  assert.equal(calls.length,3); assert.deepEqual(result.bytes,bytes); assert.deepEqual(pngDimensions(bytes),[512,512]);
  assert.deepEqual(JSON.parse(calls[0][1].body).data,requestData(images[0],cfg));
});
test('server errors and missing files are never counted as completed images',async()=>{
  let n=0;
  const fake=async()=>++n===1?Response.json({event_id:'abc'}):new Response('event: complete\ndata: [null]\n\n');
  await assert.rejects(()=>callGradio(images[0],cfg,fake),/Missing image/);
});

test('resume detects raw-image tampering before making any network call',async()=>{
  const dir=await mkdtemp(path.join(os.tmpdir(),'p9-remote-resume-'));
  await mkdir(path.join(dir,'plans'));
  const configBytes=await readFile(new URL('./config/remote_generation_v3_4.json',import.meta.url));
  await writeFile(path.join(dir,'plans/naturalistic_prompt_plan_v3_4.json'),JSON.stringify({...plan,generation_amendment_sha256:hash(configBytes)}));
  const bytes=Buffer.alloc(24,3);
  const fake=async(u,o)=>{
    if(u.includes('/api/spaces/'))return Response.json({sha:'a'.repeat(40)});
    if(u.includes('/raw/'))return new Response('public test source');
    if(u.endsWith('/info'))return Response.json({named_endpoints:{'/generate_image':{parameters:['prompt','model_name','negative_prompt','seed','width','height','guidance_scale','num_inference_steps'].map(parameter_name=>({parameter_name}))}}});
    if(o?.method==='POST')return Response.json({event_id:'abc'});
    if(u.endsWith('/abc'))return new Response('event: complete\ndata: [{"url":"'+cfg.host+'/image.png"}]\n\n');
    return new Response(bytes);
  };
  assert.equal((await generateBatch({dataRoot:dir,maxRequests:1,fetcher:fake})).completed,1);
  await writeFile(path.join(dir,'raw_images',images[0].image_id+'.bin'),Buffer.alloc(24,4));
  let called=false;
  await assert.rejects(()=>generateBatch({dataRoot:dir,maxRequests:1,resume:true,fetcher:async()=>{called=true;throw Error('must not call network');}}),/hash mismatch/);
  assert.equal(called,false);
});
