import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const ROOT=process.cwd(),MOD=process.env.RUNTIME_NODE_MODULES;
const {createRequire}=await import('node:module');const req=createRequire(path.join(MOD,'__phase46.cjs'));
const {createHash}=await import('node:crypto');
const {Presentation,PresentationFile,FileBlob}=await import(pathToFileURL(req.resolve('@oai/artifact-tool')).href);
const SKILL='./.codex/plugins/cache/openai-primary-runtime/presentations/26.1112.11217/skills/presentations';
const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const reference=path.join(ROOT,'deliverables/phase4/人工智能导论_双赛题结课作品展示.pptx');
const referenceSha=createHash('sha256').update(await fs.readFile(reference)).digest('hex');
const candidate=path.join(ROOT,'.tools/phase4_6/build/candidate.pptx');
const existing=path.join(ROOT,'deliverables/phase4_6/人工智能导论_双赛题结课作品展示.pptx');
try { await fs.copyFile(existing,path.join(ROOT,'.tools/phase4_6/build/previous-'+Date.now()+'.pptx')); await fs.unlink(existing); } catch(e) { if(e.code!=='ENOENT') throw e; }
const receipt=path.join(ROOT,'docs/phase4_6/pptx-validation.json');
try { await fs.rename(receipt,path.join(ROOT,'.tools/phase4_6/build/validation-'+Date.now()+'.json')); } catch(e) { if(e.code!=='ENOENT') throw e; }
const result=await finalizePresentation({workspaceDir:ROOT,candidatePath:candidate,finalPath:path.join(ROOT,'deliverables/phase4_6/人工智能导论_双赛题结课作品展示.pptx'),pythonExecutable:process.env.RUNTIME_PYTHON,integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),explicitTotalSlideCount:12,requiredNativeTableOwnerSlides:[4,5,7,10,11],requiredNativeChartOwnerSlides:[11],fontPolicy:{basis:'reference',families:['Microsoft YaHei'],referencePath:reference,referenceSha256:referenceSha},layoutArgs:['--expected-slide-size-emu','12192000,6858000',...[4,5,7,10,11].flatMap(n=>['--require-native-table-slide',String(n)])],receiptPath:path.join(ROOT,'docs/phase4_6/pptx-validation.json')});
console.log(JSON.stringify(result));
