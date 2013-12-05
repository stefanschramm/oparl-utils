#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2013, Stefan Schramm <mail@stefanschramm.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import codecs
import re

def main():
	testcases = [
		['examples/body_ex1.json', test_body],
		['examples/committee_ex1.json', test_committee],
		['examples/person_ex1.json', test_person],
		['examples/organisation_ex1.json', test_organisation],
		['examples/meeting_ex1.json', test_meeting],
		['examples/agendaitem_ex1.json', test_agendaitem],
		['examples/vote_ex1.json', test_vote],
		['examples/vote_ex2.json', test_vote],
		['examples/paper_ex1.json', test_paper],
		['examples/document_ex1.json', test_document],
		['examples/location_ex1.json', test_location]
	]

	for example_file, test_function in testcases:
		test_function(load_example(example_file))

	# TODO: implement test of referential integrity across all example objects (e.g. if a meeting references a person-id, check if there is a person with this id)

def load_example(filename):
	return json.load(codecs.open(filename, 'r', 'utf-8-sig'))

# type checks

def is_text(s):
	return isinstance(s, unicode)

def is_int(i):
	return isinstance(i, int)

def is_float(f):
	return isinstance(f, float)

def is_bool(b):
	return isinstance(b, bool)

def is_list(l):
	return isinstance(l, list)

def is_list_of_texts(l):
	if not is_list(l):
		return False
	for entry in l:
		if not is_text(entry):
			return False
	return True

def is_regionalschluessel(s):
	return is_text(s) and re.match("^[0-9]{12}$", s)

def is_url(u):
	# NOTE: In Spzifikationsbeschreibung festlegen, ob zusätzlich zu http auch https erlaubt ist?
	return is_text(u) and re.match('^(http|https)://.*$', u)

def is_email(e):
	# TODO: more specific email regexp? / http://davidcel.is/blog/2012/09/06/stop-validating-email-addresses-with-regex/
	return is_text(e) and re.match('^.*@.*$', e)

def is_datetime(d):
	# http://www.w3.org/TR/NOTE-datetime (Complete date plus hours, minutes and seconds) - subset of ISO 8601
	# TODO: plausability check?
	return is_text(d) and re.match('^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\+[0-9]{2}:[0-9]{2}$', d)

def is_date(d):
	# http://www.w3.org/TR/NOTE-datetime (Complete date) - subset of ISO 8601
	# TODO: plausability check?
	return is_text(d) and re.match('^[0-9]{4}-[0-9]{2}-[0-9]{2}$', d)

def is_phonenumber(p):
	# TODO: check for ITU E.123 / DIN 5008 / http://www.ietf.org/rfc/rfc3966.txt ?
	return is_text(p)

def is_sha1_checksum(c):
	return is_text(c) and re.match("^[0-9a-f]{40}$", c)

def is_relation_with_optional_dates(r):
	if not "id" in r and is_text(r["id"]):
		return False
	if "start" in r:
		if not is_date(r["start"]):
			return False
	if "end" in r:
		if not is_date(r["end"]):
			return False
	return True

def is_organisation_relation(o):
	return is_relation_with_optional_dates(o)

def is_committee_relation(c):
	return is_relation_with_optional_dates(c)

def is_list_of_geojson_positions(l):
	if not is_list(l):
		return False
	for p in l:
		if not is_geojson_position(p):
			return False
	return True

def is_geojson_position(p):
	if not is_list(p):
		return False
	if len(p) != 2:
		return False
	return True

def is_geojson_geometry(g):
	if "type" not in g:
		return False
	if g["type"] not in ["Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon", "GeometryCollection"]:
		return False
	if g["type"] == "Point":
		if "coordinates" not in g:
			return False
		if not is_geojson_position(g["coordinates"]):
			return False
	elif g["type"] in ["LineString", "MultiPoint"]:
		if "coordinates" not in g:
			return False
		if not is_list_of_geojson_positions(g["coordinates"]):
			return False
	elif g["type"] in ["Polygon", "MultiLineString"]:
		if "coordinates" not in g:
			return False
		if not is_list(g["coordinates"]):
			return False
		for p in g["coordinates"]:
			if not is_list_of_geojson_positions(p):
				return False
	else:
		# TODO: Not yet implemented: MultiPolygon, GeometryCollection
		return False
	return True

# tests for object types

def test_body(data):
	# required fields:
	assert "id" in data and is_text(data["id"])
	assert "name" in data and is_text(data["name"])
	# optional fields:
	if "regionalschluessel" in data:
		assert is_regionalschluessel(data["regionalschluessel"])
	if "gnd_url" in data:
		assert is_url(data["gnd_url"])
	if "url" in data:
		assert is_url(data["url"])
	if "license_url" in data:
		assert is_url(data["license_url"])
	if "operator_contact" in data:
		assert is_text(data["operator_contact"])

def test_committee(data):
	# required fields:
	assert "id" in data and is_text(data["id"])
	assert "body" in data and is_text(data["body"])
	assert "name" in data and is_text(data["name"])
	assert "last_modified" in data and is_datetime(data["last_modified"])
	# optional fields:
	if "short_name" in data:
		assert is_text(data["short_name"])

def test_person(data):
	# required fields:
	assert "id" in data and is_text(data["id"])
	assert "first_name" in data and is_text(data["first_name"])
	assert "last_name" in data and is_text(data["last_name"])
	# optional fields:
	if "academic_title" in data:
		assert is_text(data["academic_title"])
	if "sex" in data:
		assert data["sex"] in ["F", "M", "O"]
	if "profession" in data:
		assert is_text(data["profession"])
	if "email" in data:
		assert is_email(data["email"])
	if "phone" in data:
		assert is_phonenumber(data["phone"])
	if "fax" in data:
		assert is_phonenumber(data["fax"])
	if "address" in data:
		assert is_text(data["address"])
	if "last_modified" in data:
		assert is_datetime(data["last_modified"])
	if "organisations" in data:
		assert is_list(data["organisations"])
		for o in data["organisations"]:
			assert is_organisation_relation(o)
	if "committees" in data:
		assert is_list(data["committees"])
		for c in data["committees"]:
			assert is_committee_relation(c)

def test_organisation(data):
	# required fields:
	assert "id" in data and is_text(data["id"])
	assert "body" in data and is_text(data["body"])
	assert "name" in data and is_text(data["name"])
	assert "last_modified" in data and is_datetime(data["last_modified"])

def test_meeting(data):
	# required fields:
	assert "id" in data and is_text(data["id"])
	assert "start" in data and (is_date(data["start"]) or is_datetime(data["start"]))
	assert "last_modified" in data and is_datetime(data["last_modified"])
	assert "committees" in data and is_list(data["committees"])
	assert len(data["committees"]) >= 1
	assert is_list_of_texts(data["committees"])
	# NOTE: Meiner Auffassung nach sollte das people-Feld optional sein. Außerdem macht es für in der Zukunft liegende Sitzungen keinen Sinn bzw. ist dann zumindest noch leer.
	assert "people" in data and is_list(data["people"])
	assert is_list_of_texts(data["people"])
	# optional fields:
	if "sequence_number" in data:
		assert is_int(data["sequence_number"])
	if "end" in data:
		assert is_date(data["end"]) or is_datetime(data["end"])
	if "address" in data:
		assert is_text(data["address"])
	if "invitation" in data:
		assert is_text(data["invitation"])
	if "result_minutes" in data:
		assert is_text(data["result_minutes"])
	if "verbatim_minutes" in data:
		assert is_text(data["verbatim_minutes"])
	if "attachments" in data:
		assert is_list(data["attachments"])

def test_agendaitem(data):
	# required fields:
	assert "identifier" in data and is_text(data["identifier"])
	assert "public" in data and is_bool(data["public"])
	assert "title" in data and is_text(data["title"])
	assert "last_modified" in data and is_datetime(data["last_modified"])
	assert "meeting" in data and is_text(data["meeting"])
	# optional fields:
	# NOTE/TODO: Einheitliche Werte für result definieren?
	if "result" in data:
		assert is_text(data["result"])
	# NOTE: result_details fehlt im Beispiel
	if "result_details" in data:
		assert is_text(data["result_details"])
	if "resolution_text" in data:
		assert is_text(data["resolution_text"])
	if "votings" in data:
		assert is_list(data["votings"])
		# TODO: Führt hier zu AssertionError, da in diesem Beispiel sowohl "organisations", als auch "people" auftreten.
		#for v in data["votings"]:
		#	test_vote(v)
	if "people_absent" in data:
		assert is_list_of_texts(data["people_absent"])

def test_vote(data):
	# required fields:
	assert "sum" in data and is_int(data["sum"])
	assert "vote" in data and data["vote"] in ["DAFUER", "DAGEGEN", "ENTHALTUNG"]
	# either "people" or "organisations" key is required, but never both:
	assert "people" in data or "organisations" in data
	assert not ("people" in data and "organisations" in data)
	if "people" in data:
		assert is_list(data["people"]) and is_list_of_texts(data["people"])
		# TODO:
		# Spezifikationsbeschreibung für diesen Fall ist irritierend bzw. bzgl. des Beispiels widersprüchlich:
		# "Es wird entweder genau eine Person [...] referenziert"
		# "Gehört die Stimmabgabe zu einer Person, ist der Wert immer 1"
		assert data["sum"] == len(data["people"])
	if "organisations" in data:
		assert is_list(data["organisations"]) and is_list_of_texts(data["organisations"])

def test_paper(data):
	# required fields:
	assert "id" in data and is_text(data["id"])
	assert "date" in data and is_date(data["date"])
	assert "type" in data and is_text(data["type"])
	assert "last_modified" in data and is_datetime(data["last_modified"])
	assert "main_document" in data and is_text(data["main_document"])
	# NOTE: In der Spezifikation enthält main_document und attachments scheinbar Dateinamen (3002.pdf) - das sollten wohl eigentlich eher die id sein.
	# optional fields:
	if "attachments" in data:
		assert is_list(data["attachments"]) and is_list_of_texts(data["attachments"])
	if "committees" in data:
		assert is_list(data["committees"]) and is_list_of_texts(data["committees"])
	if "creators" in data:
		assert is_list(data["creators"])
		for c in data["creators"]:
			assert "typ" in c and c["typ"] in ["Organisation", "Person"]
			assert "id" in c and is_text(c["id"])
	if "locations" in data:
		assert is_list(data["locations"])
		for l in data["locations"]:
			# TODO:
			# An dieser Stelle scheint die Spezifikation widersprüchlich zu sein.
			# Im Kapitel "Ort (location)" wird auf GeoJSON verwiesen, das Beispiel jedoch nutzt eine andere Datenstruktur (Map mit "lat" und "lon" statt "coordinates"-key mit Liste).
			assert "description" in l and is_text(l["description"])
			assert "lat" in l and is_float(l["lat"])
			assert "lon" in l and is_float(l["lon"])
	if "related_papers" in data:
		assert is_list(data["related_papers"]) and is_list_of_texts(data["related_papers"])
		# NOTE: An dieser Stelle ist es noch nicht möglich festzulegen, welche Beziehung die referenzierte Drucksache zur aktuellen hat.
	if "consultations" in data:
		assert is_list(data["consultations"])
		for c in data["consultations"]:
			assert "meeting" in c and is_text(c["meeting"])
			assert "agendaitem" in c and is_text(c["agendaitem"])
			if "role" in c:
				assert is_text(c["role"])

def test_document(data):
	# required fields:
	assert "id" in data and is_text(data["id"])
	assert "name" in data and is_text(data["name"])
	assert "mime_type" in data and is_text(data["mime_type"])
	# TODO: Spezifikationsbeschreibung spricht bei "date" von datum, im Beispiel steht jedoch ein Zeitstempel (datetime) im Feld.
	assert "date" in data and is_datetime(data["date"])
	assert "last_modified" in data and is_datetime(data["last_modified"])
	# NOTE: In Spezifikationsbeschreibung SHA1-Prüfsummenformat festlegen auf 40stellig hexadezimal mit Kleinbuchstaben?
	assert "sha1_checksum" in data and is_sha1_checksum(data["sha1_checksum"])
	assert "url" in data and is_url(data["url"])
	# NOTE: Spezifikationsbeschreibung uneindeutig, ob "text" optional
	assert "text" in data and is_text(data["text"])
	# optional fields:
	if "master" in data:
		assert is_text(data["master"])
	# NOTE: Es fehlt die Prüfung, ob das Dokument von mindestens einer Drucksache referenziert wird (als Hauptdokument oder Anlage).

def test_location(data):
	# required fields:
	assert "last_modified" in data and is_datetime(data["last_modified"])
	# optional fields:
	if "description" in data:
		assert is_text(data["description"])
	if "geometry" in data:
		assert is_geojson_geometry(data["geometry"])

if __name__ == "__main__":
	main()

