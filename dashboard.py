import streamlit as st
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="발전기 운전실적 분석", layout="wide", page_icon="⚡")

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

with st.sidebar:
    st.title("⚙️ 필터")

    gen_options = sorted(df_daily["발전기ID"].unique().tolist())
    sel_gens = st.multiselect("발전기 선택", gen_options, default=gen_options)
    if not sel_gens:
        sel_gens = gen_options

    period_opt = st.selectbox("기간 선택", ["전체", "상반기(1~6월)", "하반기(7~12월)", "분기 선택"])
    sel_quarter = None
    if period_opt == "분기 선택":
        sel_quarter = st.selectbox("분기", ["Q1", "Q2", "Q3", "Q4"])

    st.divider()
    st.info("데이터 기준: 2023년")

# 필터 적용
df_daily_f = df_daily[df_daily["발전기ID"].isin(sel_gens)].copy()
if period_opt == "상반기(1~6월)":
    df_daily_f = df_daily_f[df_daily_f["월"] <= 6]
elif period_opt == "하반기(7~12월)":
    df_daily_f = df_daily_f[df_daily_f["월"] >= 7]
elif period_opt == "분기 선택" and sel_quarter:
    df_daily_f = df_daily_f[df_daily_f["분기"] == sel_quarter]

df_eff_f = df_weekly[df_weekly["발전기ID"].isin(sel_gens)].copy()
if period_opt == "상반기(1~6월)":
    df_eff_f = df_eff_f[df_eff_f["월"] <= 6]
elif period_opt == "하반기(7~12월)":
    df_eff_f = df_eff_f[df_eff_f["월"] >= 7]
elif period_opt == "분기 선택" and sel_quarter:
    q_months = {"Q1": [1,2,3], "Q2": [4,5,6], "Q3": [7,8,9], "Q4": [10,11,12]}
    df_eff_f = df_eff_f[df_eff_f["월"].isin(q_months[sel_quarter])]

df_hourly_f = df_hourly[df_hourly["발전기ID"].isin(sel_gens)].copy()

# ── 탭 ───────────────────────────────────────────────────────────────────────

st.title("⚡ 발전기 운전실적 분석 대시보드")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 운전 실적 요약", "🔋 출력 분석", "📈 효율 분석", "🌡️ 온도-성능 상관관계", "🤖 AI 데이터 분석"])

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
            st.markdown("**월별 발전량 (발전기별 누적)**")
            monthly_pivot = df_daily_f.pivot_table(
                index="월", columns="발전기ID", values="발전량(MWh)", aggfunc="sum"
            )
            st.bar_chart(monthly_pivot, use_container_width=True)

        with col_b:
            st.markdown("**일별 평균 가동시간 추이**")
            daily_op = df_daily_f.groupby("날짜")["가동시간(h)"].mean()
            st.line_chart(daily_op, use_container_width=True)

        st.divider()
        st.markdown("**발전기 기본 정보**")
        st.dataframe(
            df_basic[["발전기ID", "설치위치", "제조사", "모델명", "정격용량(MW)", "설치년도", "연간운영시간(h)"]],
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
        st.markdown("**일별 발전량 추이 (발전기별)**")
        daily_pivot = df_daily_f.pivot_table(
            index="날짜", columns="발전기ID", values="발전량(MWh)", aggfunc="sum"
        )
        st.line_chart(daily_pivot, use_container_width=True)

        st.divider()
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**월별 평균 발전량 비교**")
            monthly_avg = df_daily_f.pivot_table(
                index="월", columns="발전기ID", values="발전량(MWh)", aggfunc="mean"
            )
            st.bar_chart(monthly_avg, use_container_width=True)

        with col_b:
            st.markdown("**분기별 발전량 누적**")
            q_order = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}
            qtr_pivot = df_daily_f.pivot_table(
                index="분기", columns="발전기ID", values="발전량(MWh)", aggfunc="sum"
            )
            qtr_pivot = qtr_pivot.reindex([q for q in ["Q1","Q2","Q3","Q4"] if q in qtr_pivot.index])
            st.area_chart(qtr_pivot, use_container_width=True)

        st.divider()
        st.markdown("**발전기별 출력 요약**")
        summary = df_daily_f.groupby("발전기ID").agg(
            총발전량=("발전량(MWh)", "sum"),
            최대일간발전량=("발전량(MWh)", "max"),
            평균발전량=("발전량(MWh)", "mean"),
            평균가동시간=("가동시간(h)", "mean"),
        ).round(2).reset_index()
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
        eff_pivot = df_eff_f.pivot_table(
            index="주차", columns="발전기ID", values="평균효율(%)", aggfunc="mean"
        )
        eff_pivot["목표(52%)"] = 52.0
        st.line_chart(eff_pivot, use_container_width=True)

        st.divider()
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**월별 목표효율 달성율 (%)**")
            monthly_achieve = df_daily_f.pivot_table(
                index="월", columns="발전기ID", values="평균효율(%)", aggfunc="mean"
            )
            monthly_achieve_rate = (monthly_achieve / 52.0 * 100).round(2)
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
                color="발전기ID",
                use_container_width=True,
            )

        with col_b:
            st.markdown("**외기온도 vs 효율**")
            st.caption("15°C 부근에서 최고 효율 53% | 온도 이탈 시 최저 49%까지 감소")
            st.scatter_chart(
                df_hourly_f,
                x="외기온도(°C)",
                y="효율(%)",
                color="발전기ID",
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
