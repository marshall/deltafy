#!/usr/bin/env python
# deltafy unit tests 
#
# Author: Marshall Culpepper
# Licensed under the Apache Public License v2 (see LICENSE.txt)

import os, sys, unittest, shutil, datetime, time

top_dir = os.path.abspath("..")
tests_dir = os.path.join(top_dir, "tests", "tests_dir")
sys.path.append(top_dir)
from deltafy import Deltafy, Delta

if os.path.exists(Deltafy.get_database_path()):
	os.unlink(Deltafy.get_database_path())

def suite():
	tests = ['test_initial_pass', 'test_second_pass', 'test_file_modified',
		'test_file_created', 'test_file_deleted', 'test_files_modified', 'test_exclude_files']
	return unittest.TestSuite(map(DeltafyTests, tests))

class DeltafyTests(unittest.TestCase):
	def setUp(self):
		self.d = Deltafy(tests_dir)
		self.deltas = self.d.scan()
	
	def touch(self, file):
		open(file, 'w').write("#")
	
	file_paths = [
		os.path.join(tests_dir, 'dir1', 'file1.txt'),
		os.path.join(tests_dir, 'dir1', '.ignore', 'file1.txt'),
		os.path.join(tests_dir, 'dir1', 'subdir1', 'file1.txt'),
		os.path.join(tests_dir, 'dir1', 'subdir1', 'ignore.txt'),
		os.path.join(tests_dir, 'dir1', 'subdir1', '.ignore', 'file1.txt'),
		os.path.join(tests_dir, 'dir2', 'file1.txt') ]
	
	def touch_all_files(self):
		for file_path in self.file_paths:
			self.touch(file_path)
	
	def test_initial_pass(self):
		self.assertEquals(len(self.deltas), len(self.file_paths))
		for i in range(0,len(self.file_paths)):
			self.assertEquals(self.deltas[i].get_path(), self.file_paths[i])

	def test_second_pass(self):
		self.assertEquals(len(self.deltas), 0)
	
	def test_file_modified(self):
		file_path = os.path.join(tests_dir, 'dir1', 'subdir1', 'file1.txt')
		open(file_path, 'w').write("change")
		self.deltas = self.d.scan()
		self.assertEquals(len(self.deltas), 1)
		self.assertEquals(self.deltas[0].get_path(), file_path)
		self.assertEquals(self.deltas[0].get_status(), Delta.MODIFIED)
	
	def test_file_created(self):
		file_path = os.path.join(tests_dir, 'dir2', 'file2.txt')
		self.touch(file_path)
		self.deltas = self.d.scan()
		self.assertEquals(len(self.deltas), 1)
		self.assertEquals(self.deltas[0].get_path(), file_path)
		self.assertEquals(self.deltas[0].get_status(), Delta.CREATED)
		self.assertTrue(self.deltas.has_path(file_path))
		self.assertTrue(self.deltas.is_updated(file_path))
	
	def test_file_deleted(self):
		file_path = os.path.join(tests_dir, 'dir2', 'file2.txt')
		os.unlink(file_path)
		self.deltas = self.d.scan()
		self.assertEquals(len(self.deltas), 1)
		self.assertEquals(self.deltas[0].get_path(), file_path)
		self.assertEquals(self.deltas[0].get_status(), Delta.DELETED)
	
	def test_files_modified(self):
		# modified time resolution is 1 second
		time.sleep(1)
		self.touch_all_files()
		
		self.deltas = self.d.scan()
		self.assertEquals(len(self.deltas), len(self.file_paths))
		i = 0
		for file_path in self.file_paths:
			self.assertEquals(self.deltas[i].get_path(), file_path)
			self.assertEquals(self.deltas[i].get_status(), Delta.MODIFIED)
			i+=1
	
	def test_exclude_files(self):
		time.sleep(1)
		
		exclude_dirs = ['.ignore']
		exclude_files = ['ignore.txt']
		def include(path, isfile):
			if not isfile and os.path.basename(path) in exclude_dirs: return False
			elif isfile and os.path.basename(path) in exclude_files: return False
			return True
		
		self.d = Deltafy(tests_dir, include_callback=include)
		self.touch_all_files()
		self.deltas = self.d.scan()
		
		self.assertEquals(len(self.deltas), 3)
		self.assertEquals(self.deltas[0].get_path(), self.file_paths[0])
		self.assertEquals(self.deltas[1].get_path(), self.file_paths[2])
		self.assertEquals(self.deltas[2].get_path(), self.file_paths[5])
		
if __name__ == "__main__":
	runner = unittest.TextTestRunner()
	runner.run(suite())
