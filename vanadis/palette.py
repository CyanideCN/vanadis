import numpy as np

from vanadis.colormap import Colormap, Segment

def parse_palette(file):
    lines = []
    vals = []
    red = []
    green = []
    blue = []
    last_color = None
    transit_flag = False
    with open(file, "r") as f:
        for line in f:
            if not line.lower().startswith("color:"):
                continue
            l = line.lower().lstrip("color: ").strip()
            lines.append(l)
    lines.sort(key=lambda x: float(x.split(" ")[0]))
    color_len = len(lines)
    for idx, l in enumerate(lines):
        segs = [i for i in l.split(" ") if i]
        vals.append(float(segs[0]))
        current_color = tuple(int(i) / 255 for i in segs[1:4])
        if color_len - idx == 2:
            transit_flag = transit_flag if transit_flag else False
        if not isinstance(last_color, tuple) and len(segs) == 3:
            red.append((0, current_color[0]))
            green.append((0, current_color[1]))
            blue.append((0, current_color[2]))
            last_color = current_color
        else:
            if len(segs) == 7 or color_len - idx == 2:
                transit_color = tuple(int(i) / 255 for i in segs[4:7])
                if transit_flag:
                    red.append((last_color[0], current_color[0]))
                    green.append((last_color[1], current_color[1]))
                    blue.append((last_color[2], current_color[2]))
                else:
                    red.append((current_color[0], current_color[0]))
                    green.append((current_color[1], current_color[1]))
                    blue.append((current_color[2], current_color[2]))
                last_color = transit_color
                transit_flag = True
            else:
                red.append((current_color[0], current_color[0]))
                green.append((current_color[1], current_color[1]))
                blue.append((current_color[2], current_color[2]))
                last_color = current_color
                transit_flag = False
    norm_array = (np.array(vals) - vals[0]) / (vals[-1] - vals[0])
    cdict = {"red": [], "green": [], "blue": []}
    for idx in range(len(norm_array)):
        cdict["red"].append((norm_array[idx],) + red[idx])
        cdict["green"].append((norm_array[idx],) + green[idx])
        cdict["blue"].append((norm_array[idx],) + blue[idx])
    return Colormap(segmentdata=Segment(cdict))