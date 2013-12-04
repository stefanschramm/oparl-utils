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

import urllib
import re
import os

url = 'https://raw.github.com/OParl/specs/master/dokument/master/chapter_02.md'
target_dir = 'examples'

def main():

	if not os.path.isdir(target_dir):
		os.mkdir(target_dir)

	data = urllib.urlopen(url).read()
	f = None
	for line in data.split("\n"):

		if f == None:
			m = re.match('^~~~~~  \{\#(?P<name>[a-z0-9_]+) \.(?P<extension>[a-z0-9]+)\}$', line.strip())
			if m:
				# open file
				filename = "%s.%s" % (m.group("name"), m.group("extension"))
				f = open(target_dir + os.sep + filename, "w")
				continue
		else:
			m = re.match('^~~~~~$', line.strip())
			if m:
				f.close()
				f = None
				continue
			f.write(line + "\n")

if __name__ == "__main__":
	main()
