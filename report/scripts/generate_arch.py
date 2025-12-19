import os

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "../images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_svg(width, height, content):
    return f'<svg version="1.1" width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" style="font-family: sans-serif; background: white;">\n{content}\n</svg>'

def rect(x, y, w, h, fill, stroke="black", stroke_width=2, rx=5):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" rx="{rx}" />'

def text(x, y, content, size=12, fill="black", anchor="middle", weight="normal"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{content}</text>'

def arrow(x1, y1, x2, y2, stroke="black", width=2):
    # Simple line with marker
    # Note: SVG markers are annoying to define inline without defs, so I'll just draw lines
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{width}" marker-end="url(#arrow)" />'

def defs():
    return '''<defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="black" />
    </marker>
  </defs>'''

def generate_arch():
    width, height = 800, 600
    content = []
    content.append(defs())

    # Nodes
    # User -> Front -> Back -> Planner -> Executor/Vision -> OpenRouter
    
    # Coordinates
    cx = width / 2
    
    y_user = 50
    y_front = 150
    y_back = 250
    y_planner = 350
    y_agents = 450
    y_or = 550
    
    box_w, box_h = 160, 60
    
    # Draw Nodes
    
    # User
    content.append(rect(cx - box_w/2, y_user, box_w, box_h, "#e0e0e0"))
    content.append(text(cx, y_user + 35, "User", 16, weight="bold"))
    
    # Frontend
    content.append(rect(cx - box_w/2, y_front, box_w, box_h, "#bbdefb"))
    content.append(text(cx, y_front + 25, "Frontend", 14, weight="bold"))
    content.append(text(cx, y_front + 45, "(React + Vite)", 12))
    
    # Backend
    content.append(rect(cx - box_w/2, y_back, box_w, box_h, "#c8e6c9"))
    content.append(text(cx, y_back + 25, "Backend", 14, weight="bold"))
    content.append(text(cx, y_back + 45, "(FastAPI)", 12))
    
    # Planner
    content.append(rect(cx - box_w/2, y_planner, box_w, box_h, "#ffe0b2"))
    content.append(text(cx, y_planner + 25, "Planner", 14, weight="bold"))
    content.append(text(cx, y_planner + 45, "(Orchestrator)", 12))
    
    # Agents (Executor & Vision)
    x_exec = cx - 150
    x_vis = cx + 150
    
    content.append(rect(x_exec - box_w/2, y_agents, box_w, box_h, "#fff9c4"))
    content.append(text(x_exec, y_agents + 35, "Executor", 14, weight="bold"))
    
    content.append(rect(x_vis - box_w/2, y_agents, box_w, box_h, "#e1bee7"))
    content.append(text(x_vis, y_agents + 35, "Vision Agent", 14, weight="bold"))
    
    # OpenRouter
    content.append(rect(cx - box_w/2, y_or, box_w, box_h, "#cfd8dc"))
    content.append(text(cx, y_or + 35, "OpenRouter API", 14, weight="bold"))
    
    # Edges
    
    # User -> Front
    content.append(arrow(cx, y_user + box_h, cx, y_front))
    content.append(text(cx + 10, (y_user + y_front)/2 + 20, "HTTP", 10, anchor="start"))
    
    # Front -> Back
    content.append(arrow(cx, y_front + box_h, cx, y_back))
    content.append(text(cx + 10, (y_front + y_back)/2 + 20, "JSON Stream", 10, anchor="start"))
    
    # Back -> Planner
    content.append(arrow(cx, y_back + box_h, cx, y_planner))
    
    # Planner -> Executor
    content.append(arrow(cx, y_planner + box_h, x_exec, y_agents))
    
    # Planner -> Vision
    content.append(arrow(cx, y_planner + box_h, x_vis, y_agents))
    
    # Executor -> OpenRouter
    content.append(arrow(x_exec, y_agents + box_h, cx - 20, y_or))
    
    # Vision -> OpenRouter
    content.append(arrow(x_vis, y_agents + box_h, cx + 20, y_or))
    
    # Planner -> OpenRouter (Direct)
    # content.append(arrow(cx, y_planner + box_h, cx, y_or)) # Overlaps, skip for clarity
    
    
    svg_str = create_svg(width, 700, "\n".join(content))
    
    with open(os.path.join(OUTPUT_DIR, "architecture.svg"), "w") as f:
        f.write(svg_str)
    print(f"Generated {os.path.join(OUTPUT_DIR, 'architecture.svg')}")

if __name__ == "__main__":
    generate_arch()
