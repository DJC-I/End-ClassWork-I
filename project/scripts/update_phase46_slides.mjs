// Preserve source OOXML because artifact import/export loses chart workbook links.
import {spawnSync} from 'node:child_process';
const result=spawnSync(process.env.RUNTIME_PYTHON,['scripts/update_phase46_documents.py'],{stdio:'inherit'});
if(result.status!==0)throw new Error('Material update failed');
await import('./finalize_phase46_slides.mjs');
