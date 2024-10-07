{
  description = "A flake for smoothies";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            python3
            nodejs
            libwebp
            (python3.withPackages (ps: with ps; [
              uvicorn
              fastapi
              pydantic
              ipython
              jinja2
              pytest
              pytest-cov
              pytest-xdist
              ipdb
              typing-extensions
            ]))
          ];
        };
      }
    );
}

