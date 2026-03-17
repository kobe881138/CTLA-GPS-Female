import streamlit as st
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import shutil

# ==========================================
# 🌟 終極防破圖系統：解決 Noto Sans 命名衝突 Bug
# ==========================================
cache_dir = mpl.get_cachedir()
if os.path.exists(cache_dir):
    shutil.rmtree(cache_dir, ignore_errors=True)

current_dir = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(current_dir, "NotoSansTC-Regular.ttf")

# 🚨 終極解法：把我們在 packages.txt 安裝的 'WenQuanYi Zen Hei' 排在第一順位！
# 這樣就能完美避開 'Noto Sans' 的英文撞名問題
font_list = ['WenQuanYi Zen Hei', 'Microsoft JhengHei', 'PingFang HK', 'Noto Sans CJK TC']

if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
    prop = fm.FontProperties(fname=font_path)
    font_name = prop.get_name()
    
    # 避免撞名，我們把 Noto Sans 塞到清單後面，讓文泉驛正黑體優先發揮作用
    if font_name not in font_list:
        font_list.append(font_name)
    font_status_msg = f"✅ 字體已載入 (防衝突模式啟動)"
else:
    font_status_msg = "⚠️ 找不到本機字體檔，使用雲端備用字體"

font_list.append('sans-serif')
plt.rcParams['font.sans-serif'] = font_list
plt.rcParams['axes.unicode_minus'] = False

# ==========================================
# 🌟 NCAA 女子長曲棍球基準數據庫
# ==========================================
NCAA_BASELINES = {
    'Average': {'dist': 4732, 'avg_spd': 78.87, 'top_spd': 6.7, 'hsd_ratio': 13.86},
    'A': {'dist': 4610, 'avg_spd': 76.83, 'top_spd': 6.5, 'hsd_ratio': 14.86},
    'M': {'dist': 4952, 'avg_spd': 82.53, 'top_spd': 6.9, 'hsd_ratio': 17.06},
    'D': {'dist': 4579, 'avg_spd': 76.32, 'top_spd': 6.5, 'hsd_ratio': 9.00}
}

st.set_page_config(page_title="女網 GPS 數據儀表板", layout="wide")

@st.cache_data
def load_data(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return None

df = load_data('Cleaned_GPS_Data_Women.csv')

if df is None:
    st.error("❌ 找不到資料！請確認 Cleaned_GPS_Data_Women.csv 是否存在。")
else:
    # 🌟 終極殺蟲劑：強制過濾掉任何含有 '#' 號的幽靈球員
    df = df[~df['Player'].astype(str).str.contains('#')]
    
    df['Date'] = df['Session'].astype(str).apply(lambda x: x.split()[0])
    
    st.sidebar.title("🥍 女網戰情室導覽")
    
    # 💡 在側邊欄顯示字體載入狀態，幫助我們除錯
    st.sidebar.caption(f"系統狀態: {font_status_msg}")
    st.sidebar.markdown("---")
    
    page_mode = st.sidebar.radio(
        "📌 選擇分析模式：", 
        ["📊 團隊總覽 (Team Dashboard)", "👤 個人報告 (Player Profile)"]
    )
    st.sidebar.markdown("---") 

    # ==========================================
    # 模式一：團隊總覽 (Team Dashboard)
    # ==========================================
    if page_mode == "📊 團隊總覽 (Team Dashboard)":
        st.title("🥍 女網 GPS 戰情室 - 團隊總覽")
        
        st.sidebar.header("⚙️ 團隊設定面板")
        available_dates = df['Date'].dropna().unique().tolist()
        selected_date = st.sidebar.selectbox("📅 第一步：選擇日期", available_dates, key='team_date')
        
        sessions_for_date = df[df['Date'] == selected_date]['Session'].unique().tolist()
        selected_session = st.sidebar.selectbox("⏱️ 第二步：選擇時段", sessions_for_date, key='team_session')
        
        st.write("---")
        df_filtered = df[df['Session'] == selected_session]
        
        if not df_filtered.empty:
            agg_dict = {'Total Distance (m)': 'max', 'Avg Speed (m/min)': 'mean', 'Top Speed (m/s)': 'max', 'HSD Ratio': 'max', 'Position': 'first'}
            if 'RPE' in df_filtered.columns: agg_dict['RPE'] = 'max'
            df_plot = df_filtered.groupby('Player').agg(agg_dict).reset_index()

            st.subheader(f"1️⃣ {selected_session} 外部與內部負荷")
            fig1, ax1 = plt.subplots(figsize=(12, 3.5))
            bars1 = ax1.bar(df_plot['Player'], df_plot['Total Distance (m)'], color='#e06666', width=0.5)
            ax1.axhline(y=NCAA_BASELINES['Average']['dist'], color='gold', linestyle='-', linewidth=2, label='NCAA Avg')
            
            team_avg_dist = df_plot['Total Distance (m)'].mean()
            if pd.notna(team_avg_dist):
                ax1.axhline(y=team_avg_dist, color='blue', linestyle='--', label='Team Avg')
            
            for bar in bars1:
                yval = bar.get_height()
                if pd.notna(yval) and yval > 0:
                    ax1.text(bar.get_x() + bar.get_width()/2, yval/2 + 200, int(yval), ha='center', va='center', color='white', fontweight='bold', fontsize=12)
            ax1.legend()
            st.pyplot(fig1)

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("2️⃣ 平均速度表現 (vs. NCAA Avg)")
                fig2, ax2 = plt.subplots(figsize=(6, 4))
                bars2 = ax2.bar(df_plot['Player'], df_plot['Avg Speed (m/min)'], color='#c27ba0', width=0.5)
                ax2.axhline(y=NCAA_BASELINES['Average']['avg_spd'], color='gold', linestyle='-', linewidth=2, label='NCAA Avg')
                
                team_avg_spd = df_plot['Avg Speed (m/min)'].mean()
                if pd.notna(team_avg_spd):
                    ax2.axhline(y=team_avg_spd, color='blue', linestyle='--', alpha=0.5, label='Team Avg')
                    
                for bar in bars2:
                    yval = bar.get_height()
                    if pd.notna(yval) and yval > 0:
                        ax2.text(bar.get_x() + bar.get_width()/2, yval + 1, f"{yval:.1f}", ha='center', va='bottom', fontweight='bold')
                ax2.legend(loc='lower right')
                st.pyplot(fig2)

            with col2:
                st.subheader("3️⃣ 單節/分段 體能維持率")
                is_training = 'training' in selected_session.lower()
                if is_training:
                    quarter_sessions = [s for s in sessions_for_date if 'training' in str(s).lower() and str(s).split()[-1].isdigit()]
                else:
                    quarter_sessions = [s for s in sessions_for_date if 'training' not in str(s).lower() and str(s).split()[-1].isdigit()]

                quarter_sessions = sorted(quarter_sessions)

                if len(quarter_sessions) > 0:
                    df_q = df[df['Session'].isin(quarter_sessions)]
                    players = sorted(df_q['Player'].unique())
                    fig3_q, ax3_q = plt.subplots(figsize=(6, 4))
                    x = np.arange(len(players))
                    width = 0.8 / len(quarter_sessions)
                    colors = ['#6fa8dc', '#f6b26b', '#93c47d', '#ffd966']
                    
                    for i, q_sess in enumerate(quarter_sessions):
                        q_data = df_q[df_q['Session'] == q_sess]
                        y_vals = [q_data[q_data['Player'] == p]['Total Distance (m)'].max() if not q_data[q_data['Player'] == p].empty else 0 for p in players]
                        offset = i * width - (0.8/2) + (width/2)
                        bars_q = ax3_q.bar(x + offset, y_vals, width, label=f"{q_sess}", color=colors[i%len(colors)])
                        for bar in bars_q:
                            h = bar.get_height()
                            if pd.notna(h) and h > 0:
                                ax3_q.text(bar.get_x() + bar.get_width()/2, h/2, int(h), ha='center', va='center', color='white', fontsize=10, fontweight='bold', rotation=90)
                    
                    team_avg_q_dist = df_q['Total Distance (m)'].mean()
                    if pd.notna(team_avg_q_dist):
                        ax3_q.axhline(team_avg_q_dist, color='blue', linestyle='--', label='Session Avg')
                        
                    ax3_q.set_xticks(x)
                    ax3_q.set_xticklabels(players)
                    ax3_q.legend(loc='upper right', fontsize='small')
                    st.pyplot(fig3_q)
                else:
                    st.info("💡 此時段無單節資料。")

            st.write("<br>", unsafe_allow_html=True)
            st.subheader("4️⃣ 爆發力象限圖 (含 NCAA 各位置基準)")
            spacer1, col_center, spacer2 = st.columns([1, 2, 1])
            with col_center:
                fig4, ax4 = plt.subplots(figsize=(8, 5))
                x_data = df_plot['HSD Ratio'] * 100
                y_data = df_plot['Top Speed (m/s)']
                session_avg_hsd = x_data.mean()
                session_avg_top = y_data.mean()
                
                ax4.scatter(x_data, y_data, color='#e06666', s=150, zorder=5, label='Players')
                for i, player in enumerate(df_plot['Player']):
                    pos = df_plot['Position'].iloc[i]
                    if pd.notna(x_data[i]) and pd.notna(y_data[i]):
                        ax4.text(x_data[i] + 0.2, y_data[i], f"{player}({pos})", fontsize=9, fontweight='bold', va='center')

                if pd.notna(session_avg_hsd) and pd.notna(session_avg_top):
                    ax4.scatter(session_avg_hsd, session_avg_top, color='blue', marker='P', s=200, zorder=6, label='Session Avg')
                    ax4.axvline(x=session_avg_hsd, color='blue', linestyle='--', alpha=0.3)
                    ax4.axhline(y=session_avg_top, color='blue', linestyle='--', alpha=0.3)

                pos_colors = {'A': '#e69138', 'M': '#38761d', 'D': '#1155cc'}
                for p in ['A', 'M', 'D']:
                    ncaa_hsd = NCAA_BASELINES[p]['hsd_ratio']
                    ncaa_top = NCAA_BASELINES[p]['top_spd']
                    ax4.scatter(ncaa_hsd, ncaa_top, color=pos_colors[p], marker='*', s=250, zorder=10, label=f'NCAA {p}')

                ax4.set_xlabel('HSD (>4m/s) Ratio (%)', fontweight='bold')
                ax4.set_ylabel('Top Speed (m/s)', fontweight='bold')
                ax4.legend(loc='upper left', bbox_to_anchor=(1, 1))
                st.pyplot(fig4)
        else:
            st.warning("此時段沒有數據喔！")

    # ==========================================
    # 模式二：個人專屬報告 (Player Profile - Total Focus)
    # ==========================================
    elif page_mode == "👤 個人報告 (Player Profile)":
        st.title("🥍 女網 GPS 戰情室 - 個人報告")
        
        st.sidebar.header("👤 個人報告設定")
        all_players = sorted(df['Player'].unique().tolist())
        selected_player = st.sidebar.selectbox("🏃 選擇選手：", all_players)
        
        df_total_only = df[df['Session'].str.lower().str.contains('total')]
        player_dates_with_total = df_total_only[df_total_only['Player'] == selected_player]['Date'].dropna().unique().tolist()
        all_total_dates = df_total_only['Date'].dropna().unique().tolist()
        
        if not player_dates_with_total:
            st.warning(f"💡 找不到 {selected_player} 的 Total 加總數據。")
        else:
            raw_pos = str(df_total_only[df_total_only['Player'] == selected_player]['Position'].iloc[0])
            primary_pos = raw_pos.split('/')[0].strip().upper() if '/' in raw_pos else raw_pos.strip().upper()
            if primary_pos not in ['A', 'M', 'D']: primary_pos = 'Average'

            st.sidebar.markdown("### 🎯 NCAA 對標設定")
            ncaa_options = ['Average', 'A', 'M', 'D']
            default_index = ncaa_options.index(primary_pos) if primary_pos in ncaa_options else 0
            
            selected_ncaa = st.sidebar.selectbox("長條圖比較 NCAA 對象：", ncaa_options, index=default_index)
            
            st.write("---")
            st.subheader(f"🛡️ {selected_player} (註冊位置: {raw_pos} | 長條圖當前對標: NCAA {selected_ncaa}) - 個人表現分析")

            col_radar, col_bar = st.columns([1, 1.5])

            # ==========================================
            # 🎯 雷達圖：對標當日團隊平均 (Z-Score 標準化)
            # ==========================================
            with col_radar:
                st.markdown(f"##### 📍 六角雷達圖：對標當日團隊平均")
                radar_date = st.selectbox("📅 選擇雷達圖日期：", player_dates_with_total, index=0)
                
                team_radar_df = df_total_only[df_total_only['Date'] == radar_date]
                team_mean = team_radar_df[['Total Distance (m)', 'Avg Speed (m/min)', 'Top Speed (m/s)', 'HSD Ratio']].mean()
                team_std = team_radar_df[['Total Distance (m)', 'Avg Speed (m/min)', 'Top Speed (m/s)', 'HSD Ratio']].std().replace(0, 1).fillna(1)
                
                player_radar = df_total_only[(df_total_only['Player'] == selected_player) & (df_total_only['Date'] == radar_date)].iloc[0]

                categories = ['Total Distance', 'Average Speed', 'Max Speed', 'HSD Ratio']
                N = len(categories)
                
                def calc_z(col):
                    if pd.isna(player_radar[col]) or pd.isna(team_mean[col]): return 0
                    z = (player_radar[col] - team_mean[col]) / team_std[col]
                    return np.clip(z, -2, 2)
                    
                p_dist = calc_z('Total Distance (m)')
                p_avg_spd = calc_z('Avg Speed (m/min)')
                p_top_spd = calc_z('Top Speed (m/s)')
                p_hsd = calc_z('HSD Ratio')
                
                player_ratios = [p_dist, p_avg_spd, p_top_spd, p_hsd]
                player_ratios += player_ratios[:1] 
                team_ratios = [0, 0, 0, 0, 0] 
                
                angles = [n / float(N) * 2 * np.pi for n in range(N)]
                angles += angles[:1]

                fig_r, ax_r = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
                ax_r.set_theta_offset(np.pi / 2)
                ax_r.set_theta_direction(-1)
                ax_r.set_xticks(angles[:-1])
                ax_r.set_xticklabels(categories, fontsize=12, fontweight='bold')
                
                ax_r.set_ylim(-2, 2)
                ax_r.set_yticks([-2, -1, 0, 1, 2])
                ax_r.set_yticklabels(['-2', '-1', '0', '1', '2'], color="grey", size=9, alpha=0.7)
                
                ax_r.plot(angles, team_ratios, linewidth=2, linestyle='dashed', color='#e06666', label=f'{radar_date} Team Avg (0)')
                ax_r.fill(angles, team_ratios, color='#e06666', alpha=0.1)
                
                ax_r.plot(angles, player_ratios, linewidth=2.5, color='#4a86e8', label=f'{selected_player}')
                ax_r.fill(angles, player_ratios, color='#4a86e8', alpha=0.3)

                ax_r.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
                st.pyplot(fig_r)

            # ==========================================
            # 📊 長條圖：連動選擇 (解決同日疊加 Bug)
            # ==========================================
            with col_bar:
                st.markdown("##### 📈 歷史進步軌跡")
                
                col_b1, col_b2 = st.columns(2)
                with col_b1: 
                    player_selected_date = st.selectbox("📅 當前表現 (Current)：", player_dates_with_total)
                with col_b2:
                    selected_baseline = st.selectbox("📉 比較基準 (Baseline)：", ["NCAA Benchmark"] + all_total_dates)
                
                player_current_bar = df_total_only[(df_total_only['Player'] == selected_player) & (df_total_only['Date'] == player_selected_date)].iloc[0]
                
                current_label = f"{player_selected_date} (當前)"
                can_plot = False
                
                if selected_baseline == "NCAA Benchmark":
                    ncaa_target = NCAA_BASELINES[selected_ncaa]
                    past_avg = {
                        'Total Distance (m)': ncaa_target['dist'],
                        'Avg Speed (m/min)': ncaa_target['avg_spd'],
                        'Top Speed (m/s)': ncaa_target['top_spd'],
                        'HSD Ratio': ncaa_target['hsd_ratio'] / 100 
                    }
                    baseline_label = f"NCAA {selected_ncaa} (基準)"
                    can_plot = True
                else:
                    past_data = df_total_only[(df_total_only['Player'] == selected_player) & (df_total_only['Date'] == selected_baseline)]
                    if not past_data.empty:
                        past_avg = past_data[['Total Distance (m)', 'Avg Speed (m/min)', 'Top Speed (m/s)', 'HSD Ratio']].mean()
                        baseline_label = f"{selected_baseline} (基準)"
                        can_plot = True
                    else:
                        st.info(f"💡 貼心提醒：{selected_player} 在 {selected_baseline} 剛好沒有紀錄，請選擇其他日期作為基準喔！")
                        can_plot = False

                if can_plot:
                    fig_b, axes = plt.subplots(1, 4, figsize=(10, 4))
                    metrics = [
                        ('Total Distance', 'Total Distance (m)', '#e06666', '#ea9999'),
                        ('Average Speed', 'Avg Speed (m/min)', '#c27ba0', '#d5a6bd'),
                        ('Max Speed', 'Top Speed (m/s)', '#f6b26b', '#fce5cd'),
                        ('HSD Ratio (%)', 'HSD Ratio', '#93c47d', '#d9ead3')
                    ]
                    
                    labels = [baseline_label, current_label]
                    for i, (title, col_name, color_curr, color_past) in enumerate(metrics):
                        val_past = past_avg[col_name] if pd.notna(past_avg[col_name]) else 0
                        val_curr = player_current_bar[col_name] if pd.notna(player_current_bar[col_name]) else 0
                        
                        if 'Ratio' in col_name:
                            val_past *= 100
                            val_curr *= 100
                            
                        bars = axes[i].bar(labels, [val_past, val_curr], color=[color_past, color_curr], width=0.6)
                        axes[i].set_title(title, fontweight='bold', fontsize=11)
                        axes[i].spines['top'].set_visible(False)
                        axes[i].spines['right'].set_visible(False)
                        
                        for bar in bars:
                            yval = bar.get_height()
                            if pd.notna(yval) and yval > 0:
                                format_str = f"{int(yval)}" if 'Distance' in title else f"{yval:.1f}"
                                axes[i].text(bar.get_x() + bar.get_width()/2, yval + (yval*0.02), format_str, ha='center', va='bottom', fontweight='bold', fontsize=10)

                    plt.tight_layout()
                    st.pyplot(fig_b)