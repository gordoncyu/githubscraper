{ lib
, stdenv
, buildPythonPackage
, fetchPypi
}:

buildPythonPackage rec {
  pname = "pampy";
  version = "0.3.0";

  src = fetchPypi {
    inherit pname version;
    # You can get the correct sha256 by running:
    #   nix-prefetch-url --unpack https://files.pythonhosted.org/packages/.../pampy-0.3.0.tar.gz
    # and replace the dummy hash below with the output.
    sha256 = "sha256-ggVCEuRHj8IhY8VTIaNYPtqZGK/0RA7tbBl+hyoqZns=";
  };

  # If pampy has no dependencies beyond standard library, you can omit this or leave it empty:
  propagatedBuildInputs = [];

  # If there are tests but no standard test runner, you might set doCheck = false:
  doCheck = false;

  # You can also add meta information if you like:
  # meta = with lib; {
  #   homepage = "https://github.com/nbro/pampy";
  #   description = "Pampy: pattern matching for Python";
  #   license = licenses.mit;
  # };
}
