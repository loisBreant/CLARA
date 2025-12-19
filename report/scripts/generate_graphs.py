import csv
import os
import math
import statistics

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TELEMETRICS_PATH = os.path.join(BASE_DIR, "../../back/telemetrics.csv")
OPENROUTER_PATH = os.path.join(BASE_DIR, "../../back/openrouter_activity_2025-12-19.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "../images")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- SVG Helpers ---

def create_svg(width, height, content):
    return f'<svg version="1.1" width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" style="font-family: sans-serif; background: white;">\n{content}\n</svg>'

def rect(x, y, w, h, fill, stroke="none", opacity=1.0):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" fill-opacity="{opacity}" />'

def circle(cx, cy, r, fill, stroke="none", opacity=1.0):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" fill-opacity="{opacity}" />'

def line(x1, y1, x2, y2, stroke, width=1):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{width}" />'

def text(x, y, content, size=12, fill="black", anchor="middle", rotate=0):
    transform = f'transform="rotate({rotate} {x} {y})"' if rotate else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" {transform}>{content}</text>'

def group(content, transform=""):
    t_attr = f'transform="{transform}"' if transform else ""
    return f'<g {t_attr}>\n{content}\n</g>'

# --- Data Loading ---

def load_telemetrics():
    data = []
    try:
        with open(TELEMETRICS_PATH, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Clean Agent Type
                atype = row['model_kind']
                if '.' in atype:
                    atype = atype.split('.')[-1]
                
                try:
                    data.append({
                        'agent_type': atype,
                        'total_tokens': float(row['input_tokens']) + float(row['output_tokens']),
                        'time_taken': float(row['time_taken'])
                    })
                except ValueError:
                    continue
    except FileNotFoundError:
        print("Telemetrics file not found.")
    return data

def load_openrouter():
    data = []
    try:
        with open(OPENROUTER_PATH, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Handle empty strings for numeric fields
                    cost_str = row.get('cost_total', '0')
                    cost = float(cost_str) if cost_str else 0.0
                    
                    time_str = row.get('generation_time_ms', '0')
                    time_ms = float(time_str) if time_str else 0.0
                    
                    prompt_str = row.get('tokens_prompt', '0')
                    comp_str = row.get('tokens_completion', '0')
                    tokens = float(prompt_str) + float(comp_str)
                    
                    data.append({
                        'provider': row.get('provider_name', 'Unknown'),
                        'cost': cost,
                        'tokens': tokens,
                        'time_ms': time_ms
                    })
                except ValueError:
                    continue
    except FileNotFoundError:
        print("OpenRouter file not found.")
    return data

# --- Chart Generators ---

def generate_scatter(data, output_path):
    # Latency vs Tokens
    width, height = 800, 500
    margin = 60
    
    if not data:
        return

    max_tokens = max(d['total_tokens'] for d in data) * 1.1
    max_time = max(d['time_taken'] for d in data) * 1.1
    
    # Axis
    svg_content = []
    
    # Grid and Axis Labels
    svg_content.append(line(margin, height - margin, width - margin, height - margin, "black", 2)) # X
    svg_content.append(line(margin, margin, margin, height - margin, "black", 2)) # Y
    
    svg_content.append(text(width/2, height - 10, "Total Tokens", 14))
    svg_content.append(text(20, height/2, "Latence (s)", 14, rotate=-90))
    svg_content.append(text(width/2, 30, "Performance: Latence vs Tokens", 18))

    # Plot points
    colors = {"PLANNER": "#e74c3c", "EXECUTOR": "#3498db", "REACTIVE": "#2ecc71", "MEMORY": "#f1c40f", "CRITIC": "#9b59b6"}
    
    # X Axis Ticks
    for i in range(0, 11):
        val = (max_tokens / 10) * i
        x = margin + (val / max_tokens) * (width - 2 * margin)
        svg_content.append(line(x, height - margin, x, height - margin + 5, "black"))
        svg_content.append(text(x, height - margin + 20, f"{int(val)}", 10))
    
    # Y Axis Ticks
    for i in range(0, 11):
        val = (max_time / 10) * i
        y = (height - margin) - (val / max_time) * (height - 2 * margin)
        svg_content.append(line(margin - 5, y, margin, y, "black"))
        svg_content.append(text(margin - 25, y + 4, f"{val:.1f}", 10, anchor="end"))

    # Points
    for d in data:
        x = margin + (d['total_tokens'] / max_tokens) * (width - 2 * margin)
        y = (height - margin) - (d['time_taken'] / max_time) * (height - 2 * margin)
        col = colors.get(d['agent_type'], "gray")
        svg_content.append(circle(x, y, 6, col, "white", 0.7))

    # Legend
    legend_x = width - 120
    legend_y = margin
    for i, (atype, col) in enumerate(colors.items()):
        svg_content.append(circle(legend_x, legend_y + i*20, 6, col))
        svg_content.append(text(legend_x + 15, legend_y + i*20 + 4, atype, 10, anchor="start"))

    with open(output_path, 'w') as f:
        f.write(create_svg(width, height, "\n".join(svg_content)))
    print(f"Saved {output_path}")

def generate_bar(data, output_path):
    # Activity Volume
    width, height = 600, 400
    margin = 60
    
    if not data:
        return

    counts = {}
    for d in data:
        counts[d['agent_type']] = counts.get(d['agent_type'], 0) + 1
    
    sorted_cats = sorted(counts.keys())
    max_count = max(counts.values()) * 1.2
    
    svg_content = []
    
    # Axis
    svg_content.append(line(margin, height - margin, width - margin, height - margin, "black", 2)) # X
    svg_content.append(line(margin, margin, margin, height - margin, "black", 2)) # Y
    
    svg_content.append(text(width/2, height - 10, "Type d'Agent", 14))
    svg_content.append(text(20, height/2, "Nombre d'appels", 14, rotate=-90))
    svg_content.append(text(width/2, 30, "Volume d'Activité par Agent", 18))

    bar_width = (width - 2 * margin) / len(sorted_cats) * 0.6
    spacing = (width - 2 * margin) / len(sorted_cats)
    
    colors = ["#3498db", "#e74c3c", "#2ecc71", "#f1c40f", "#9b59b6"]

    # Y Axis Ticks
    for i in range(0, 6):
        val = (max_count / 5) * i
        y = (height - margin) - (val / max_count) * (height - 2 * margin)
        svg_content.append(line(margin - 5, y, margin, y, "black"))
        svg_content.append(text(margin - 10, y + 4, f"{int(val)}", 10, anchor="end"))

    for i, cat in enumerate(sorted_cats):
        count = counts[cat]
        bar_h = (count / max_count) * (height - 2 * margin)
        x = margin + i * spacing + spacing/2 - bar_width/2
        y = (height - margin) - bar_h
        
        svg_content.append(rect(x, y, bar_width, bar_h, colors[i % len(colors)], "black"))
        svg_content.append(text(x + bar_width/2, height - margin + 20, cat, 10))
        svg_content.append(text(x + bar_width/2, y - 5, str(count), 10))

    with open(output_path, 'w') as f:
        f.write(create_svg(width, height, "\n".join(svg_content)))
    print(f"Saved {output_path}")

def generate_cost_bar(data, output_path):
    # Cost per Provider
    width, height = 600, 400
    margin = 80
    
    if not data:
        return

    costs = {}
    tokens = {}
    for d in data:
        costs[d['provider']] = costs.get(d['provider'], 0) + d['cost']
        tokens[d['provider']] = tokens.get(d['provider'], 0) + d['tokens']
    
    # Decide what to plot: Cost or Tokens (if cost is 0)
    total_cost = sum(costs.values())
    use_cost = total_cost > 0.0001
    
    values = costs if use_cost else tokens
    label = "Coût ($)" if use_cost else "Total Tokens"
    title = "Coût par Provider" if use_cost else "Volume de Tokens par Provider"
    
    sorted_cats = sorted(values.keys())
    max_val = max(values.values()) * 1.2 if values else 1
    
    svg_content = []
    
    svg_content.append(line(margin, height - margin, width - margin, height - margin, "black", 2)) # X
    svg_content.append(line(margin, margin, margin, height - margin, "black", 2)) # Y
    
    svg_content.append(text(width/2, height - 10, "Provider", 14))
    svg_content.append(text(20, height/2, label, 14, rotate=-90))
    svg_content.append(text(width/2, 30, title, 18))

    if not sorted_cats:
        with open(output_path, 'w') as f:
            f.write(create_svg(width, height, text(width/2, height/2, "No Data")))
        return

    bar_width = (width - 2 * margin) / len(sorted_cats) * 0.6
    spacing = (width - 2 * margin) / len(sorted_cats)
    
    # Y Axis Ticks
    for i in range(0, 6):
        val = (max_val / 5) * i
        y = (height - margin) - (val / max_val) * (height - 2 * margin)
        svg_content.append(line(margin - 5, y, margin, y, "black"))
        fmt = f"{val:.4f}" if use_cost else f"{int(val)}"
        svg_content.append(text(margin - 10, y + 4, fmt, 10, anchor="end"))

    for i, cat in enumerate(sorted_cats):
        val = values[cat]
        bar_h = (val / max_val) * (height - 2 * margin)
        x = margin + i * spacing + spacing/2 - bar_width/2
        y = (height - margin) - bar_h
        
        svg_content.append(rect(x, y, bar_width, bar_h, "teal", "black"))
        svg_content.append(text(x + bar_width/2, height - margin + 20, cat, 10, rotate=15))
        fmt = f"{val:.4f}" if use_cost else f"{int(val)}"
        svg_content.append(text(x + bar_width/2, y - 5, fmt, 10))

    with open(output_path, 'w') as f:
        f.write(create_svg(width, height, "\n".join(svg_content)))
    print(f"Saved {output_path}")

# --- Main ---

if __name__ == "__main__":
    tel_data = load_telemetrics()
    or_data = load_openrouter()
    
    generate_scatter(tel_data, os.path.join(OUTPUT_DIR, "latency_vs_tokens.svg"))
    generate_bar(tel_data, os.path.join(OUTPUT_DIR, "agent_activity.svg"))
    generate_cost_bar(or_data, os.path.join(OUTPUT_DIR, "provider_costs.svg"))
    print("Done generating SVGs.")