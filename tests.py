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
		['examples/person_ex1.json', test_person],
		['examples/meeting_ex1.json', test_meeting],
		['examples/paper_ex1.json', test_paper]
		# TODO: committee, organisation, agendaitem, vote, document, location
	]

	for example_file, test_function in testcases:
		test_function(load_example(example_file))

def load_example(filename):
	return json.load(codecs.open(filename, 'r', 'utf-8-sig'))

def is_text(s):
	return isinstance(s, unicode)

def is_list(l):
	return isinstance(l, list)

def is_integer(i):
	return isinstance(i, int)

def is_float(f):
	return isinstance(f, float)

def is_regionalschluessel(s):
	return is_text(s) and re.match("^[0-9]{12}$", s)

def is_url(u):
	return is_text(u) and re.match('^(http|https)://.*$', u)

def is_email(e):
	# TODO: more specific email regexp? / http://davidcel.is/blog/2012/09/06/stop-validating-email-addresses-with-regex/
	return is_text(e) and re.match('^.*@.*$', e)

def is_datetime(d):
	# TODO: check for ISO 8601 / RFC 3339?
	return is_text(d) and re.match('^[0-9]{4}-[0-9]{2}-[0-9]{2}.*', d)

def is_date(d):
	# TODO: check for ISO 8601 / RFC 3339?
	return is_text(d) and re.match('^[0-9]{4}-[0-9]{2}-[0-9]{2}$', d)

def is_phonenumber(p):
	# TODO: check for ITU E.123 or DIN 5008?
	return is_text(p)

def is_relation_with_optional_dates(r):
	assert "id" in r and is_text(r["id"])
	if "start" in r:
		assert is_date(r["start"])
	if "end" in r:
		assert is_date(r["end"])
	return True

def is_organisation_relation(o):
	return is_relation_with_optional_dates(o)

def is_committee_relation(c):
	return is_relation_with_optional_dates(c)

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

def test_meeting(data):
	# required fields:
	assert "id" in data and is_text(data["id"])
	assert "start" in data and (is_date(data["start"]) or is_datetime(data["start"]))
	assert "last_modified" in data and is_datetime(data["last_modified"])
	assert "committees" in data and is_list(data["committees"])
	assert len(data["committees"]) >= 1
	for c in data["committees"]:
		assert is_text(c)
	# NOTE: Meiner Auffassung nach sollte das People-Feld optional sein. Außerdem macht es für zukünftige Sitzungen nicht unbedingt Sinn bzw. ist dann zumindest leer.
	assert "people" in data and is_list(data["people"])
	for p in data["people"]:
		assert is_text(p)
	# optional fields:
	if "sequence_number" in data:
		assert is_integer(data["sequence_number"])
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

def test_paper(data):
	# required fields:
	assert "id" in data and is_text(data["id"])
	assert "date" in data and is_date(data["date"])
	assert "type" in data and is_text(data["type"])
	assert "last_modified" in data and is_datetime(data["last_modified"])
	assert "main_document" in data and is_text(data["main_document"])
	# optional fields:
	if "attachments" in data:
		assert is_list(data["attachments"])
		for a in data["attachments"]:
			assert is_text(a)
	if "committees" in data:
		assert is_list(data["committees"])
		for c in data["committees"]:
			assert is_text(c)
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
		assert is_list(data["related_papers"])
		for rp in data["related_papers"]:
			# NOTE: An dieser Stelle ist noch nicht möglich festzulegen, welche Beziehung die referenzierte Drucksache zur aktuellen hat.
			assert is_text(rp)
	if "consultations" in data:
		assert is_list(data["consultations"])
		for c in data["consultations"]:
			assert "meeting" in c and is_text(c["meeting"])
			assert "agendaitem" in c and is_text(c["agendaitem"])
			if "role" in c:
				assert is_text(c["role"])

if __name__ == "__main__":
	main()

