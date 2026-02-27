#!/usr/bin/env python3
"""Streamlit web app for BTS two-day attendance comparison."""

from __future__ import annotations

from typing import Dict, List, Tuple

import streamlit as st

from compare_bts import Record, build_outputs, parse_line


def load_records_from_text(content: str, file_label: str) -> Tuple[Dict[str, Record], List[str]]:
    by_iin: Dict[str, Record] = {}
    skipped: List[str] = []

    for idx, line in enumerate(content.splitlines(), start=1):
        parsed = parse_line(line)
        if parsed is None:
            skipped.append(f"{file_label}:{idx}")
            continue
        by_iin[parsed.iin] = parsed

    return by_iin, skipped


def to_text(lines: List[str]) -> str:
    if not lines:
        return ""
    return "\n".join(lines).rstrip("\n") + "\n"


st.set_page_config(page_title="BTS Нәтиже Салыстыру", page_icon="📄", layout="wide")

st.title("BTS Нәтиже Салыстыру")
st.caption("Тек екі күнге де қатысқан оқушыларды анықтау. Нұсқаның 3-ші саны 7/8/9 ғана есепке алынады.")

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        day1_file = st.file_uploader("1-күн TXT", type=["txt"], key="day1")
    with col2:
        day2_file = st.file_uploader("2-күн TXT", type=["txt"], key="day2")

    run = st.button("Салыстыруды бастау", type="primary", use_container_width=True)

if run:
    if not day1_file or not day2_file:
        st.error("Екі файлды да енгізіңіз.")
        st.stop()

    day1_text = day1_file.getvalue().decode("utf-8", errors="replace")
    day2_text = day2_file.getvalue().decode("utf-8", errors="replace")

    day1_records, day1_skipped = load_records_from_text(day1_text, day1_file.name)
    day2_records, day2_skipped = load_records_from_text(day2_text, day2_file.name)

    both_lines, one_day_lines = build_outputs(day1_records, day2_records)

    both_count = len(set(day1_records) & set(day2_records))
    one_day_count = len(set(day1_records) ^ set(day2_records))
    skipped_count = len(day1_skipped) + len(day2_skipped)

    c1, c2, c3 = st.columns(3)
    c1.metric("Екі күн қатысқан", both_count)
    c2.metric("Бір күн ғана қатысқан", one_day_count)
    c3.metric("Өткізіліп кеткен жол", skipped_count)

    both_text = to_text(both_lines)
    one_day_text = to_text(one_day_lines)

    d1, d2 = st.columns(2)
    with d1:
        st.download_button(
            "Екі күн қатысқандар TXT жүктеу",
            data=both_text,
            file_name="eki_kunde_katyskandar.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with d2:
        st.download_button(
            "Бір күн қатысқандар TXT жүктеу",
            data=one_day_text,
            file_name="bir_kun_katyskandar.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with st.expander("Нәтиже алдын ала қарау", expanded=False):
        preview_col1, preview_col2 = st.columns(2)
        with preview_col1:
            st.subheader("Екі күн қатысқандар")
            st.text(both_text[:6000] if both_text else "Нәтиже жоқ")
        with preview_col2:
            st.subheader("Бір күн қатысқандар")
            st.text(one_day_text[:6000] if one_day_text else "Нәтиже жоқ")
