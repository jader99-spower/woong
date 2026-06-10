import streamlit as st
import pandas as pd
import numpy as np
import os
import google.generativeai as genai

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="친환경 발전소 운전실적 분석", layout="wide", page_icon="🌿")

HERO_HTML = """
<style>
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #071422 0%, #0a1e30 100%);
    border-right: 1px solid rgba(46,204,113,0.15);
}
.stTabs [data-baseweb="tab-list"] {
    background-color: rgba(255,255,255,0.04);
    border-radius: 10px;
    gap: 4px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    color: rgba(200,230,210,0.7);
    border-radius: 8px;
    padding: 6px 16px;
}
.stTabs [aria-selected="true"] {
    background-color: rgba(46,204,113,0.2) !important;
    color: #4ade80 !important;
}
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(46,204,113,0.15);
    border-radius: 10px;
    padding: 8px;
}
</style>

<div style="width:100%;border-radius:14px;overflow:hidden;margin-bottom:18px;box-shadow:0 8px 40px rgba(0,0,0,0.6);">
<svg viewBox="0 0 1400 300" xmlns="http://www.w3.org/2000/svg" style="width:100%;display:block;">
  <defs>
    <linearGradient id="skyG" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#020c18"/>
      <stop offset="45%" stop-color="#08244a"/>
      <stop offset="78%" stop-color="#0e4a72"/>
      <stop offset="100%" stop-color="#1a6a8a"/>
    </linearGradient>
    <radialGradient id="sunHalo" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#ffe45a" stop-opacity="0.55"/>
      <stop offset="40%"  stop-color="#ff9a20" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="#ff6a00" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="sunCore" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#ffffff"/>
      <stop offset="30%"  stop-color="#ffe566"/>
      <stop offset="100%" stop-color="#ffb020"/>
    </radialGradient>
    <linearGradient id="hillBack" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#143824"/>
      <stop offset="100%" stop-color="#091a10"/>
    </linearGradient>
    <linearGradient id="hillMid" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0d2e1c"/>
      <stop offset="100%" stop-color="#061208"/>
    </linearGradient>
    <linearGradient id="hillFront" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0a2416"/>
      <stop offset="100%" stop-color="#040e08"/>
    </linearGradient>
    <linearGradient id="solarPanel" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%"   stop-color="#1a3d72"/>
      <stop offset="50%"  stop-color="#2a5faa"/>
      <stop offset="100%" stop-color="#1a3d72"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2.5" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="txtGlow" x="-10%" y="-30%" width="120%" height="160%">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <!-- Sky -->
  <rect width="1400" height="300" fill="url(#skyG)"/>

  <!-- Stars -->
  <circle cx="80"  cy="22" r="1.4" fill="white" opacity="0.8"/>
  <circle cx="180" cy="14" r="1.0" fill="white" opacity="0.6"/>
  <circle cx="310" cy="38" r="1.4" fill="white" opacity="0.7"/>
  <circle cx="460" cy="12" r="1.0" fill="white" opacity="0.5"/>
  <circle cx="560" cy="30" r="1.2" fill="white" opacity="0.7"/>
  <circle cx="680" cy="10" r="1.0" fill="white" opacity="0.5"/>
  <circle cx="820" cy="25" r="1.4" fill="white" opacity="0.8"/>
  <circle cx="970" cy="16" r="1.0" fill="white" opacity="0.6"/>
  <circle cx="1080" cy="36" r="1.2" fill="white" opacity="0.7"/>
  <circle cx="1230" cy="20" r="1.4" fill="white" opacity="0.8"/>
  <circle cx="1360" cy="42" r="1.0" fill="white" opacity="0.5"/>
  <circle cx="40"  cy="50" r="1.0" fill="white" opacity="0.4"/>
  <circle cx="420" cy="44" r="1.0" fill="white" opacity="0.5"/>
  <circle cx="740" cy="48" r="1.0" fill="white" opacity="0.4"/>
  <circle cx="1160" cy="52" r="1.0" fill="white" opacity="0.5"/>

  <!-- Sun halo -->
  <circle cx="700" cy="222" r="110" fill="url(#sunHalo)"/>
  <!-- Sun rays -->
  <g transform="translate(700,222)" opacity="0.45" filter="url(#glow)">
    <line x1="0" y1="-68" x2="0"   y2="-88"  stroke="#ffe566" stroke-width="2"/>
    <line x1="48" y1="-48" x2="61" y2="-61"  stroke="#ffe566" stroke-width="2"/>
    <line x1="68" y1="0"   x2="88" y2="0"    stroke="#ffe566" stroke-width="2"/>
    <line x1="48" y1="48"  x2="61" y2="61"   stroke="#ffe566" stroke-width="2"/>
    <line x1="-48" y1="-48" x2="-61" y2="-61" stroke="#ffe566" stroke-width="2"/>
    <line x1="-68" y1="0"   x2="-88" y2="0"   stroke="#ffe566" stroke-width="2"/>
    <line x1="-48" y1="48"  x2="-61" y2="61"  stroke="#ffe566" stroke-width="2"/>
    <line x1="0"  y1="68"   x2="0"   y2="88"  stroke="#ffe566" stroke-width="2"/>
  </g>
  <!-- Sun core -->
  <circle cx="700" cy="222" r="32" fill="url(#sunCore)" opacity="0.92"/>

  <!-- Clouds -->
  <g opacity="0.12">
    <ellipse cx="250" cy="68" rx="55" ry="18" fill="white"/>
    <ellipse cx="285" cy="59" rx="38" ry="14" fill="white"/>
    <ellipse cx="218" cy="63" rx="30" ry="12" fill="white"/>
  </g>
  <g opacity="0.10">
    <ellipse cx="1120" cy="55" rx="60" ry="19" fill="white"/>
    <ellipse cx="1155" cy="47" rx="40" ry="15" fill="white"/>
    <ellipse cx="1082" cy="52" rx="32" ry="13" fill="white"/>
  </g>

  <!-- Back mountain silhouettes -->
  <path d="M0,235 Q180,195 360,218 Q520,238 680,210 Q840,188 1000,208 Q1150,225 1400,205 L1400,300 L0,300 Z"
        fill="#0a1f12" opacity="0.7"/>

  <!-- ── WIND TURBINES ── -->
  <!-- Turbine 1 (x=155, hub y=148) -->
  <line x1="155" y1="275" x2="155" y2="148" stroke="#bbc8d4" stroke-width="5" stroke-linecap="round"/>
  <circle cx="155" cy="148" r="7" fill="#ccd6e0"/>
  <g filter="url(#glow)">
    <animateTransform attributeName="transform" attributeType="XML"
      type="rotate" from="0 155 148" to="360 155 148" dur="8s" repeatCount="indefinite"/>
    <line x1="155" y1="148" x2="155" y2="94"  stroke="#deeaf4" stroke-width="4.5" stroke-linecap="round"/>
    <line x1="155" y1="148" x2="202" y2="175" stroke="#deeaf4" stroke-width="4.5" stroke-linecap="round"/>
    <line x1="155" y1="148" x2="108" y2="175" stroke="#deeaf4" stroke-width="4.5" stroke-linecap="round"/>
  </g>

  <!-- Turbine 2 (x=330, hub y=165) -->
  <line x1="330" y1="275" x2="330" y2="165" stroke="#bbc8d4" stroke-width="4" stroke-linecap="round"/>
  <circle cx="330" cy="165" r="5" fill="#ccd6e0"/>
  <g filter="url(#glow)">
    <animateTransform attributeName="transform" attributeType="XML"
      type="rotate" from="120 330 165" to="480 330 165" dur="6s" repeatCount="indefinite"/>
    <line x1="330" y1="165" x2="330" y2="121" stroke="#deeaf4" stroke-width="3.5" stroke-linecap="round"/>
    <line x1="330" y1="165" x2="368" y2="187" stroke="#deeaf4" stroke-width="3.5" stroke-linecap="round"/>
    <line x1="330" y1="165" x2="292" y2="187" stroke="#deeaf4" stroke-width="3.5" stroke-linecap="round"/>
  </g>

  <!-- Turbine 3 (x=1060, hub y=145) -->
  <line x1="1060" y1="275" x2="1060" y2="145" stroke="#bbc8d4" stroke-width="5" stroke-linecap="round"/>
  <circle cx="1060" cy="145" r="7" fill="#ccd6e0"/>
  <g filter="url(#glow)">
    <animateTransform attributeName="transform" attributeType="XML"
      type="rotate" from="240 1060 145" to="600 1060 145" dur="7s" repeatCount="indefinite"/>
    <line x1="1060" y1="145" x2="1060" y2="90"  stroke="#deeaf4" stroke-width="4.5" stroke-linecap="round"/>
    <line x1="1060" y1="145" x2="1108" y2="173" stroke="#deeaf4" stroke-width="4.5" stroke-linecap="round"/>
    <line x1="1060" y1="145" x2="1012" y2="173" stroke="#deeaf4" stroke-width="4.5" stroke-linecap="round"/>
  </g>

  <!-- Turbine 4 (x=1245, hub y=162) -->
  <line x1="1245" y1="275" x2="1245" y2="162" stroke="#bbc8d4" stroke-width="4" stroke-linecap="round"/>
  <circle cx="1245" cy="162" r="5" fill="#ccd6e0"/>
  <g filter="url(#glow)">
    <animateTransform attributeName="transform" attributeType="XML"
      type="rotate" from="60 1245 162" to="420 1245 162" dur="9s" repeatCount="indefinite"/>
    <line x1="1245" y1="162" x2="1245" y2="118" stroke="#deeaf4" stroke-width="3.5" stroke-linecap="round"/>
    <line x1="1245" y1="162" x2="1283" y2="184" stroke="#deeaf4" stroke-width="3.5" stroke-linecap="round"/>
    <line x1="1245" y1="162" x2="1207" y2="184" stroke="#deeaf4" stroke-width="3.5" stroke-linecap="round"/>
  </g>

  <!-- Mid hills -->
  <path d="M0,260 Q200,242 420,255 Q600,268 760,250 Q920,235 1100,252 Q1280,265 1400,256 L1400,300 L0,300 Z"
        fill="url(#hillMid)"/>

  <!-- SOLAR PANEL FARM (right center area) -->
  <g transform="translate(580,252)" opacity="0.88">
    <rect x="0"  y="-14" width="32" height="20" rx="2" fill="url(#solarPanel)" stroke="#3a6aaa" stroke-width="0.8"/>
    <rect x="35" y="-16" width="32" height="20" rx="2" fill="url(#solarPanel)" stroke="#3a6aaa" stroke-width="0.8"/>
    <rect x="70" y="-18" width="32" height="20" rx="2" fill="url(#solarPanel)" stroke="#3a6aaa" stroke-width="0.8"/>
    <rect x="105" y="-20" width="32" height="20" rx="2" fill="url(#solarPanel)" stroke="#3a6aaa" stroke-width="0.8"/>
    <rect x="5"  y="9"  width="32" height="20" rx="2" fill="url(#solarPanel)" stroke="#3a6aaa" stroke-width="0.8"/>
    <rect x="40" y="7"  width="32" height="20" rx="2" fill="url(#solarPanel)" stroke="#3a6aaa" stroke-width="0.8"/>
    <rect x="75" y="5"  width="32" height="20" rx="2" fill="url(#solarPanel)" stroke="#3a6aaa" stroke-width="0.8"/>
    <rect x="110" y="3" width="32" height="20" rx="2" fill="url(#solarPanel)" stroke="#3a6aaa" stroke-width="0.8"/>
    <!-- Panel grid lines -->
    <line x1="16" y1="-14" x2="16" y2="6"  stroke="#2a5a9a" stroke-width="0.6" opacity="0.6"/>
    <line x1="0"  y1="-4"  x2="32" y2="-4" stroke="#2a5a9a" stroke-width="0.6" opacity="0.6"/>
    <line x1="51" y1="-16" x2="51" y2="4"  stroke="#2a5a9a" stroke-width="0.6" opacity="0.6"/>
    <line x1="35" y1="-6"  x2="67" y2="-6" stroke="#2a5a9a" stroke-width="0.6" opacity="0.6"/>
    <!-- Shine reflection -->
    <rect x="2"  y="-12" width="9" height="5" rx="1" fill="white" opacity="0.18"/>
    <rect x="37" y="-14" width="9" height="5" rx="1" fill="white" opacity="0.18"/>
    <rect x="72" y="-16" width="9" height="5" rx="1" fill="white" opacity="0.18"/>
    <rect x="107" y="-18" width="9" height="5" rx="1" fill="white" opacity="0.18"/>
  </g>

  <!-- Front hills -->
  <path d="M0,278 Q250,265 500,275 Q700,284 900,268 Q1100,256 1300,272 Q1360,278 1400,274 L1400,300 L0,300 Z"
        fill="url(#hillFront)"/>

  <!-- Subtle horizon glow -->
  <rect x="0" y="200" width="1400" height="30" fill="url(#sunHalo)" opacity="0.2"/>

  <!-- Title text -->
  <text x="700" y="136" text-anchor="middle" fill="white" font-size="26" font-weight="bold"
        font-family="'Segoe UI', Arial, sans-serif" filter="url(#txtGlow)" letter-spacing="3">
    ⚡ 친환경 발전소 운전실적 분석 대시보드
  </text>
  <text x="700" y="168" text-anchor="middle" fill="#7ee8a8" font-size="13"
        font-family="'Segoe UI', Arial, sans-serif" letter-spacing="2" opacity="0.9">
    태양광 · 풍력 신재생에너지 — GEN_001 · 2023년
  </text>
  <!-- Accent line -->
  <line x1="520" y1="182" x2="880" y2="182" stroke="#2ecc71" stroke-width="1" opacity="0.45"/>
</svg>
</div>
"""

st.markdown(HERO_HTML, unsafe_allow_html=True)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ── 데이터 로딩 ──────────────────────────────────────────────────────────────

@st.cache_data
def load_basic():
    df = pd.read_csv(f"{DATA_DIR}/발전기_기본정보.csv", encoding="utf-8-sig")
    return df

@st.cache_data
def load_daily():
    df = pd.read_csv(f"{DATA_DIR}/일일_발전량.csv", encoding="utf-8-sig", parse_dates=["날짜"])
    df["월"] = df["날짜"].dt.month
    df["분기"] = df["날짜"].dt.quarter.map({1: "Q1", 2: "Q2", 3: "Q3", 4: "Q4"})
    return df

@st.cache_data
def load_weekly_eff():
    df = pd.read_csv(f"{DATA_DIR}/효율_분석.csv", encoding="utf-8-sig", parse_dates=["주차"])
    df["월"] = df["주차"].dt.month
    return df

@st.cache_data
def load_hourly():
    df = pd.read_csv(f"{DATA_DIR}/시간별_성능.csv", encoding="utf-8-sig", parse_dates=["시간"])
    return df.iloc[::6].reset_index(drop=True)  # 6행마다 1행 샘플링 (~7,300행)

@st.cache_data
def load_temp():
    df = pd.read_csv(f"{DATA_DIR}/온도_특성.csv", encoding="utf-8-sig", parse_dates=["날짜"])
    df["월"] = df["날짜"].dt.month
    return df

df_basic   = load_basic()
df_daily   = load_daily()
df_weekly  = load_weekly_eff()
df_hourly  = load_hourly()
df_temp    = load_temp()

# ── 사이드바 필터 ─────────────────────────────────────────────────────────────

GEN_ID = "GEN_001"

with st.sidebar:
    st.title("⚙️ 필터")
    st.info(f"발전기: {GEN_ID}")

    period_opt = st.selectbox("기간 선택", ["전체", "상반기(1~6월)", "하반기(7~12월)", "분기 선택"])
    sel_quarter = None
    if period_opt == "분기 선택":
        sel_quarter = st.selectbox("분기", ["Q1", "Q2", "Q3", "Q4"])

    st.divider()
    st.info("데이터 기준: 2023년")

# 필터 적용 (GEN_001 고정)
df_daily_f = df_daily[df_daily["발전기ID"] == GEN_ID].copy()
if period_opt == "상반기(1~6월)":
    df_daily_f = df_daily_f[df_daily_f["월"] <= 6]
elif period_opt == "하반기(7~12월)":
    df_daily_f = df_daily_f[df_daily_f["월"] >= 7]
elif period_opt == "분기 선택" and sel_quarter:
    df_daily_f = df_daily_f[df_daily_f["분기"] == sel_quarter]

df_eff_f = df_weekly[df_weekly["발전기ID"] == GEN_ID].copy()
if period_opt == "상반기(1~6월)":
    df_eff_f = df_eff_f[df_eff_f["월"] <= 6]
elif period_opt == "하반기(7~12월)":
    df_eff_f = df_eff_f[df_eff_f["월"] >= 7]
elif period_opt == "분기 선택" and sel_quarter:
    q_months = {"Q1": [1,2,3], "Q2": [4,5,6], "Q3": [7,8,9], "Q4": [10,11,12]}
    df_eff_f = df_eff_f[df_eff_f["월"].isin(q_months[sel_quarter])]

df_hourly_f = df_hourly[df_hourly["발전기ID"] == GEN_ID].copy()

# ── 탭 ───────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🌱 운전 실적 요약", "⚡ 출력 분석", "🍃 효율 분석", "🌬️ 온도-성능 상관관계", "🤖 AI 데이터 분석"])

# ════════════════════════════════════════════════════════════════════════════
# Tab 1 — 운전 실적 요약
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("운전 실적 요약")

    if df_daily_f.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    else:
        total_power   = df_daily_f["발전량(MWh)"].sum()
        avg_eff       = df_daily_f["평균효율(%)"].mean()
        avg_op_hours  = df_daily_f["가동시간(h)"].mean()
        util_rate     = df_daily_f["가동시간(h)"].sum() / (len(df_daily_f) * 24) * 100

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("총 발전량 (MWh)", f"{total_power:,.0f}")
        c2.metric("평균 효율 (%)", f"{avg_eff:.2f}")
        c3.metric("평균 가동시간 (h/일)", f"{avg_op_hours:.1f}")
        c4.metric("설비이용률 (%)", f"{util_rate:.1f}")

        st.divider()

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**월별 발전량**")
            monthly_sum = df_daily_f.groupby("월")["발전량(MWh)"].sum().rename("발전량(MWh)")
            st.bar_chart(monthly_sum, use_container_width=True)

        with col_b:
            st.markdown("**일별 가동시간 추이**")
            daily_op = df_daily_f.set_index("날짜")["가동시간(h)"]
            st.line_chart(daily_op, use_container_width=True)

        st.divider()
        st.markdown("**발전기 기본 정보**")
        st.dataframe(
            df_basic[df_basic["발전기ID"] == GEN_ID][["발전기ID", "설치위치", "제조사", "모델명", "정격용량(MW)", "설치년도", "연간운영시간(h)"]],
            use_container_width=True,
            hide_index=True,
        )

# ════════════════════════════════════════════════════════════════════════════
# Tab 2 — 출력 분석
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("출력 분석")

    if df_daily_f.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    else:
        st.markdown("**일별 발전량 추이**")
        daily_series = df_daily_f.set_index("날짜")["발전량(MWh)"]
        st.line_chart(daily_series, use_container_width=True)

        st.divider()
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**월별 평균 발전량**")
            monthly_avg = df_daily_f.groupby("월")["발전량(MWh)"].mean().rename("발전량(MWh)")
            st.bar_chart(monthly_avg, use_container_width=True)

        with col_b:
            st.markdown("**분기별 발전량 누적**")
            qtr_sum = df_daily_f.groupby("분기")["발전량(MWh)"].sum().rename("발전량(MWh)")
            qtr_sum = qtr_sum.reindex([q for q in ["Q1","Q2","Q3","Q4"] if q in qtr_sum.index])
            st.area_chart(qtr_sum, use_container_width=True)

        st.divider()
        st.markdown("**출력 요약**")
        summary = pd.DataFrame([{
            "발전기ID": GEN_ID,
            "총발전량(MWh)": round(df_daily_f["발전량(MWh)"].sum(), 2),
            "최대일간발전량(MWh)": round(df_daily_f["발전량(MWh)"].max(), 2),
            "평균발전량(MWh)": round(df_daily_f["발전량(MWh)"].mean(), 2),
            "평균가동시간(h)": round(df_daily_f["가동시간(h)"].mean(), 2),
        }])
        st.dataframe(summary, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════════════════
# Tab 3 — 효율 분석
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("효율 분석")

    if df_eff_f.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    else:
        avg_eff_val   = df_eff_f["평균효율(%)"].mean()
        achieve_rate  = avg_eff_val / 52.0 * 100
        best_week_row = df_eff_f.loc[df_eff_f["평균효율(%)"].idxmax()]
        best_week_str = best_week_row["주차"].strftime("%Y-%m-%d") if pd.notna(best_week_row["주차"]) else "-"

        c1, c2, c3 = st.columns(3)
        c1.metric("연간 평균 효율 (%)", f"{avg_eff_val:.2f}")
        c2.metric("목표 대비 달성율 (%)", f"{achieve_rate:.1f}")
        c3.metric("최고 효율 달성 주차", best_week_str)

        st.divider()

        st.markdown("**주간 평균효율 추이 (목표: 52%)**")
        eff_weekly = df_eff_f.set_index("주차")[["평균효율(%)"]].copy()
        eff_weekly["목표(52%)"] = 52.0
        st.line_chart(eff_weekly, use_container_width=True)

        st.divider()
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**월별 목표효율 달성율 (%)**")
            monthly_achieve_rate = (
                df_daily_f.groupby("월")["평균효율(%)"].mean() / 52.0 * 100
            ).round(2).rename("달성율(%)")
            st.bar_chart(monthly_achieve_rate, use_container_width=True)

        with col_b:
            st.markdown("**효율 범위 (최고 / 평균 / 최저)**")
            eff_range = df_eff_f.groupby("주차").agg(
                최고효율=("최고효율(%)", "mean"),
                평균효율=("평균효율(%)", "mean"),
                최저효율=("최저효율(%)", "mean"),
            )
            st.line_chart(eff_range, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# Tab 4 — 온도-성능 상관관계
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("온도-성능 상관관계")

    if df_hourly_f.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    else:
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**외기온도 vs 전력출력**")
            st.caption("저온일수록 출력 증가 | 기준: 15°C → 835MW / 40°C → 730MW / -16°C → 890MW")
            st.scatter_chart(
                df_hourly_f,
                x="외기온도(°C)",
                y="전력출력(MW)",
                use_container_width=True,
            )

        with col_b:
            st.markdown("**외기온도 vs 효율**")
            st.caption("15°C 부근에서 최고 효율 53% | 온도 이탈 시 최저 49%까지 감소")
            st.scatter_chart(
                df_hourly_f,
                x="외기온도(°C)",
                y="효율(%)",
                use_container_width=True,
            )

        st.divider()
        col_c, col_d = st.columns(2)

        with col_c:
            st.markdown("**월별 평균 외기온도**")
            monthly_temp = df_temp.groupby("월")["외기온도(°C)"].mean().rename("평균 외기온도(°C)")
            st.line_chart(monthly_temp, use_container_width=True)

        with col_d:
            st.markdown("**온도 구간별 평균 효율**")
            df_temp_eff = df_daily_f.copy()
            df_temp_eff["온도구간"] = pd.cut(
                df_temp_eff["평균외기온도(°C)"],
                bins=[-20, -10, 0, 10, 20, 30, 40],
                labels=["-20~-10", "-10~0", "0~10", "10~20", "20~30", "30~40"],
            ).astype(str)
            temp_eff_avg = (
                df_temp_eff.groupby("온도구간")["평균효율(%)"]
                .mean()
                .reindex(["-20~-10", "-10~0", "0~10", "10~20", "20~30", "30~40"])
                .dropna()
                .rename("평균효율(%)")
            )
            st.bar_chart(temp_eff_avg, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# Tab 5 — AI 데이터 분석 (Gemini)
# ════════════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("🤖 AI 데이터 분석 챗봇")
    st.caption("현재 필터 조건이 적용된 데이터를 기반으로 Gemini AI에게 질문할 수 있습니다.")

    if not GEMINI_API_KEY:
        st.error("GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")
    else:
        def build_data_context():
            lines = ["=== 발전기 운전실적 데이터 요약 (2023년) ===\n"]

            lines.append("[ 발전기 기본 정보 ]")
            lines.append(df_basic[["발전기ID", "설치위치", "제조사", "모델명", "정격용량(MW)", "설치년도"]].to_string(index=False))

            lines.append("\n[ 일별 발전 데이터 요약 (필터 적용) ]")
            if not df_daily_f.empty:
                summary = df_daily_f.groupby("발전기ID").agg(
                    총발전량=("발전량(MWh)", "sum"),
                    평균발전량=("발전량(MWh)", "mean"),
                    최대발전량=("발전량(MWh)", "max"),
                    평균효율=("평균효율(%)", "mean"),
                    평균가동시간=("가동시간(h)", "mean"),
                ).round(2)
                lines.append(summary.to_string())
                total = df_daily_f["발전량(MWh)"].sum()
                avg_eff = df_daily_f["평균효율(%)"].mean()
                util = df_daily_f["가동시간(h)"].sum() / (len(df_daily_f) * 24) * 100
                lines.append(f"\n전체 총 발전량: {total:,.0f} MWh")
                lines.append(f"전체 평균 효율: {avg_eff:.2f}%")
                lines.append(f"설비 이용률: {util:.1f}%")

            lines.append("\n[ 효율 분석 요약 (필터 적용) ]")
            if not df_eff_f.empty:
                eff_sum = df_eff_f.groupby("발전기ID").agg(
                    평균효율=("평균효율(%)", "mean"),
                    최고효율=("최고효율(%)", "max"),
                    최저효율=("최저효율(%)", "min"),
                ).round(2)
                lines.append(eff_sum.to_string())

            lines.append("\n[ 월별 발전량 합계 ]")
            if not df_daily_f.empty:
                monthly = df_daily_f.groupby("월")["발전량(MWh)"].sum().round(2)
                lines.append(monthly.to_string())

            return "\n".join(lines)

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_input = st.chat_input("데이터에 대해 질문해보세요. 예: 가장 효율이 높은 발전기는?")

        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                with st.spinner("분석 중..."):
                    try:
                        data_ctx = build_data_context()
                        system_prompt = (
                            "당신은 발전기 운전실적 데이터를 분석하는 전문 AI입니다. "
                            "아래 데이터를 바탕으로 사용자의 질문에 한국어로 명확하고 친절하게 답변해주세요. "
                            "수치를 인용할 때는 구체적인 숫자를 포함해주세요.\n\n"
                            + data_ctx
                        )
                        model = genai.GenerativeModel("gemini-2.5-flash")
                        history_for_gemini = []
                        for h in st.session_state.chat_history[:-1]:
                            role = "user" if h["role"] == "user" else "model"
                            history_for_gemini.append({"role": role, "parts": [h["content"]]})
                        chat = model.start_chat(history=history_for_gemini)
                        response = chat.send_message(system_prompt + "\n\n사용자 질문: " + user_input)
                        answer = response.text
                        st.markdown(answer)
                        st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    except Exception as e:
                        err_msg = f"오류가 발생했습니다: {str(e)}"
                        st.error(err_msg)
                        st.session_state.chat_history.append({"role": "assistant", "content": err_msg})

        if st.session_state.chat_history:
            if st.button("대화 초기화", key="clear_chat"):
                st.session_state.chat_history = []
                st.rerun()
