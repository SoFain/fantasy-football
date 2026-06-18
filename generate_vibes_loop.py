import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cv2
import sys
import pandas as pd
from google.cloud import bigquery

# Video configuration
width, height = 1920, 1080
fps = 30
duration_secs = 30
total_frames = fps * duration_secs

# Create the VideoWriter using the cross-platform MPEG-4 codec
video_path = "vibes_background_loop.mp4"
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

print(f"Initializing video writer: {video_path} ({width}x{height} @ {fps}fps)")
print("Connecting to BigQuery to fetch actual NFL stats...")

# Query BigQuery once at startup
try:
    client = bigquery.Client(project="fantasy-football-498121")
    
    # 1. Fetch top players for Mojo vs Swag Scatter Plot
    top_players_sql = """
        WITH max_s AS (
            SELECT MAX(season) as max_season 
            FROM `fantasy-football-498121.fantasy_football_brain.analytics_player_weekly_truth`
        )
        SELECT 
            player_name, 
            position, 
            team, 
            AVG(fantasy_points_ppr) as avg_ppr,
            AVG(opportunity_score) as avg_opportunity,
            AVG(efficiency_score) as avg_efficiency,
            AVG(analytical_grade) as avg_grade
        FROM `fantasy-football-498121.fantasy_football_brain.analytics_player_weekly_truth`, max_s
        WHERE season = max_s.max_season AND position IN ('QB', 'RB', 'WR', 'TE')
        GROUP BY player_name, position, team
        ORDER BY avg_ppr DESC
        LIMIT 10
    """
    df_players = client.query(top_players_sql).result().to_dataframe()
    print(f"Loaded {len(df_players)} players for Mojo-Swag Scatter Plot.")
    
    # 2. Fetch weekly stats for top 3 players
    weekly_sql = """
        WITH max_s AS (
            SELECT MAX(season) as max_season 
            FROM `fantasy-football-498121.fantasy_football_brain.analytics_player_weekly_truth`
        ),
        top_players AS (
            SELECT 
                player_id,
                player_name,
                AVG(fantasy_points_ppr) as avg_ppr
            FROM `fantasy-football-498121.fantasy_football_brain.analytics_player_weekly_truth`, max_s
            WHERE season = max_s.max_season AND position IN ('QB', 'RB', 'WR', 'TE')
            GROUP BY player_id, player_name
            ORDER BY avg_ppr DESC
            LIMIT 3
        )
        SELECT 
            t.player_name,
            t.week,
            t.fantasy_points_ppr
        FROM `fantasy-football-498121.fantasy_football_brain.analytics_player_weekly_truth` t
        JOIN top_players tp ON t.player_id = tp.player_id
        WHERE t.season = (SELECT max_season FROM max_s)
        ORDER BY t.player_name, t.week
    """
    df_weekly = client.query(weekly_sql).result().to_dataframe()
    print(f"Loaded {len(df_weekly)} weekly logs for Swag Trend Chart.")
    
except Exception as e:
    print(f"Error querying BigQuery: {e}")
    print("Falling back to local high-fidelity mock data...")
    # High-quality fallback data
    df_players = pd.DataFrame([
        {"player_name": "C.McCaffrey", "position": "RB", "team": "SF", "avg_ppr": 24.5, "avg_opportunity": 88.6, "avg_efficiency": 82.1, "avg_grade": 92.0},
        {"player_name": "P.Nacua", "position": "WR", "team": "LA", "avg_ppr": 23.4, "avg_opportunity": 85.2, "avg_efficiency": 80.5, "avg_grade": 90.1},
        {"player_name": "J.Allen", "position": "QB", "team": "BUF", "avg_ppr": 22.8, "avg_opportunity": 91.0, "avg_efficiency": 78.4, "avg_grade": 89.5},
        {"player_name": "B.Robinson", "position": "RB", "team": "ATL", "avg_ppr": 21.8, "avg_opportunity": 84.1, "avg_efficiency": 79.8, "avg_grade": 88.0},
        {"player_name": "J.Gibbs", "position": "RB", "team": "DET", "avg_ppr": 21.5, "avg_opportunity": 80.3, "avg_efficiency": 85.4, "avg_grade": 87.6},
        {"player_name": "J.Jefferson", "position": "WR", "team": "MIN", "avg_ppr": 21.2, "avg_opportunity": 86.4, "avg_efficiency": 83.1, "avg_grade": 91.2},
        {"player_name": "C.Lamb", "position": "WR", "team": "DAL", "avg_ppr": 20.8, "avg_opportunity": 85.0, "avg_efficiency": 81.2, "avg_grade": 89.8},
        {"player_name": "T.Hill", "position": "WR", "team": "MIA", "avg_ppr": 20.5, "avg_opportunity": 84.8, "avg_efficiency": 82.5, "avg_grade": 90.5},
        {"player_name": "L.Jackson", "position": "QB", "team": "BAL", "avg_ppr": 20.1, "avg_opportunity": 88.0, "avg_efficiency": 76.5, "avg_grade": 88.2},
        {"player_name": "A.St. Brown", "position": "WR", "team": "DET", "avg_ppr": 19.8, "avg_opportunity": 83.5, "avg_efficiency": 80.0, "avg_grade": 88.8},
    ])
    
    df_weekly = pd.DataFrame([
        {"player_name": "C.McCaffrey", "week": w, "fantasy_points_ppr": 20 + 5*np.sin(w*0.8) + np.random.normal(0,1)} for w in range(1, 11)
    ] + [
        {"player_name": "P.Nacua", "week": w, "fantasy_points_ppr": 18 + 4*np.cos(w*0.7) + np.random.normal(0,1)} for w in range(1, 11)
    ] + [
        {"player_name": "J.Allen", "week": w, "fantasy_points_ppr": 22 + 6*np.sin(w*0.6) + np.random.normal(0,1)} for w in range(1, 11)
    ])

# Calculate Mojo-Swag coordinates statically to normalize, then animate dynamically
mojo_base = (df_players["avg_opportunity"] * 0.6 + df_players["avg_grade"] * 0.4).values
swag_base = (df_players["avg_ppr"] * 2.5 + df_players["avg_efficiency"] * 0.3).values

# Normalize Mojo and Swag values to a nice 65-95 range
min_m, max_m = mojo_base.min(), mojo_base.max()
min_s, max_s = swag_base.min(), swag_base.max()

mojo_norm = 65 + 28 * (mojo_base - min_m) / (max_m - min_m + 1e-5)
swag_norm = 65 + 28 * (swag_base - min_s) / (max_s - min_s + 1e-5)

# Prep the line chart weekly data series
top_3_names = df_weekly["player_name"].unique()[:3]
weekly_series = {}
for name in top_3_names:
    player_data = df_weekly[df_weekly["player_name"] == name].sort_values("week")
    weeks = player_data["week"].values
    points = player_data["fantasy_points_ppr"].fillna(0.0).values
    # Normalize points slightly for Swag Momentum (scale to 60-95)
    points_norm = 60 + 30 * (points - points.min()) / (points.max() - points.min() + 1e-5)
    weekly_series[name] = {"weeks": weeks, "points": points_norm}

print(f"Generating {total_frames} frames for a {duration_secs}-second seamless loop...")

for f in range(total_frames):
    # Theta ranges from 0 to 2*pi for seamless looping
    theta = 2 * np.pi * (f / total_frames)
    
    fig = plt.figure(figsize=(16, 9), dpi=120)
    fig.patch.set_facecolor('#080d1a') # deep navy background
    
    # Title overlay
    fig.suptitle("AI VS MEATBAGS  •  FEELINGS BASED ANALYTICS", color='#f472b6', fontsize=20, fontweight='black', y=0.96)
    
    # 1. MOJO-SWAG QUANTUM VECTOR SCATTER PLOT (Top Central Axis)
    ax1 = fig.add_axes([0.28, 0.52, 0.44, 0.38])
    ax1.set_facecolor('#080d1a')
    ax1.grid(True, color='#1e293b', alpha=0.3, linestyle=':')
    ax1.set_title("THE MOJO-SWAG QUANTUM VECTOR", color='#38bdf8', fontsize=12, fontweight='bold', pad=8)
    
    ax1.set_xlim(55, 105)
    ax1.set_ylim(55, 105)
    ax1.set_xlabel("MOJO VECTOR (EPA/GRADE WEIGHTED)", color='#475569', fontsize=8, fontweight='bold')
    ax1.set_ylabel("SWAG INDEX (PPR/EFF WEIGHTED)", color='#475569', fontsize=8, fontweight='bold')
    ax1.tick_params(colors='#475569', labelsize=8)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_color('#1e293b')
    ax1.spines['bottom'].set_color('#1e293b')
    
    # 2. WEEKLY SWAG FLOW MOMENTUM LINE CHART (Bottom Central Axis)
    ax2 = fig.add_axes([0.28, 0.08, 0.44, 0.36])
    ax2.set_facecolor('#080d1a')
    ax2.grid(True, color='#1e293b', alpha=0.3, linestyle=':')
    ax2.set_title("WEEKLY SWAG FLOW MOMENTUM", color='#ec4899', fontsize=12, fontweight='bold', pad=8)
    
    ax2.set_xlim(1, 10)
    ax2.set_ylim(50, 105)
    ax2.set_xlabel("NFL REGULAR SEASON WEEK", color='#475569', fontsize=8, fontweight='bold')
    ax2.set_ylabel("SWAG MOMENTUM INDEX", color='#475569', fontsize=8, fontweight='bold')
    ax2.tick_params(colors='#475569', labelsize=8)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_color('#1e293b')
    ax2.spines['bottom'].set_color('#1e293b')
    
    # Animate Top Scatter Plot (players orbit slightly)
    for i, row in df_players.iterrows():
        p_name = row["player_name"]
        pos = row["position"]
        # Slow orbit animation phase-shifted per player
        orbit_x = mojo_norm[i] + 3.0 * np.sin(theta + i * 1.2)
        orbit_y = swag_norm[i] + 3.0 * np.cos(theta + i * 0.9)
        
        # Color by position
        if pos == "QB":
            color = "#10b981" # neon green
            marker = "o"
        elif pos == "RB":
            color = "#06b6d4" # neon cyan
            marker = "s"
        elif pos == "WR":
            color = "#ec4899" # neon pink
            marker = "^"
        else:
            color = "#a855f7" # neon purple
            marker = "D"
            
        # Draw scatter point with subtle glow
        ax1.scatter(orbit_x, orbit_y, c=color, alpha=0.3, s=180, marker=marker, edgecolors='none')
        ax1.scatter(orbit_x, orbit_y, c=color, alpha=0.9, s=50, marker=marker, edgecolors='#f8fafc', linewidths=0.5)
        
        # Draw player label next to point
        ax1.text(orbit_x + 1.2, orbit_y - 0.5, f"{p_name} ({pos})", color='#cbd5e1', fontsize=7.5, weight='semibold')

    # Animate Bottom Line Chart (weekly swag flows like waves)
    colors_line = ["#06b6d4", "#ec4899", "#f59e0b"]
    for idx, (name, data) in enumerate(weekly_series.items()):
        weeks = data["weeks"]
        points = data["points"]
        
        # Add dynamic waves to weekly points
        dynamic_points = points + 6.5 * np.sin(theta + weeks * 0.7 + idx * 1.5)
        color = colors_line[idx % len(colors_line)]
        
        # Draw line with glow effect
        ax2.plot(weeks, dynamic_points, color=color, alpha=0.15, linewidth=8)
        ax2.plot(weeks, dynamic_points, color=color, alpha=0.3, linewidth=4)
        ax2.plot(weeks, dynamic_points, color=color, alpha=0.9, linewidth=2, label=f"{name} (Vibe Flow)")
        
        # Draw endpoints
        ax2.scatter(weeks[-1], dynamic_points[-1], color=color, s=30, zorder=5)
        
    ax2.legend(loc='lower left', facecolor='#080d1a', edgecolor='#1e293b', labelcolor='#cbd5e1', fontsize=7.5)

    # DRAW COHOST OVERLAY CALIBRATION SIDES (Visual indicators for left/right host positions)
    # Divider lines at 25% and 75%
    line_left = plt.Line2D([0.26, 0.26], [0.05, 0.92], transform=fig.transFigure, color='#1e293b', linestyle='--', alpha=0.5, linewidth=1.5)
    line_right = plt.Line2D([0.74, 0.74], [0.05, 0.92], transform=fig.transFigure, color='#1e293b', linestyle='--', alpha=0.5, linewidth=1.5)
    fig.add_artist(line_left)
    fig.add_artist(line_right)
    
    # Calibration guides and grid text in margins
    fig.text(0.12, 0.5, "COHOST 1 ZONE • LEFT WEB FEED", color='#1e293b', alpha=0.25, fontsize=12, fontweight='bold', ha='center', va='center', rotation=90)
    fig.text(0.88, 0.5, "COHOST 2 ZONE • RIGHT WEB FEED", color='#1e293b', alpha=0.25, fontsize=12, fontweight='bold', ha='center', va='center', rotation=90)
    
    # Save frame
    # plt.tight_layout(rect=[0, 0, 1, 0.93])
    fig.canvas.draw()
    
    # Convert figure to OpenCV image
    img_rgba = np.asarray(fig.canvas.buffer_rgba())
    img = cv2.cvtColor(img_rgba, cv2.COLOR_RGBA2BGR)
    
    # Resize to exactly 1920x1080 if needed
    if img.shape[1] != width or img.shape[0] != height:
        img = cv2.resize(img, (width, height))
        
    out.write(img)
    plt.close(fig)
    
    # Print progress
    if (f + 1) % 90 == 0:
        print(f"Progress: {((f + 1) / total_frames) * 100:.1f}% done ({f+1}/{total_frames} frames)")

out.release()
print(f"Seamless 30s background loop successfully generated at: {video_path}")
