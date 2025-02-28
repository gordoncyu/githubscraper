let
  pkgs = import <nixos-unstable> { config = { allowUnfree = true; }; };
  python3Packages = pkgs.python312Packages;
  pampy = import ~/nix-derivations/pampy.nix {
    inherit (pkgs) lib stdenv;
    inherit (python3Packages) buildPythonPackage fetchPypi;
  };
  premailer = import ~/nix-derivations/premailer.nix {
    inherit (python3Packages) buildPythonPackage fetchPypi cssutils lxml cssselect requests cachetools defusedxml six;
    inherit (pkgs) lib stdenv;
  };
  yagmail = import ~/nix-derivations/yagmail.nix {
    inherit (python3Packages) buildPythonPackage fetchPypi;
    inherit (pkgs) lib stdenv;
    # Provide dependencies for yagmail if needed:
    keyring   = python3Packages.keyring;
    pyxdg     = python3Packages.pyxdg;
    # And if you have a pinned version of premailer for yagmail, pass it too, or omit if not required
    premailer = premailer;
  };

in pkgs.mkShell {
  packages = [
    (pkgs.python312.withPackages (python: [
    pkgs.python312
    python.ipython
    python.toolz
    python.numpy
    python.matplotlib
    python.tqdm
    python.pydantic
    python.pygithub
    python.returns
    python.sumtypes
    python.python-dotenv
    ]))
  ];
  buildInputs = [
    pampy
    yagmail
  ];
}
