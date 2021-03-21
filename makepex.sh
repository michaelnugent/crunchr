# build require pex package installed on top of requirements.txt for the runtime
pex . click jsonschema -c crunchr -o crunchr.pex
