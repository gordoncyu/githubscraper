{ lib
, stdenv
, buildPythonPackage
, fetchPypi
, keyring
, premailer
, pyxdg
}:

buildPythonPackage rec {
  pname = "yagmail";
  version = "0.15.293";
  src = fetchPypi {
    inherit pname version;
    sha256 = "sha256-ROjQzaT2PiKhSQLMkJbVIZf9DO0CPVCwQJMl9AFYUpY=";
  };
  propagatedBuildInputs = [
    keyring      # >= 15.1.0
    premailer    # >= 3.9.0
    pyxdg        # (used on Linux)
  ];
  doCheck = false;
}

