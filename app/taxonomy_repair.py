"""CV-AI taxonomy repair utility. Save as C:\\CV_AI\\app\\taxonomy_repair.py and run with the project venv."""
import json, shutil
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

APP = Path(__file__).resolve().parent
ROOT = APP.parent
TAX = ROOT / '09_CONFIG' / 'taxonomy'
BACKUPS = ROOT / '10_BACKUP'
REQUIRED = ['taxonomy_metadata.json','domains.json','functions.json','activities.json','technologies.json','architectures.json','aliases.json']
OVERRIDES = {
 'MV_LV':'Medium-Voltage / Low-Voltage','CRAC_CRAH':'CRAC / CRAH','DX':'Direct Expansion (DX)',
 'DCIM':'Data Center Infrastructure Management (DCIM)','BMS':'Building Management System (BMS)',
 'SD_WAN':'Software-Defined WAN (SD-WAN)','IP_MPLS':'IP / MPLS','VXLAN_EVPN':'VXLAN / EVPN',
 'NAC':'Network Access Control (NAC)','NGFW':'Next-Generation Firewall (NGFW)',
 'SIEM':'Security Information and Event Management (SIEM)','SOAR':'Security Orchestration, Automation and Response (SOAR)',
 'NDR':'Network Detection and Response (NDR)','IAM':'Identity and Access Management (IAM)',
 'PAM':'Privileged Access Management (PAM)','VAPT':'Vulnerability Assessment and Penetration Testing (VAPT)',
 'GRC':'Governance, Risk and Compliance (GRC)','HCI':'Hyper-Converged Infrastructure (HCI)',
 'HPC':'High-Performance Computing (HPC)','GPU_INFRASTRUCTURE':'GPU Infrastructure',
 'AI_NETWORKING':'AI Networking','AI_STORAGE':'AI Storage','MLOPS':'Machine Learning Operations (MLOps)',
 'RAG':'Retrieval-Augmented Generation (RAG)','NLP':'Natural Language Processing (NLP)',
 'HRBP':'Human Resources Business Partner (HRBP)','HRIS':'Human Resources Information System (HRIS)',
 'PO':'Purchase Orders','DR':'Disaster Recovery (DR)','HA_DR':'High Availability and Disaster Recovery',
 'SAN':'Storage Area Network (SAN)','NAS':'Network-Attached Storage (NAS)','NVME':'Non-Volatile Memory Express (NVMe)',
 'NVME_OF':'NVMe over Fabrics (NVMe-oF)','IOT':'Internet of Things (IoT)','OT':'Operational Technology (OT)',
 'SCADA':'Supervisory Control and Data Acquisition (SCADA)','API':'Application Programming Interfaces (APIs)',
 'SAAS':'Software as a Service (SaaS)','MPLS':'Multiprotocol Label Switching (MPLS)'
}
def load(path):
    with path.open(encoding='utf-8') as f: return json.load(f)
def save(path, obj):
    with path.open('w', encoding='utf-8', newline='\n') as f: json.dump(obj, f, ensure_ascii=False, indent=4); f.write('\n')
def humanize(token): return OVERRIDES.get(token, ' '.join(x.capitalize() for x in token.split('_')))
def patch_loader(path):
    s = path.read_text(encoding='utf-8'); old = s
    replacements = [
      ('        "domains.json",\n        "functions.json",','        "domains.json",\n        "subdomains.json",\n        "functions.json",'),
      ('        self.domain_index = {}\n        self.function_index = {}','        self.domain_index = {}\n        self.subdomain_index = {}\n        self.function_index = {}'),
      ('        self._register_entities(\n            self.function_index,','        self._register_entities(\n            self.subdomain_index,\n            self.data["subdomains.json"].get("subdomains", [])\n        )\n\n        self._register_entities(\n            self.function_index,'),
      ('    def get_function(self, function_id):','    def get_subdomain(self, subdomain_id):\n        return self.subdomain_index.get(subdomain_id)\n\n    def get_function(self, function_id):'),
      ('    def get_functions(self, branch=None):','    def get_subdomains(self, branch=None):\n        return self._filter_by_branch(self.subdomain_index.values(), branch)\n\n    def get_functions(self, branch=None):'),
      ('            "domains": len(self.domain_index),\n            "functions": len(self.function_index),','            "domains": len(self.domain_index),\n            "subdomains": len(self.subdomain_index),\n            "functions": len(self.function_index),')]
    for a,b in replacements:
        if b not in s: s=s.replace(a,b)
    checks=['"subdomains.json"','self.subdomain_index = {}','self.data["subdomains.json"].get("subdomains", [])','def get_subdomain(','"subdomains": len(self.subdomain_index)']
    missing=[x for x in checks if x not in s]
    if missing: raise RuntimeError('Safe loader patch failed; missing insertion(s): '+', '.join(missing)+'. Loader not written.')
    if s != old: path.write_text(s, encoding='utf-8', newline='\n')
    return s != old

def main():
    if not TAX.is_dir(): raise SystemExit(f'Taxonomy folder not found: {TAX}')
    missing=[x for x in REQUIRED if not (TAX/x).is_file()]
    if missing: raise SystemExit('Required local files missing; no changes made: '+', '.join(missing))
    loader=APP/'taxonomy_loader.py'
    if not loader.is_file(): raise SystemExit(f'Loader not found: {loader}')
    stamp=datetime.now().strftime('%Y%m%d_%H%M%S'); backup=BACKUPS/f'taxonomy_repair_{stamp}'; backup.mkdir(parents=True, exist_ok=False)
    for f in TAX.glob('*.json'): shutil.copy2(f, backup/f.name)
    shutil.copy2(loader, backup/loader.name)
    validator = APP/'taxonomy_validator.py'
    if validator.is_file(): shutil.copy2(validator, backup/validator.name)
    try:
        docs={name:load(TAX/name) for name in REQUIRED}
        domains=docs['domains.json'].get('domains',[]); functions=docs['functions.json'].get('functions',[])
        techs=docs['technologies.json'].get('technologies',[]); activities_doc=docs['activities.json']; activities=activities_doc.setdefault('activities',[])
        activity_ids={x.get('id') for x in activities}; refs=defaultdict(list)
        for fn in functions:
            for aid in fn.get('activities',[]):
                if isinstance(aid,str): refs[aid].append(fn)
        added_activities=[]
        for aid in sorted(set(refs)-activity_ids):
            token=aid.split('.')[-1]; fns=refs[aid]; branches=[x.get('branch') for x in fns if x.get('branch')]
            branch=Counter(branches).most_common(1)[0][0] if branches else 'CROSS_FUNCTIONAL'
            lowered=(token+' '+' '.join(x.get('name','') for x in fns)).lower()
            groups=[(('tender','quotation','commercial','contract','oem','vendor','supplier'),'COMMERCIAL_AND_VENDOR'),(('audit','compliance','risk','taxation','financial_control'),'GOVERNANCE_AND_COMPLIANCE'),(('hr_','employee','compensation','benefits','onboarding'),'HUMAN_RESOURCES'),(('inventory','material','distribution','demand_planning','supply_chain'),'SUPPLY_CHAIN_AND_INVENTORY'),(('database','backup','recovery','patching','capacity','platform_engineering'),'TECHNICAL_OPERATIONS'),(('code','debug','release','migration','integration_design','interoperability'),'SOFTWARE_AND_INTEGRATION'),(('stakeholder','coordination','documentation','reporting','executive_support'),'COORDINATION_AND_ADMINISTRATION'),(('fat','sat','handover','training','poc','demo','technical_proposal'),'SOLUTION_DELIVERY')]
            category=next((cat for words,cat in groups if any(w in lowered for w in words)),'GENERAL_BUSINESS_OR_TECHNICAL_ACTIVITY')
            activities.append({'id':aid,'name':humanize(token),'category':category,'branch':branch,'aliases':[],
              'description':'Generated from an existing function-to-activity reference. Review and refine before production use.',
              'review_status':'GENERATED_NEEDS_REVIEW','generated_by':'taxonomy_repair.py'})
            added_activities.append(aid)

        subpath=TAX/'subdomains.json'; subdoc=load(subpath) if subpath.exists() else {'subdomains':[]}
        subs=subdoc.setdefault('subdomains',[]); sub_by_id={x.get('id'):x for x in subs if x.get('id')}
        domain_by_id={x.get('id'):x for x in domains if x.get('id')}; parents=defaultdict(list); tech_refs=defaultdict(list)
        for d in domains:
            for child in d.get('children',[]):
                if d.get('id') and d['id'] not in parents[child]: parents[child].append(d['id'])
        for t in techs:
            sid=t.get('subdomain')
            for x in (sid if isinstance(sid,list) else [sid]):
                if isinstance(x,str) and x: tech_refs[x].append(t)
        all_sids=set(parents)|set(tech_refs)|set(sub_by_id); added_subdomains=[]
        for sid in sorted(all_sids):
            inferred=list(dict.fromkeys(parents.get(sid,[])+[d for t in tech_refs.get(sid,[]) for d in t.get('domains',[]) if d in domain_by_id]))
            if sid in sub_by_id:
                if inferred and not sub_by_id[sid].get('parent_domain_ids'): sub_by_id[sid]['parent_domain_ids']=inferred
                continue
            token=sid.split('.')[-1]; branches=[domain_by_id[d].get('branch') for d in inferred if domain_by_id.get(d,{}).get('branch')]
            branch=Counter(branches).most_common(1)[0][0] if branches else ('BUSINESS_CORPORATE' if sid.startswith('BUSINESS.') else 'CROSS_FUNCTIONAL')
            subs.append({'id':sid,'name':humanize(token),'branch':branch,'parent_domain_ids':inferred,
              'description':'Generated from existing domain-child and/or technology references. Review name, parent domain(s), and definition before production use.',
              'aliases':[],'review_status':'GENERATED_NEEDS_REVIEW','generated_by':'taxonomy_repair.py'})
            sub_by_id[sid]=subs[-1]; added_subdomains.append(sid)
        subdoc['subdomains']=subs; save(subpath,subdoc); save(TAX/'activities.json',activities_doc)
        loader_changed=patch_loader(loader)
        validator_changed=False
        if validator.is_file():
            validator_text=validator.read_text(encoding='utf-8')
            corrected=validator_text.replace("metadata.get('version')", "metadata.get('taxonomy_version')").replace('metadata.get("version")', 'metadata.get("taxonomy_version")')
            if corrected != validator_text:
                validator.write_text(corrected, encoding='utf-8', newline='\n')
                validator_changed=True

        errors=[]; warnings=[]; seen={}
        collections=[('domains',domains),('subdomains',subs),('functions',functions),('activities',activities),('technologies',techs),('architectures',docs['architectures.json'].get('architectures',[]))]
        for label,records in collections:
            for rec in records:
                eid=rec.get('id')
                if not eid: errors.append(f'{label}: record missing id: {rec.get("name","<unnamed>")}'); continue
                if eid in seen: errors.append(f'Duplicate entity ID {eid} in {seen[eid]} and {label}')
                else: seen[eid]=label
        aids={x.get('id') for x in activities}; sids={x.get('id') for x in subs}; dids=set(domain_by_id)
        for fn in functions:
            for aid in fn.get('activities',[]):
                if aid not in aids: errors.append(f'{fn.get("id")} references missing activity {aid}')
        for d in domains:
            for child in d.get('children',[]):
                if child not in sids: errors.append(f'{d.get("id")} references missing subdomain {child}')
        for t in techs:
            sid=t.get('subdomain')
            for x in (sid if isinstance(sid,list) else [sid]):
                if x and x not in sids: errors.append(f'{t.get("id")} references missing subdomain {x}')
            for did in t.get('domains',[]):
                if did not in dids: warnings.append(f'{t.get("id")} references unknown domain {did}')
        meta=docs['taxonomy_metadata.json']; version=meta.get('taxonomy_version')
        if not isinstance(version,str) or not version.strip(): errors.append('taxonomy_metadata.json: taxonomy_version missing/invalid')
        for alias in docs['aliases.json'].get('aliases',[]):
            for target in alias.get('entity_ids',[]):
                if target not in seen: errors.append(f'Alias {alias.get("alias")!r} targets unknown entity {target}')
        report=['CV-AI TAXONOMY REPAIR REPORT',f'Run: {stamp}',f'Taxonomy: {TAX}',f'Backup: {backup}',
          f'Activity definitions added: {len(added_activities)}',f'Subdomain definitions added: {len(added_subdomains)}',f'Total subdomains: {len(subs)}',
          f'Loader updated for subdomain indexing: {loader_changed}',f'Validator metadata field corrected: {validator_changed}',f'Validation errors: {len(errors)}',f'Warnings: {len(warnings)}','',
          'ADDED ACTIVITIES (generated; review before production):',*(added_activities or ['(none)']),'',
          'ADDED SUBDOMAINS (generated; review before production):',*(added_subdomains or ['(none)']),'','WARNINGS:',*(warnings or ['(none)']),'','ERRORS:',*(errors or ['(none)']),
          '', 'Generated records are scaffolding derived from existing references, not authoritative definitions.',
          'Records marked GENERATED_NEEDS_REVIEW must be reviewed before production use.']
        log=ROOT/'08_LOGS'/'taxonomy_repair_report.txt'; log.parent.mkdir(parents=True,exist_ok=True); log.write_text('\n'.join(report)+'\n',encoding='utf-8')
        print('\n'.join(report)); print(f'\nReport saved to: {log}')
        if errors: raise SystemExit(2)
        print('\nSTRUCTURAL VALIDATION PASSED. Please review generated entries before using them for candidate classification.')
    except Exception:
        # Restore all changed files from this run's backup if an unexpected failure occurs.
        for name in ('activities.json','subdomains.json'):
            src=backup/name; dst=TAX/name
            if src.exists(): shutil.copy2(src,dst)
            elif dst.exists(): dst.unlink()
        shutil.copy2(backup/loader.name,loader)
        if validator.is_file() and (backup/validator.name).is_file(): shutil.copy2(backup/validator.name,validator)
        raise

if __name__=='__main__': main()
