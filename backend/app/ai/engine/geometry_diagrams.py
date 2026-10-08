"""Structured, deterministic geometry diagrams.

The frontend renders these descriptions as SVG.  Coordinates are mathematical
coordinates rather than a stock illustration, so the labels/lengths/angles are
bound to the actual generated data.
"""
from __future__ import annotations


def triangle_3_4_5(a=3, b=4, labels=("A", "B", "C")):
    # A=(0,0), B=(b,0), C=(0,a). AB=b, AC=a, BC=sqrt(a^2+b^2).
    return {
        "type": "geometry",
        "shape": "right_triangle",
        "points": {labels[0]: [0, 0], labels[1]: [b, 0], labels[2]: [0, a]},
        "segments": [[labels[0], labels[1]], [labels[1], labels[2]], [labels[2], labels[0]]],
        "labels": labels,
        "right_angle": labels[0],
        "measurements": [
            {"from": labels[0], "to": labels[1], "text": f"{b}"},
            {"from": labels[0], "to": labels[2], "text": f"{a}"},
        ],
        "caption": "Tam giác vuông với hai cạnh góc vuông được cho.",
    }


def rectangle(width, height, labels=("A", "B", "C", "D")):
    return {
        "type": "geometry",
        "shape": "polygon",
        "points": {
            labels[0]: [0, 0], labels[1]: [width, 0],
            labels[2]: [width, height], labels[3]: [0, height],
        },
        "segments": [[labels[0], labels[1]], [labels[1], labels[2]], [labels[2], labels[3]], [labels[3], labels[0]]],
        "labels": labels,
        "measurements": [
            {"from": labels[0], "to": labels[1], "text": str(width)},
            {"from": labels[0], "to": labels[3], "text": str(height)},
        ],
        "caption": "Hình chữ nhật theo đúng kích thước dữ kiện.",
    }


def coordinate_rectangle(x1, y1, x2, y2):
    labels = ("A", "B", "C", "D")
    return {
        "type": "geometry",
        "shape": "coordinate_polygon",
        "points": {
            "A": [x1, y1], "B": [x2, y1], "C": [x2, y2], "D": [x1, y2]
        },
        "segments": [["A", "B"], ["B", "C"], ["C", "D"], ["D", "A"]],
        "labels": labels,
        "axes": True,
        "caption": "Mô hình khu đất trên mặt phẳng tọa độ.",
    }


def circle(radius, center=(0, 0)):
    return {
        "type": "geometry",
        "shape": "circle",
        "center": [center[0], center[1]],
        "radius": radius,
        "labels": ["O"],
        "measurements": [{"from": "O", "to": "R", "text": str(radius)}],
        "caption": "Đường tròn với bán kính theo dữ kiện đề bài.",
    }
