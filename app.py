import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import select, delete, func
from database.connection import SessionLocal, init_db, engine
from database.models import JobPosting, PipelineRun, Company, Skill
from pipeline.orchestrator import run_pipeline
from data.sample.seed import seed_demo

st.set_page_config(page_title="JobLens BD", page_icon="J", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root{--ink:#172033;--muted:#68758a;--blue:#465fff;--line:#e7eaf0;--bg:#f7f8fb}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:var(--ink)} .stApp{background:var(--bg)}
[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--line)}
[data-testid="stSidebar"] h1{font-family:Manrope,sans-serif;letter-spacing:-.04em}
h1,h2,h3{font-family:Manrope,sans-serif;letter-spacing:-.035em}
[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);padding:18px 20px;border-radius:12px;box-shadow:0 2px 7px #17203308}
[data-testid="stMetricLabel"]{color:var(--muted)} [data-testid="stMetricValue"]{color:var(--ink);font-family:Manrope,sans-serif}
.stButton>button,.stDownloadButton>button{border-radius:8px;border:1px solid var(--line)}
hr{border-color:var(--line)} .subtle{color:var(--muted);font-size:.92rem} .eyebrow{text-transform:uppercase;letter-spacing:.12em;color:var(--blue);font-size:.72rem;font-weight:700}
</style>""",unsafe_allow_html=True)
init_db()
with SessionLocal() as s:
    if s.scalar(select(func.count(JobPosting.id))) == 0: seed_demo(s)

def rows_to_df(jobs):
    return pd.DataFrame([{"id":j.id,"title":j.title,"company":j.company.name,"description":j.description,"location":j.location,"employment_type":j.employment_type,"experience_level":j.experience_level,"education":j.education,"salary":j.salary,"posted_date":j.posted_date,"deadline":j.deadline,"source_url":j.source_url,"source_name":j.source_name,"is_demo":j.is_demo,"category":j.category,"skills":", ".join(x.skill.name for x in j.skills)} for j in jobs])

def get_filtered(s, filters=True):
    jobs=s.scalars(select(JobPosting).order_by(JobPosting.posted_date.desc().nullslast(),JobPosting.id.desc())).all()
    df=rows_to_df(jobs)
    if df.empty:return df
    if filters:
        with st.sidebar:
            st.markdown("#### Filters")
            cats=sorted(df.category.dropna().unique()); cat=st.multiselect("Category",cats,default=cats,key="cat_filter")
            locs=sorted(df.location.dropna().unique()); loc=st.multiselect("Location",locs,default=locs,key="loc_filter")
            exps=sorted(df.experience_level.dropna().unique()); exp=st.multiselect("Experience",exps,default=exps,key="exp_filter")
            types=sorted(df.employment_type.dropna().unique()); typ=st.multiselect("Employment type",types,default=types,key="type_filter")
            realdemo=st.radio("Data set",["All records","Real only","Demo only"],horizontal=False)
            dates=pd.to_datetime(df.posted_date,errors="coerce").dropna()
            date_range=None
            if not dates.empty:
                dr=st.date_input("Posting dates",(dates.min().date(),dates.max().date()),key="date_filter")
                if isinstance(dr,tuple) and len(dr)==2: date_range=dr
        if cat:df=df[df.category.isin(cat)]
        if loc:df=df[df.location.isin(loc)]
        if exp:df=df[df.experience_level.isin(exp)]
        if typ:df=df[df.employment_type.isin(typ)]
        if realdemo=="Real only":df=df[~df.is_demo]
        if realdemo=="Demo only":df=df[df.is_demo]
        if date_range:
            dt=pd.to_datetime(df.posted_date,errors="coerce").dt.date
            df=df[dt.between(date_range[0],date_range[1]) | dt.isna()]
    return df

def title_block(section, title, desc):
    st.markdown(f'<div class="eyebrow">{section}</div>',unsafe_allow_html=True);st.title(title);st.markdown(f'<div class="subtle">{desc}</div>',unsafe_allow_html=True);st.write("")

with st.sidebar:
    st.markdown("# JobLens BD")
    st.caption("Bangla Job Market Intelligence")
    page=st.radio("Navigate",["Overview","Job Explorer","Skill Intelligence","Data Ingestion","Pipeline Monitor","Data Quality"],label_visibility="collapsed")
    st.divider()
    st.caption(f"Database · {engine.dialect.name.upper()}")
    st.caption("Connected" if engine else "Disconnected")
    st.caption("Understanding Bangladesh's evolving job market through data.")

with SessionLocal() as session:
    df=get_filtered(session, page in ["Overview","Skill Intelligence"])
    demo_count=int(df.is_demo.sum()) if not df.empty else 0
    if demo_count: st.info(f"Demo mode: {demo_count} synthetic posting(s) are included in this view. They are clearly labelled and are not real market observations.")
    if page=="Overview":
        title_block("Market snapshot","Overview","A live view of the records currently stored in your JobLens database.")
        if df.empty: st.info("No postings match these filters. Adjust filters or import job data.")
        else:
            a,b,c,d=st.columns(4);a.metric("Job postings",f"{len(df):,}");b.metric("Companies",f"{df.company.nunique():,}");c.metric("Categories",f"{df.category.nunique():,}");d.metric("Skills identified",f"{sum(len(str(x).split(', ')) for x in df.skills if x):,}")
            l,r=st.columns(2)
            with l:
                counts=df.explode("skills").query("skills != ''").groupby("skills").size().sort_values(ascending=False).head(10).sort_values()
                st.subheader("Most demanded skills"); st.plotly_chart(px.bar(counts,x=counts.values,y=counts.index,orientation="h",labels={"x":"Unique job postings","y":"Skill"},color_discrete_sequence=["#465fff"]),use_container_width=True)
            with r:
                st.subheader("Job categories"); cats=df.groupby("category").size().reset_index(name="Postings")
                st.plotly_chart(px.pie(cats,names="category",values="Postings",hole=.66,color_discrete_sequence=px.colors.qualitative.Pastel),use_container_width=True)
            l,r=st.columns(2)
            with l: st.subheader("Location distribution");st.plotly_chart(px.bar(df.location.value_counts().head(10).sort_values(),orientation="h",labels={"value":"Postings","index":"Location"},color_discrete_sequence=["#7283ff"]),use_container_width=True)
            with r: st.subheader("Experience requirements");st.plotly_chart(px.histogram(df,x="experience_level",color_discrete_sequence=["#465fff"],labels={"experience_level":"Experience level","count":"Postings"}),use_container_width=True)
            dated=df.dropna(subset=["posted_date"])
            if dated.posted_date.nunique()>1:
                st.subheader("Posting trend by month"); dated=dated.copy();dated["month"]=pd.to_datetime(dated.posted_date).dt.to_period("M").astype(str);st.plotly_chart(px.line(dated.groupby("month").size().reset_index(name="Postings"),x="month",y="Postings",markers=True),use_container_width=True)
            st.subheader("Recently collected");st.dataframe(df.sort_values("posted_date",ascending=False).head(8)[["title","company","location","category","posted_date","is_demo"]],use_container_width=True,hide_index=True)
    elif page=="Job Explorer":
        title_block("Records","Job Explorer","Search, filter and inspect individual job postings.")
        all_df=get_filtered(session,False)
        q=st.text_input("Search titles, companies, descriptions and extracted skills",placeholder="e.g. Python, data analyst, Dhaka")
        c1,c2,c3=st.columns(3); company=c1.selectbox("Company",["All"]+sorted(all_df.company.unique().tolist()) if not all_df.empty else ["All"]); category=c2.selectbox("Category",["All"]+sorted(all_df.category.unique().tolist()) if not all_df.empty else ["All"]);location=c3.selectbox("Location",["All"]+sorted(all_df.location.unique().tolist()) if not all_df.empty else ["All"])
        if not all_df.empty:
            if company!="All":all_df=all_df[all_df.company==company]
            if category!="All":all_df=all_df[all_df.category==category]
            if location!="All":all_df=all_df[all_df.location==location]
            if q:all_df=all_df[all_df[["title","company","description","skills"]].fillna("").agg(" ".join,axis=1).str.contains(q,case=False,regex=False)]
            sort=st.selectbox("Sort by",["Newest first","Title A–Z","Company A–Z"])
            if sort=="Title A–Z":all_df=all_df.sort_values("title")
            elif sort=="Company A–Z":all_df=all_df.sort_values("company")
            page_no=st.number_input("Page",min_value=1,max_value=max(1,(len(all_df)+19)//20),step=1);start=(page_no-1)*20;chunk=all_df.iloc[start:start+20]
            st.caption(f"Showing {start+1 if len(all_df) else 0}–{start+len(chunk)} of {len(all_df)} postings")
            for _,row in chunk.iterrows():
                with st.expander(f"{row.title} · {row.company} · {row.location}"+(" · DEMO" if row.is_demo else "")):
                    st.markdown(f"**Category:** {row.category} · **Experience:** {row.experience_level} · **Type:** {row.employment_type}")
                    st.markdown(f"**Skills:** {row.skills or 'None identified'} · **Education:** {row.education} · **Salary:** {row.salary}")
                    st.write(row.description);st.caption(f"Posted {row.posted_date or 'date unavailable'} · Deadline {row.deadline or 'not listed'} · Source: {row.source_name}")
                    st.link_button("Open source posting",row.source_url)
            st.download_button("Export filtered results as CSV",all_df.to_csv(index=False).encode("utf-8-sig"),"joblens_postings.csv","text/csv")
        else: st.info("No postings yet.")
    elif page=="Skill Intelligence":
        title_block("Demand analysis","Skill Intelligence","Explore skill frequency across postings, categories and experience levels.")
        if df.empty:st.info("No postings match the selected filters.")
        else:
            exploded=df.assign(skill_list=df.skills.str.split(", ")).explode("skill_list").rename(columns={"skill_list":"skill"});exploded=exploded[exploded.skill.fillna("")!=""]
            st.caption("Counts represent unique postings containing a skill, not the number of times a word appears in a description.")
            l,r=st.columns(2)
            with l:
                st.subheader("Skill frequency");freq=exploded.groupby("skill").id.nunique().sort_values(ascending=False).head(20).sort_values();st.plotly_chart(px.bar(freq,x=freq.values,y=freq.index,orientation="h",labels={"x":"Postings","y":"Skill"},color_discrete_sequence=["#465fff"]),use_container_width=True)
            with r:
                st.subheader("Skills by category");top=exploded.groupby(["category","skill"]).id.nunique().reset_index(name="Postings");st.plotly_chart(px.density_heatmap(top,x="skill",y="category",z="Postings",histfunc="sum",color_continuous_scale="Blues"),use_container_width=True)
            st.subheader("Skills by experience level");byexp=exploded.groupby(["experience_level","skill"]).id.nunique().reset_index(name="Postings");topskills=exploded.groupby("skill").id.nunique().nlargest(12).index;st.plotly_chart(px.bar(byexp[byexp.skill.isin(topskills)],x="skill",y="Postings",color="experience_level",barmode="group"),use_container_width=True)
            co={}
            for skills in df.skills:
                ss=sorted(set(x for x in str(skills).split(", ") if x))
                for i,x in enumerate(ss):
                    for y in ss[i+1:]:co[(x,y)]=co.get((x,y),0)+1
            st.subheader("Skills appearing together");pairs=sorted(co.items(),key=lambda x:x[1],reverse=True)[:10]
            st.dataframe(pd.DataFrame([{"Skill A":k[0],"Skill B":k[1],"Postings together":v} for k,v in pairs]),use_container_width=True,hide_index=True)
            st.download_button("Export skill counts",exploded.groupby("skill").id.nunique().rename("postings").reset_index().to_csv(index=False),"skill_demand.csv","text/csv")
    elif page=="Data Ingestion":
        title_block("Bring in data","Data Ingestion","Upload a CSV or add a posting manually. Source URLs are required for reliable duplicate detection.")
        st.download_button("Download CSV template",Path(__file__).parent.joinpath("data/templates/jobs_template.csv").read_bytes(),"jobs_template.csv","text/csv")
        tab1,tab2=st.tabs(["CSV upload","Manual entry"])
        with tab1:
            file=st.file_uploader("Choose a CSV file",type=["csv"])
            if file:
                try:
                    uploaded=pd.read_csv(file).fillna("");st.dataframe(uploaded.head(10),use_container_width=True)
                    if st.button("Run ETL pipeline",type="primary"):
                        with st.spinner("Validating, enriching and loading records…"):
                            result=run_pipeline(session,uploaded.to_dict("records"))
                        st.success(f"Processed {result['processed']}: {result['successful']} loaded, {result['rejected']} rejected, {result['duplicates']} duplicates · {result['duration_seconds']:.2f}s")
                        if result["errors"]:st.error("\n".join(result["errors"][:12]))
                except Exception as e:st.error(f"Could not read CSV: {e}")
        with tab2:
            with st.form("manual_entry"):
                c1,c2=st.columns(2);title=c1.text_input("Job title*");company=c2.text_input("Company*");loc=c1.text_input("Location",value="Dhaka");etype=c2.selectbox("Employment type",["Full-time","Part-time","Contract","Internship","Not specified"]);url=st.text_input("Source URL*");desc=st.text_area("Job description");posted=st.date_input("Posting date")
                submit=st.form_submit_button("Validate and save")
            if submit:
                result=run_pipeline(session,[{"title":title,"company":company,"location":loc,"employment_type":etype,"source_url":url,"description":desc,"posted_date":str(posted),"source_name":"Manual entry","is_demo":False}])
                if result["successful"]:st.success("Posting saved and indexed.")
                else:st.error("Posting rejected or already present. " + "; ".join(result["errors"]))
        st.markdown("#### Source connector guidance");st.caption("Optional feeds and APIs can be added in ingestion/source_connectors.py. Use only public endpoints that permit access; this app does not bypass access controls or website policies.")
    elif page=="Pipeline Monitor":
        title_block("Operations","Pipeline Monitor","Execution history and record-level outcomes from ETL runs.")
        runs=session.scalars(select(PipelineRun).order_by(PipelineRun.started_at.desc()).limit(100)).all()
        if not runs:st.info("No pipeline runs yet. Upload a CSV or add a manual record to create a run.")
        else:
            rdf=pd.DataFrame([{"Run":r.id,"Started":r.started_at,"Status":r.status,"Processed":r.processed,"Loaded":r.successful,"Rejected":r.rejected,"Duplicates":r.duplicates,"Duration (s)":round(r.duration_seconds,3),"Details":r.details} for r in runs]);st.dataframe(rdf,use_container_width=True,hide_index=True)
            selected=st.selectbox("Inspect run",[r.id for r in runs]);chosen=next(r for r in runs if r.id==selected)
            if chosen.details:st.error(chosen.details)
            else:st.success("This run completed without rejected records.")
    elif page=="Data Quality":
        title_block("Trust & completeness","Data Quality","Transparent checks across all records, including records outside dashboard filters.")
        jobs=session.scalars(select(JobPosting)).all();qdf=rows_to_df(jobs)
        if qdf.empty:st.info("No postings available for quality checks.")
        else:
            fields=["title","company","description","location","employment_type","experience_level","source_url","posted_date"]
            completeness={f:float(qdf[f].notna().astype(int).mean() if f not in ["posted_date"] else qdf[f].notna().mean()) for f in fields}
            miss=1-sum(completeness.values())/len(fields);dupes=int(qdf.source_url.duplicated(keep=False).sum());invalid=int((~qdf.source_url.fillna("").str.match(r"^https?://[^\s]+$",case=False)).sum());empty=int(qdf.description.fillna("").str.strip().eq("").sum());invalid_date=int(pd.to_datetime(qdf.posted_date,errors="coerce").isna().sum())
            score=max(0,100*(1-miss)*(1-min(dupes/max(1,len(qdf)),1))*(1-min(invalid/max(1,len(qdf)),1)))
            a,b,c,d=st.columns(4);a.metric("Quality score",f"{score:.1f}/100",help="100 × field completeness × (1 − duplicate rate) × (1 − invalid URL rate)");b.metric("Missing field rate",f"{miss:.1%}");c.metric("Duplicate rows",dupes);d.metric("Validation issues",invalid+empty+invalid_date)
            st.subheader("Field completeness");st.plotly_chart(px.bar(pd.DataFrame({"Field":completeness.keys(),"Complete":list(completeness.values())}),x="Field",y="Complete",range_y=[0,1],color_discrete_sequence=["#465fff"]),use_container_width=True)
            issues=qdf[(~qdf.source_url.fillna("").str.match(r"^https?://[^\s]+$",case=False)) | qdf.description.fillna("").str.strip().eq("") | pd.to_datetime(qdf.posted_date,errors="coerce").isna() | qdf.source_url.duplicated(keep=False)]
            st.subheader(f"Records to inspect ({len(issues)})");st.dataframe(issues[["id","title","company","source_url","posted_date","description","is_demo"]],use_container_width=True,hide_index=True)
            with st.expander("Remove synthetic demo records"):
                st.caption("This permanently removes records marked DEMO and their associated skill links.")
                if st.button("Delete all demo records",type="secondary"):
                    from database.models import JobSkill
                    ids=list(session.scalars(select(JobPosting.id).where(JobPosting.is_demo.is_(True))).all())
                    if ids:session.execute(delete(JobSkill).where(JobSkill.job_id.in_(ids)));session.execute(delete(JobPosting).where(JobPosting.is_demo.is_(True)));session.commit()
                    st.success(f"Deleted {len(ids)} demo postings.");st.rerun()
