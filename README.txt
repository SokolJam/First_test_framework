# Test-Framework
Final Task of The Python Automation Courses by EPAM version 2.0. 25/08/2017

---------------------------------------------------------------------------
GENERAL USAGE NOTES
---------------------------------------------------------------------------

 - Test Framework is created by py.test architecture. It's testing Network
   File System. There is show threa differense tests, ather create the same
   way. Full list of tests you can read in "TestCase_Documentation.docx"
 - Framework inkludes prepare part, test's block and teardown. Prepare part
   consists from a check for availability nfs-utils; installation if 
   necessary, running the necessary services on the server; installing the 
   software on the client; running the necessary services on the client;
   create a shared folder on the server; determine the level of the client's
   access to the shared folder.
 - Every of tests start from mounted server share directiry to local client 
   folder. Framework's working finish a global cleaning such as remove all
   temporary file and folders, and the empty from the defoult ather settings.
----------------------------------------------------------------------------
INSTALLATION
----------------------------------------------------------------------------
  This version of test framework was made for Centos 7 (Linux) with Python 2.7.
  For a running ich of tests you must have two Linux-machin, becouse framework
  use SSH connect for the running some of steps its working.
  If you want to run all tests from the terminal, write:

    PYTHONPATH=. py.test -v

  If you want to run one of tests from the terminal, write:

    PYTHONPATH=. py.test -v -l path/test_name.py

  Ather information about parameters of PYTEST you can read on https://doc.pytest.org/
