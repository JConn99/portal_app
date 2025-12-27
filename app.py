import os
from dotenv import load_dotenv
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from serpapi import GoogleSearch
import re
import streamlit as st
import pandas as pd

from portal import get_player_info

# Define icon URLs (replace with your preferred icons)
roster_icon = "https://img.icons8.com/?size=100&id=70933&format=png&color=000000"
x_icon = "https://img.icons8.com/ios-filled/50/000000/twitterx--v2.png"
hudl_icon = "https://img.icons8.com/?size=100&id=11631&format=png&color=000000"

tab1, tab2 = st.tabs(["Single Player Lookup", "File Upload Lookup"])

with tab1:
    st.title("Player Information Lookup")

    name = st.text_input("Enter the player's name:")
    school = st.text_input("Enter the school name:")

    if st.button("Search"):
        if name and school:
            player_df = get_player_info(name, school)
            if player_df is not None and not player_df.empty:
                st.subheader("Player Information")
                for _, row in player_df.iterrows():
                    col_img, col_info = st.columns([1, 3])
                    with col_img:
                        if row.get("profile_image"):
                            st.image(row["profile_image"], width=120)
                        else:
                            st.write("No image")
                        # Links as icons
                        links_md = ""
                        if row.get("roster_link"):
                            links_md += f'<a href="{row["roster_link"]}" target="_blank"><img src="{roster_icon}" width="35" style="margin-right:8px;"/></a>'
                        if row.get("x_link"):
                            links_md += f'<a href="{row["x_link"]}" target="_blank"><img src="{x_icon}" width="35" style="margin-right:8px;"/></a>'
                        if row.get("hudl_link"):
                            links_md += f'<a href="{row["hudl_link"]}" target="_blank"><img src="{hudl_icon}" width="35" style="margin-right:8px;"/></a>'
                        if links_md:
                            st.markdown(f'<div style="margin-top:10px;">{links_md}</div>', unsafe_allow_html=True)
                    with col_info:
                        st.markdown(f"<h2 style='margin-bottom: 0.5em'>{row['name']}</h2>", unsafe_allow_html=True)
                        info_left, info_right = st.columns(2)
                        with info_left:
                            st.markdown(f"**Position:** {row.get('position', '')}")
                            st.markdown(f"**Height:** {row.get('height', '')}")
                            st.markdown(f"**Weight:** {row.get('weight', '')}")
                            st.markdown(f"**Class:** {row.get('class', '')}")
                        with info_right:
                            st.markdown(f"**Hometown:** {row.get('hometown', '')}")
                            st.markdown(f"**Previous School:** {row.get('previous_school', '')}")
                            st.markdown(f"**Major:** {row.get('major', '')}")
                    st.markdown("---")


with tab2:
    st.subheader("Upload CSV to Process Players")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file is not None:
        csv_df = pd.read_csv(uploaded_file)
        if (
            not csv_df.empty
            and "Name" in list(csv_df.columns)
            and "School" in list(csv_df.columns)
        ):
            for _, csv_row in csv_df.iterrows():
                name = csv_row["Name"]
                school = csv_row["School"]
                player_df = get_player_info(name, school)
                if player_df is not None and not player_df.empty:
                    for _, row in player_df.iterrows():
                        col_img, col_info = st.columns([1, 3])
                        with col_img:
                            if row.get("profile_image"):
                                st.image(row["profile_image"], width=120)
                            else:
                                st.write("No image")
                            links_md = ""
                            if row.get("roster_link"):
                                links_md += f'<a href="{row["roster_link"]}" target="_blank"><img src="{roster_icon}" width="25" style="margin-right:8px;"/></a>'
                            if row.get("x_link"):
                                links_md += f'<a href="{row["x_link"]}" target="_blank"><img src="{x_icon}" width="25" style="margin-right:8px;"/></a>'
                            if row.get("hudl_link"):
                                links_md += f'<a href="{row["hudl_link"]}" target="_blank"><img src="{hudl_icon}" width="25" style="margin-right:8px;"/></a>'
                            if links_md:
                                st.markdown(f'<div style="margin-top:10px;">{links_md}</div>', unsafe_allow_html=True)
                        with col_info:
                            st.markdown(f"<h2 style='margin-bottom: 0.5em'>{row['name']}</h2>", unsafe_allow_html=True)
                            info_left, info_right = st.columns(2)
                            with info_left:
                                st.markdown(f"**Position:** {row.get('position', '')}")
                                st.markdown(f"**Height:** {row.get('height', '')}")
                                st.markdown(f"**Weight:** {row.get('weight', '')}")
                                st.markdown(f"**Class:** {row.get('class', '')}")
                            with info_right:
                                st.markdown(f"**Hometown:** {row.get('hometown', '')}")
                                st.markdown(f"**Previous School:** {row.get('previous_school', '')}")
                                st.markdown(f"**Major:** {row.get('major', '')}")
                        st.markdown("---")