import pytest
from app.ai.engine.geometry_diagrams import regular_prism_projection, triangular_prism_by_dimensions, pyramid_by_base_height, validate_geometry_diagram

@pytest.mark.parametrize('n',[3,4,5,6,8])
def test_regular_prism_has_exact_3d_vertices(n):
    d=regular_prism_projection(n,2,4)
    assert len(d['coordinates_3d']) == 2*n
    assert d['solid_dimensions']['height'] == 4
    assert not validate_geometry_diagram(d)

def test_triangular_prism_dimensions_are_preserved():
    d=triangular_prism_by_dimensions(3,4,5,7)
    assert len(d['coordinates_3d']) == 6
    assert d['solid_dimensions']['length'] == 7
    assert not validate_geometry_diagram(d)

def test_pyramid_dimensions_are_preserved():
    d=pyramid_by_base_height(4,2,5)
    assert len(d['coordinates_3d']) == 5
    assert d['solid_dimensions']['height'] == 5
    assert not validate_geometry_diagram(d)

def test_invalid_prism_rejected():
    with pytest.raises(ValueError): regular_prism_projection(2,2,3)

def test_invalid_triangle_prism_rejected():
    with pytest.raises(ValueError): triangular_prism_by_dimensions(1,2,5,4)
