import math
from app.ai.engine.geometry_curriculum import generate
from app.ai.engine.geometry_diagrams import triangle_with_base_height, validate_geometry_diagram


def test_altitude_is_explicit_and_perpendicular():
    d = triangle_with_base_height(12, 5)
    assert d['altitudes'] == [['C', 'H']]
    assert d['dashed_segments'] == [['C', 'H']]
    assert not validate_geometry_diagram(d)
    p = d['points']
    assert math.isclose(p['C'][0], p['H'][0])
    assert math.isclose(p['C'][1] - p['H'][1], 5)


def test_ten_previously_unlinked_geometry_topics_generate_questions():
    topics = [
        (10, 'hinh_hoc_co_ban_10'), (10, 'tam_giac_tu_giac_10'),
        (10, 'duong_tron_co_ban_10'), (10, 'he_thuc_luong_van_dung_10'),
        (10, 'toa_do_hinh_hoc_10'), (10, 'chung_minh_hinh_hoc_10'),
        (11, 'phep_bien_hinh_co_ban_11'), (11, 'nhan_biet_hinh_khong_gian_11'),
        (12, 'hinh_khoi_va_the_tich_co_ban_12'), (12, 'hinh_hoc_oxyz_van_dung_12'),
    ]
    for grade, topic in topics:
        q = generate(grade, topic, 'medium', f'{topic}_Khám phá_stage2')
        assert q and q.get('question') and q.get('answer') is not None
        if q.get('diagram'):
            assert not validate_geometry_diagram(q['diagram'])


def test_geometry_diagram_uses_correct_auxiliary_lines_and_diameter():
    from app.ai.engine.topic_expansion import geometry_diagram

    altitude = geometry_diagram('hinh_hoc_10', 'Tam giác ABC có đường cao AH.', '5')
    p = altitude['points']
    assert altitude['right_angle'] == 'H'
    assert altitude['altitudes'] == [['A', 'H']]
    assert math.isclose(p['A'][0], p['H'][0])
    assert math.isclose(p['A'][1] - p['H'][1], 7)
    assert not validate_geometry_diagram(altitude)

    median = geometry_diagram('hinh_hoc_10', 'Tam giác ABC có trung tuyến AM, M là trung điểm BC.', '5')
    assert median['points']['M'] == [4.5, 0.0]
    assert ['A', 'M'] in median['segments']

    bisector = geometry_diagram('hinh_hoc_10', 'Tam giác ABC có AD là đường phân giác góc A.', '5')
    q = bisector['points']
    ab = math.dist(q['A'], q['B'])
    ac = math.dist(q['A'], q['C'])
    bd = math.dist(q['B'], q['D'])
    dc = math.dist(q['D'], q['C'])
    assert math.isclose(bd / dc, ab / ac, rel_tol=1e-9)

    diameter = geometry_diagram('hinh_hoc_10', 'Đường tròn tâm O có đường kính AB=10 cm. Tính bán kính.', '5')
    assert diameter['radius'] == 5
    assert diameter['diameter'] == 10
    assert math.isclose(math.dist(diameter['points']['A'], diameter['points']['B']), 10)
