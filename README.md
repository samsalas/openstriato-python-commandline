# openstriato-python-commandline
My contribution to the project OpenStriato, a python package to use "openstriato -arg argument...". This package will be used to control the Raspberry with NFC tags.
# Static Analysis
This project uses PyLint. To use PyLint install the package (pip install pylint) and run<br />
<code>$pylint -f parseable file.py</code>
# Tests
This project uses Nose. To use Nose install the package (pip install nose) and run<br />
<code>$nosetests -v file.py</code><br />
You can edit XML reports in JUnit and Cobertura. For example, you can associate a continuous integration tool. Just run<br />
<code>$nosetests -v file.py -xunit -xcoverage</code>
