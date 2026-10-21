/** Remote P9-v3 image generation following manual_validation/VLM/SD-Turbo.py.
 * Dependency-free Gradio REST transport. Requires Node >= 20.
 * node experiments/v3/generate_remote_dataset.mjs --execute [--resume]
 * No extraction model is invoked and no naturalistic labels are fabricated.
 */
import * as fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
export const DEFAULT_DATA = path.join(ROOT, 'artifacts/downloads/p9_v3');
const CONFIG = path.join(ROOT, 'experiments/v3/config/remote_generation_v3_4.json');
const envToken = () => typeof process === 'undefined' ? undefined : process.env.P9_HF_TOKEN;
export const hash = value => createHash('sha256').update(value).digest('hex');
const read = async p => JSON.parse(await fs.readFile(p, 'utf8'));
const exists = async p => { try { await fs.access(p); return true; } catch { return false; } };

async function atomicJson(p, value) {
  await fs.mkdir(path.dirname(p), { recursive: true });
  const tmp = p + '.tmp';
  await fs.writeFile(tmp, JSON.stringify(value, null, 2) + '\n');
  await fs.rename(tmp, p);
}

export function validatePlan(plan, cfg) {
  if (plan.model_id !== 'stabilityai/sd-turbo' || plan.model_id !== cfg.requested_model_id ||
      plan.space_id !== cfg.space_id || JSON.stringify(plan.requested_parameters) !== JSON.stringify(cfg.requested_parameters)) {
    // Compare canonical properties below too; object key order has no scientific meaning.
    const p = plan.requested_parameters;
    if (plan.model_id !== cfg.requested_model_id || plan.model_id !== 'stabilityai/sd-turbo' || plan.space_id !== cfg.space_id ||
        !p || Object.keys(p).length !== Object.keys(cfg.requested_parameters).length ||
        Object.entries(cfg.requested_parameters).some(([k,v]) => p[k] !== v)) throw Error('Generation plan/config mismatch');
  }
  const expected = new Set();
  for (let f=1;f<=24;f++) for(let i=1;i<=5;i++) expected.add(`cap-v3-B-F${String(f).padStart(2,'0')}-${String(i).padStart(2,'0')}`);
  if (plan.images.length !== 120) throw Error('Expected 120 naturalistic requests');
  for (const row of plan.images) {
    if (!expected.delete(row.image_id) || typeof row.prompt !== 'string' || !row.prompt.trim()) throw Error('Duplicate/invalid request');
    const f=Number(row.image_id.slice(10,12)), i=Number(row.image_id.slice(-2));
    if (row.seed !== 925031+100*f+i || row.split !== (f<=12?'development':'validation') || row.family_id !== `F${String(f).padStart(2,'0')}`) throw Error('Seed/family/split mismatch');
  }
  if (expected.size) throw Error('Missing deterministic image IDs');
}

export function requestData(row, cfg) {
  const p=cfg.requested_parameters;
  return [row.prompt,cfg.requested_model_id,p.negative_prompt,row.seed,p.width,p.height,p.guidance_scale,p.num_inference_steps];
}

export function parseEvent(block) {
  const lines=block.replaceAll('\r','').split('\n');
  const event=lines.find(l=>l.startsWith('event:'))?.slice(6).trim();
  const text=lines.filter(l=>l.startsWith('data:')).map(l=>l.slice(5).trimStart()).join('\n');
  if(!event || !text) return null;
  if(event==='error') throw Error('Gradio event error: '+text.slice(0,1500));
  return {event,data:JSON.parse(text)};
}

export function pngDimensions(bytes) {
  if(bytes.length<24 || bytes.subarray(0,8).toString('hex')!=='89504e470d0a1a0a') throw Error('Server did not return a PNG');
  const size=[bytes.readUInt32BE(16),bytes.readUInt32BE(20)];
  if(size[0]!==512 || size[1]!==512) throw Error('Server image is not 512x512');
  return size;
}

async function checkedFetch(url, opts={}, fetcher=fetch) {
  const r=await fetcher(url,{...opts,signal:opts.signal || AbortSignal.timeout(180000)});
  if(!r.ok) throw Error(`HTTP ${r.status} at ${new URL(url).pathname}: ${(await r.text()).slice(0,500)}`);
  return r;
}

export async function callGradio(row, cfg, fetcher=fetch) {
  const headers={'Content-Type':'application/json'};
  // Explicit env token only. Never read or transmit a token embedded in VLM examples.
  if(envToken()) headers.Authorization=`Bearer ${envToken()}`;
  const base=cfg.host+'/gradio_api/call'+cfg.api_name;
  const queued=await (await checkedFetch(base,{method:'POST',headers,body:JSON.stringify({data:requestData(row,cfg)})},fetcher)).json();
  if(typeof queued.event_id!=='string' || !/^[\w-]+$/.test(queued.event_id)) throw Error('Invalid Gradio event ID');
  const stream=await checkedFetch(base+'/'+queued.event_id,{headers,signal:AbortSignal.timeout(240000)},fetcher);
  const reader=stream.body.getReader(), decoder=new TextDecoder();
  let buffer='', result;
  try {
    while(true) {
      const {value,done}=await reader.read();
      buffer+=decoder.decode(value,{stream:!done}).replaceAll('\r','');
      let end;
      while((end=buffer.indexOf('\n\n'))!==-1) {
        const event=parseEvent(buffer.slice(0,end)); buffer=buffer.slice(end+2);
        if(event?.event==='complete') {result=event.data; break;}
      }
      if(result!==undefined || done) break;
      if(buffer.length>4e6) throw Error('Oversized Gradio event');
    }
  } finally { await reader.cancel().catch(()=>{}); }
  if(!Array.isArray(result)||result.length!==1||!result[0]) throw Error('Missing image output; no substitute/retry selected');
  const image=result[0];
  const url=image.url || (image.path?cfg.host+'/gradio_api/file='+image.path:null);
  if(!url || new URL(url).origin!==new URL(cfg.host).origin) throw Error('Unexpected image-download host');
  const bytes=Buffer.from(await (await checkedFetch(url,{headers},fetcher)).arrayBuffer());
  // Gradio may encode a PIL image as WebP. Retain the original response bytes;
  // Pillow performs lossless-format PNG materialization as a separate step.
  if(bytes.length<24) throw Error('Truncated remote image');
  return {bytes,event_id:queued.event_id,remote_file:image};
}

async function captureServer(dataRoot,cfg,fetcher) {
  const dir=path.join(dataRoot,'provenance');
  await fs.mkdir(dir,{recursive:true});
  const metadata=await (await checkedFetch('https://huggingface.co/api/spaces/'+cfg.space_id,{},fetcher)).json();
  if(!/^[a-f0-9]{40}$/.test(metadata.sha)) throw Error('Missing Space commit provenance');
  const source=await (await checkedFetch(`https://huggingface.co/spaces/${cfg.space_id}/raw/${metadata.sha}/app.py`,{},fetcher)).text();
  const api=await (await checkedFetch(cfg.host+'/gradio_api/info',{},fetcher)).json();
  const names=api.named_endpoints?.[cfg.api_name]?.parameters.map(p=>p.parameter_name);
  if(JSON.stringify(names)!==JSON.stringify(['prompt','model_name','negative_prompt','seed','width','height','guidance_scale','num_inference_steps'])) throw Error('Remote API parameter order changed');
  const sourceFile=`space_app_${metadata.sha}.py`;
  const sourcePath=path.join(dir,sourceFile);
  if(await exists(sourcePath)) {
    if(hash(await fs.readFile(sourcePath))!==hash(source)) throw Error('Space source changed at the same commit');
  } else await fs.writeFile(sourcePath,source,{flag:'wx'});
  const apiHash=hash(JSON.stringify(api)),apiFile='api_schema_'+apiHash+'.json';
  if(!await exists(path.join(dir,apiFile))) await atomicJson(path.join(dir,apiFile),api);
  // Keep the first readable alias; every session also names its immutable copy.
  if(!await exists(path.join(dir,'api_schema.json'))) await atomicJson(path.join(dir,'api_schema.json'),api);
  return {space_commit:metadata.sha,space_source_path:'provenance/'+sourceFile,space_source_sha256:hash(source),api_schema_path:'provenance/'+apiFile,api_schema_sha256:apiHash,captured_at_utc:new Date().toISOString(),model_revision_verified:false};
}

export async function generateBatch({dataRoot=DEFAULT_DATA,maxRequests=120,resume=false,onProgress=()=>{},fetcher=fetch}={}) {
  const cfg=await read(CONFIG);
  const planPath=path.join(dataRoot,'plans/naturalistic_prompt_plan_v3_4.json');
  const planBytes=await fs.readFile(planPath),plan=JSON.parse(planBytes);
  validatePlan(plan,cfg);
  if(plan.generation_amendment_sha256!==hash(await fs.readFile(CONFIG))) throw Error('Amendment hash mismatch');
  const receiptPath=path.join(dataRoot,'provenance/remote_generation_receipt_v3_4.json');
  let receipt;
  if(await exists(receiptPath)) {
    if(!resume) throw Error('Receipt exists: use --resume to verify and continue');
    receipt=await read(receiptPath);
    if(receipt.prompt_plan_sha256!==hash(planBytes)||receipt.generation_amendment_sha256!==plan.generation_amendment_sha256) throw Error('Resume plan/config hash mismatch');
  } else {
    receipt={schema_version:'remote-generation-receipt-v3.4.0',status:'partial',requested_model_id:cfg.requested_model_id,
      requested_parameters:cfg.requested_parameters,actual_model_revision:null,actual_parameters_verified:false,
      prompt_plan_sha256:hash(planBytes),generation_amendment_sha256:plan.generation_amendment_sha256,
      source_limitations:cfg.provenance_limit,created_at_utc:new Date().toISOString(),sessions:[],records:[]};
  }
  const records=new Map();
  for(const r of receipt.records) {
    if(records.has(r.image_id)||!plan.images.some(x=>x.image_id===r.image_id)) throw Error('Duplicate/unknown receipt image');
    const bytes=await fs.readFile(path.join(dataRoot,'raw_images',r.image_id+'.bin'));
    if(hash(bytes)!==r.raw_image_sha256) throw Error('Resume image hash mismatch: '+r.image_id);
    const core={...r}; delete core.record_sha256;
    if(hash(JSON.stringify(core))!==r.record_sha256) throw Error('Receipt record integrity failure');
    records.set(r.image_id,r);
  }
  // Verify the whole directory before any external call, including orphan images.
  for(const row of plan.images) if(!records.has(row.image_id)&&await exists(path.join(dataRoot,'raw_images',row.image_id+'.bin'))) throw Error('Unreceipted image: '+row.image_id);
  if(records.size===120) return {status:'complete',completed:120,new_images:0};
  const session=await captureServer(dataRoot,cfg,fetcher);
  const originalSession=receipt.sessions[0];
  if(originalSession&&(originalSession.space_commit!==session.space_commit||originalSession.api_schema_sha256!==session.api_schema_sha256)) throw Error('Space source/API changed during dataset generation; start an explicitly versioned new dataset');
  receipt.sessions.push(session);
  await atomicJson(receiptPath,receipt);
  await fs.mkdir(path.join(dataRoot,'raw_images'),{recursive:true});
  let generated=0;
  for(const row of plan.images) {
    if(records.has(row.image_id)) continue;
    if(generated>=maxRequests) break;
    const start=Date.now();
    try {
      const output=await callGradio(row,cfg,fetcher);
      const record={image_id:row.image_id,prompt_sha256:hash(row.prompt),seed:row.seed,
        raw_image_sha256:hash(output.bytes),bytes:output.bytes.length,event_id:output.event_id,
        space_commit:session.space_commit,requested_model_id:cfg.requested_model_id,
        requested_parameters:cfg.requested_parameters,completed_at_utc:new Date().toISOString(),elapsed_seconds:(Date.now()-start)/1000};
      record.record_sha256=hash(JSON.stringify(record));
      // Image+receipt interruption leaves an explicit orphan that blocks resume;
      // never silently regenerate/overwrite it with another server sample.
      await fs.writeFile(path.join(dataRoot,'raw_images',row.image_id+'.bin'),output.bytes,{flag:'wx'});
      receipt.records.push(record); records.set(row.image_id,record); generated++;
      receipt.status=records.size===120?'complete':'partial';
      await atomicJson(receiptPath,receipt);
      onProgress({image_id:row.image_id,completed:records.size,total:120,seconds:record.elapsed_seconds});
    } catch(e) {
      let message=String(e);
      if(envToken()) message=message.replaceAll(envToken(),'[REDACTED]');
      const error={image_id:row.image_id,at_utc:new Date().toISOString(),error:message};
      await fs.appendFile(path.join(dataRoot,'provenance/generation_errors.jsonl'),JSON.stringify(error)+'\n');
      throw Error(`Generation stopped at ${row.image_id} (${records.size}/120 saved): ${message}`);
    }
  }
  return {status:receipt.status,completed:records.size,new_images:generated};
}

if(typeof process!=='undefined'&&process.argv[1]&&import.meta.url===pathToFileURL(path.resolve(process.argv[1])).href) {
  const args=process.argv.slice(2);
  if(!args.includes('--execute')) {
    console.log('Preflight only. Use --execute to generate the 120 planned images; --resume verifies existing receipts.');
  } else {
    const at=args.indexOf('--data-root');
    generateBatch({dataRoot:at<0?DEFAULT_DATA:path.resolve(args[at+1]),resume:args.includes('--resume'),onProgress:console.log})
      .then(console.log).catch(e=>{console.error(e.message);process.exitCode=1;});
  }
}
