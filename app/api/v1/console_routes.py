"""Trust Trigger Delivery Console — API routes and HTML interface."""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.workflow_db import ProjectDB, TaskDB, ProjectDBStatus, TaskDBStatus
from app.services.content_pipeline import run_content_generator, GENERATORS
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel
router = APIRouter(prefix="/console", tags=["Delivery Console"])

@router.get("/api/queue")
async def get_console_queue(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProjectDB).order_by(ProjectDB.created_at.desc()).limit(50))
    projects = result.scalars().all()
    queue = []
    for p in projects:
        tasks = await db.execute(select(TaskDB).where(TaskDB.project_id == p.id).order_by(TaskDB.created_at))
        task_list = tasks.scalars().all()
        total = len(task_list)
        completed = sum(1 for t in task_list if t.status in (TaskDBStatus.completed, TaskDBStatus.approved, TaskDBStatus.skipped))
        awaiting = [t for t in task_list if t.status == TaskDBStatus.awaiting_review]
        failed = [t for t in task_list if t.status == TaskDBStatus.failed]
        rejected = [t for t in task_list if t.status == TaskDBStatus.rejected]
        priority = "attention" if rejected or failed else "review" if awaiting else "normal"
        progress = round(completed / total * 100, 1) if total > 0 else 0
        queue.append({
            "id": p.id, "business_name": p.business_name, "status": p.status.value,
            "progress": progress, "priority": priority,
            "tasks_awaiting_review": len(awaiting), "tasks_failed": len(failed),
            "tasks_rejected": len(rejected), "task_count": total, "tasks_completed": completed,
        })
    return {"queue": queue, "total": len(queue)}

@router.get("/api/projects/{project_id}/review")
async def get_project_review(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProjectDB).where(ProjectDB.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    tasks = await db.execute(select(TaskDB).where(TaskDB.project_id == project_id).order_by(TaskDB.created_at))
    task_list = tasks.scalars().all()
    timeline = [{"id": t.id, "type": t.type.value, "status": t.status.value, "created_at": t.created_at.isoformat() if t.created_at else None, "completed_at": t.completed_at.isoformat() if t.completed_at else None, "duration_seconds": t.duration_seconds, "output": t.output, "review_notes": t.review_notes, "depends_on": t.depends_on} for t in task_list]
    content_tasks = [t for t in task_list if t.status in (TaskDBStatus.awaiting_review, TaskDBStatus.rejected)]
    return {
        "project": {
            "id": project.id, "business_name": project.business_name, "website": project.website,
            "email": project.email, "status": project.status.value,
            "progress": round(sum(1 for t in task_list if t.status in (TaskDBStatus.completed, TaskDBStatus.approved, TaskDBStatus.skipped)) / len(task_list) * 100 if task_list else 0, 1),
        },
        "timeline": timeline,
        "content_tasks": [{"id": t.id, "type": t.type.value, "status": t.status.value, "output": t.output, "review_notes": t.review_notes, "versions": t.attempts if t.attempts else []} for t in content_tasks],
    }

Part 2:

class ApproveTaskRequest(BaseModel):
    approved: bool
    notes: str = ""
@router.post("/api/tasks/{task_id}/review")
async def review_task(task_id: str, req: ApproveTaskRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TaskDB).where(TaskDB.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = TaskDBStatus.approved if req.approved else TaskDBStatus.rejected
    task.reviewed_at = datetime.now(timezone.utc)
    task.review_notes = req.notes
    await db.commit()
    return {"success": True, "task_id": task_id, "new_status": task.status.value}

@router.post("/api/tasks/{task_id}/regenerate")
async def regenerate_task_content(task_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TaskDB).where(TaskDB.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = TaskDBStatus.pending
    task.retry_count = 0
    task.reviewed_by = None
    task.reviewed_at = None
    from app.models.workflow_engine import Task as WfTask, Project as WfProject
    wf_task = WfTask(id=task.id, project_id=task.project_id, type=task.type.value, depends_on=task.depends_on)
    proj = await db.execute(select(ProjectDB).where(ProjectDB.id == task.project_id))
    pdb = proj.scalar_one_or_none()
    wf_project = WfProject(id=pdb.id, organisation_id=pdb.organisation_id, lead_id=pdb.lead_id, business_name=pdb.business_name, website=pdb.website, email=pdb.email)
    output = await run_content_generator(wf_task, wf_project)
    task.output = output
    task.status = TaskDBStatus.awaiting_review if output.get("generated") else TaskDBStatus.failed
    await db.commit()
    return {"success": True, "task_id": task_id, "new_status": task.status.value, "output": output}

@router.post("/api/bulk/approve")
async def bulk_approve(task_ids: list[str], db: AsyncSession = Depends(get_db)):
    count = 0
    for tid in task_ids:
        result = await db.execute(select(TaskDB).where(TaskDB.id == tid))
        task = result.scalar_one_or_none()
        if task and task.status == TaskDBStatus.awaiting_review:
            task.status = TaskDBStatus.approved
            task.reviewed_at = datetime.now(timezone.utc)
            count += 1
    await db.commit()
    return {"success": True, "approved": count}

CONSOLE_HTML = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Trust Trigger Delivery Console</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh}
.app{display:flex;min-height:100vh}
.sidebar{width:240px;background:#1e293b;padding:1.5rem;border-right:1px solid #334155;flex-shrink:0}
.sidebar h1{font-size:1rem;font-weight:700;color:#fbbf24;margin-bottom:1.5rem}
.sidebar .nav-item{padding:.6rem .8rem;border-radius:8px;color:#94a3b8;font-size:.85rem;cursor:pointer;margin-bottom:2px}
.sidebar .nav-item:hover{background:#334155;color:#e2e8f0}
.main{flex:1;padding:1.5rem 2rem;overflow-y:auto}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem}
.header h2{font-size:1.4rem;font-weight:700}
.header .stats{display:flex;gap:1.5rem;font-size:.8rem;color:#94a3b8}
.queue{display:flex;flex-direction:column;gap:.6rem}
.queue-card{background:#1e293b;border:1px solid #334155;border-radius:10px;padding:.9rem 1.1rem;cursor:pointer;display:flex;align-items:center;gap:1rem}
.queue-card:hover{border-color:#fbbf24}
.queue-card .dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.queue-card .dot.review{background:#22c55e}
.queue-card .dot.attention{background:#ef4444}
.queue-card .info{flex:1}
.queue-card .info .name{font-weight:600;font-size:.9rem}
.queue-card .info .meta{font-size:.75rem;color:#94a3b8;margin-top:2px}
.queue-card .progress{text-align:right}
.queue-card .progress .pct{font-weight:700;font-size:1rem}
.queue-card .progress .label{font-size:.7rem;color:#64748b}
.review-layout{display:grid;grid-template-columns:200px 1fr;gap:1.5rem}
.task-list{display:flex;flex-direction:column;gap:4px}
.task-item{padding:.5rem .7rem;border-radius:6px;font-size:.8rem;color:#94a3b8;cursor:pointer;border:1px solid transparent}
.task-item:hover{background:#334155;color:#e2e8f0}
.task-item.active{background:#334155;border-color:#fbbf24;color:#fbbf24}
.task-item .s{display:inline-block;width:6px;height:6px;border-radius:50%;margin-right:6px}
.task-item .s.awaiting_review{background:#fbbf24}
.task-item .s.approved{background:#22c55e}
.task-item .s.rejected{background:#ef4444}
.review-content{background:#1e293b;border:1px solid #334155;border-radius:10px;padding:1.25rem}
.review-content .output{font-size:.85rem;line-height:1.6;color:#cbd5e1;white-space:pre-wrap;font-family:monospace;background:#0f172a;padding:1rem;border-radius:6px;margin-top:.5rem;max-height:350px;overflow-y:auto}
.review-content .actions{display:flex;gap:.5rem;margin-top:1rem}
.review-content .actions button{padding:.5rem 1rem;border-radius:6px;border:none;font-weight:600;font-size:.8rem;cursor:pointer;font-family:inherit}
.btn-approve{background:#22c55e;color:#fff}
.btn-reject{background:#ef4444;color:#fff}
.btn-regenerate{background:#f59e0b;color:#0f172a}
.timeline{background:#1e293b;border:1px solid #334155;border-radius:10px;padding:1.25rem;margin-top:1.5rem}
.timeline h3{font-size:.8rem;font-weight:600;color:#94a3b8;margin-bottom:.8rem;text-transform:uppercase;letter-spacing:.05em}
.timeline-item{display:flex;align-items:center;gap:.5rem;padding:.3rem 0;font-size:.8rem}
.timeline-item .icon{width:18px;text-align:center}
.timeline-item .icon.completed{color:#22c55e}
.timeline-item .icon.pending{color:#64748b}
.timeline-item .icon.failed{color:#ef4444}
.timeline-item .icon.awaiting_review{color:#fbbf24}
.back-btn{background:none;border:none;color:#94a3b8;cursor:pointer;font-size:.85rem;margin-bottom:1rem;font-family:inherit}
.back-btn:hover{color:#fbbf24}
</style></head>
<body>
<div class="app">
<div class="sidebar"><h1>🛡️ Delivery Console</h1>
<div class="nav-item" onclick="location.reload()">📋 Queue</div>
<div class="nav-item" style="font-size:.7rem;color:#64748b;margin-top:2rem">Trust Trigger Agency v1.0</div>
</div>
<div class="main">
<div id="queueView">
<div class="header"><h2>Fulfilment Queue</h2>
<div class="stats"><span id="totalCount">0</span> projects <span id="reviewCount">0</span> to review</div>
</div>
<div class="queue" id="queueList"></div>
</div>
<div id="reviewView" style="display:none">
<button class="back-btn" onclick="showQueue()">← Back</button>
<div class="header"><h2 id="reviewProjectName">Project</h2>
<div class="stats"><span id="reviewProgress">0%</span> complete</div>
</div>
<div class="review-layout">
<div class="task-list" id="taskList"></div>
<div class="review-content" id="reviewContent"><div style="color:#64748b;text-align:center;padding:2rem">Select a task</div></div>
</div>
<div class="timeline" id="timeline"><h3>Timeline</h3><div id="timelineList"></div></div>
</div>
</div></div>
<script>
const API='/console/api';
let currentProjectId=null,currentTasks=[];
async function loadQueue(){const r=await(await fetch(API+'/queue')).json();const l=document.getElementById('queueList');l.innerHTML='';document.getElementById('totalCount').textContent=r.total;let rc=0;
r.queue.forEach(p=>{if(p.tasks_awaiting_review>0||p.priority==='attention')rc++;const c=document.createElement('div');c.className='queue-card';c.onclick=()=>loadProject(p.id);
c.innerHTML='<div class="dot '+(p.priority==='review'?'review':p.priority==='attention'?'attention':'')+'"></div><div class="info"><div class="name">'+p.business_name+'</div><div class="meta">'+
(p.tasks_awaiting_review>0?'<span style="color:#fbbf24">'+p.tasks_awaiting_review+' to review</span> ':'')+
(p.tasks_failed>0?'<span style="color:#ef4444">'+p.tasks_failed+' failed</span> ':'')+
(p.tasks_rejected>0?'<span style="color:#f59e0b">'+p.tasks_rejected+' rejected</span> ':'')+'</div></div>'+
'<div class="progress"><div class="pct">'+p.progress+'%</div><div class="label">'+p.tasks_completed+'/'+p.task_count+' tasks</div></div></div>';
l.appendChild(c)});document.getElementById('reviewCount').textContent=rc}
async function loadProject(id){currentProjectId=id;const d=await(await fetch(API+'/projects/'+id+'/review')).json();currentTasks=d.content_tasks;
document.getElementById('reviewProjectName').textContent=d.project.business_name;document.getElementById('reviewProgress').textContent=d.project.progress;
const tl=document.getElementById('taskList');tl.innerHTML='';
d.content_tasks.forEach((t,i)=>{const e=document.createElement('div');e.className='task-item'+(i===0?' active':'');e.onclick=()=>selectTask(t,i);e.id='ti'+i;
e.innerHTML='<span class="s '+t.status+'"></span>'+(t.status==='approved'?'✅':t.status==='rejected'?'🔄':'⏳')+' '+t.type.replace(/_/g,' ');tl.appendChild(e)});
const tml=document.getElementById('timelineList');tml.innerHTML='';
d.timeline.forEach(t=>{const e=document.createElement('div');e.className='timeline-item';
const ic=t.status==='completed'||t.status==='approved'?'✅':t.status==='failed'?'❌':t.status==='awaiting_review'?'⏳':'⬜'
const icc=t.status==='completed'||t.status==='approved'?'completed':t.status==='failed'?'failed':t.status==='awaiting_review'?'awaiting_review':'pending';
e.innerHTML='<span class="icon '+icc+'">'+ic+'</span><span>'+t.type.replace(/_/g,' ')+'</span>';tml.appendChild(e)});
if(d.content_tasks.length>0)selectTask(d.content_tasks[0],0);else document.getElementById('reviewContent').innerHTML='<div style="color:#64748b;text-align:center;padding:2rem">All tasks completed</div>';
document.getElementById('queueView').style.display='none';document.getElementById('reviewView').style.display='block'}
function selectTask(t,i){document.querySelectorAll('.task-item').forEach(e=>e.classList.remove('active'));const e=document.getElementById('ti'+i);if(e)e.classList.add('active');
const out=t.output&&t.output.content?t.output.content:t.output&&t.output.emails?JSON.stringify(t.output.emails,null,2):t.output&&t.output.posts?t.output.posts.join('\\n'):t.output&&t.output.facebook?'Facebook:\\n'+t.output.facebook.join('\\n')+'\\n\\nInstagram:\\n'+t.output.instagram.join('\\n'):'No content';
document.getElementById('reviewContent').innerHTML='<h3 style="font-size:1rem;font-weight:600;margin-bottom:.5rem;text-transform:capitalize">'+t.type.replace(/_/g,' ')+'</h3><p style="font-size:.8rem;color:#94a3b8;margin-bottom:.5rem">Status: '+t.status+'</p>'+
(t.review_notes?'<p style="color:#f59e0b;font-size:.8rem">Notes: '+t.review_notes+'</p>':'')+
'<div class="output">'+out+'</div><div class="actions"><button class="btn-approve" onclick="reviewTask(\\''+t.id+'\\',true)">✅ Approve</button>'+
'<button class="btn-reject" onclick="reviewTask(\\''+t.id+'\\',false)">❌ Reject</button>'+
'<button class="btn-regenerate" onclick="regenerateTask(\\''+t.id+'\\')">🔄 Regenerate</button></div>'}
async function reviewTask(id,a){await fetch(API+'/tasks/'+id+'/review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({approved:a,notes:''})});loadProject(currentProjectId)}
async function regenerateTask(id){await fetch(API+'/tasks/'+id+'/regenerate',{method:'POST'});loadProject(currentProjectId)}
function showQueue(){document.getElementById('queueView').style.display='block';document.getElementById('reviewView').style.display='none';loadQueue()}
loadQueue();
</script>
</body></html>"""

@router.get("", response_class=HTMLResponse)
async def delivery_console():
    return HTMLResponse(content=CONSOLE_HTML)
