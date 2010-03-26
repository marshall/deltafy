Deltafy is a python library that aims to make querying the changes in a given file tree very simple.

All you need to do is pass Deltafy the root directory of your file tree, and scan() it whenever you want to know about new changes in the filesystem. Deltafy automatically stores the last known "scan state" in a local sqlite database, so you can know what's changed since the last time you scanned. 

Keep in mind that the initial scan on each system will return a full list of "CREATED" deltas , you might want to seed it by running deltafy.py directly.

Basic Example
----
<code>
from deltafy import *
import time

# seed the db
myproject = Deltafy("/myproject")
myproject.scan()

# wait for a background service to change some files in myproject
time.sleep(10)

deltas = myproject.scan()
for delta in deltas:
	# the timestamp as a datetime object:
	timestamp = delta.get_timestamp()
	# the path
	path = delta.get_path()
	
	# the delta status	
	if delta.get_status() == Delta.CREATED:
		# handle created (since the last scan) files
		pass
	elif delta.get_status() == Delta.DELETED:
		# handle deleted (since the last scan) files
		pass
	elif delta.get_status() == Delta.MODIFIED:
		# handle modified (since the last scan) files
		pass

	# you can also get status as a string
	status_str = delta.get_status_str()

# check if a certain path changed
if deltas.has_path("/myproject/file.xml"):
	# generate code from xml..
	pass
</code>

Advanced Example
----
<code>
from deltafy import *
import os

# you can use a custom handler to only scan certain files/directories
# here we only want xml files or files under any "descriptors" directory
def xmlincluder(path, isfile):
	if isfile and os.path.basename(path).endswith(".xml"): return True
	elif !isfile and os.path.basename(path) == "descriptors": return True
	return False

myproject = Deltafy("/myproject", xmlincluder)
</code>

If you're looking for more, you can also run and read the testsuite under tests/tests.py.
