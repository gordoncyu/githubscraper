{ lib
, stdenv
, buildPythonPackage
, fetchPypi
, cssutils
, lxml
, cssselect
, requests
, cachetools
, defusedxml
, six
}:

buildPythonPackage rec {
  pname = "premailer";
  version = "3.10.0";
  src = fetchPypi {
    inherit pname version;
    sha256 = "sha256-0YdahBH13JK1Pvnxk9tsD4edw3jWGOCtKScj44i/5MI=";
  };
  propagatedBuildInputs = [
    cssutils
    lxml
    cssselect
    requests
    cachetools
    defusedxml
    six
  ];
  doCheck = false;
}

