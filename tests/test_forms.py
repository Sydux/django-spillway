from django.test import SimpleTestCase, TestCase
from django.forms import fields
from django.contrib.gis import geos

from spillway import forms
from .models import Location


class PKeyQuerySetForm(forms.QuerySetForm):
    pk = fields.IntegerField()


class GeometryQueryFormTestCase(SimpleTestCase):
    def test_data(self):
        form = forms.GeometryQueryForm({'srs': 3857})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['srs'].srid, 3857)


class SpatialQueryFormTestCase(SimpleTestCase):
    def _assert_form_data(self, form, key, expected):
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.keys(), expected.keys())
        self.assertTrue(form.cleaned_data[key].equals_exact(expected[key]))
        self.assertEqual(form.cleaned_data[key].srid, 4326)

    def test_data(self):
        data = {'bbox': '-120,38,-118,42'}
        poly = geos.Polygon.from_bbox(data['bbox'].split(','))
        key = 'bboverlaps'
        expected = {key: poly}
        form = forms.SpatialQueryForm(data)
        self._assert_form_data(form, key, expected)

    def test_intersects(self):
        key = 'intersects'
        poly = geos.Polygon.from_bbox((0, 0, 10, 10))
        expected = {key: poly}
        data = {key: poly.geojson}
        form = forms.SpatialQueryForm(data)
        self._assert_form_data(form, key, expected)

    def test_intersects_invalid(self):
        data = {'intersects': '{"type":"Point","coordinates":[0]}'}
        form = forms.SpatialQueryForm(data)
        self.assertFalse(form.is_valid())


class QuerySetFormTestCase(TestCase):
    def test_queryset(self):
        Location.add_buffer((5, 7), 2)
        qs = Location.objects.all()
        form = PKeyQuerySetForm({'pk': '1'}, queryset=qs)
        self.assertEqual(form.query()[0].pk, 1)

    def test_missing_queryset(self):
        form = PKeyQuerySetForm({'pk': '1'})
        self.assertRaises(TypeError, form.query)
