{
  description = "Simple devshell template";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    utils.url = "github:numtide/flake-utils";
  };
  outputs = {
    nixpkgs,
    utils,
    ...
  }:
    utils.lib.eachDefaultSystem (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};
      in {
        devShell = pkgs.mkShell {
          buildInputs = with pkgs; [
            deno
            just
            ruff
            tinymist
            ty
            typescript
            typescript-language-server
            typst
            typstyle
            uv
            zathura
            libgcc.lib
            nodejs
          ];
        };
      }
    );
}
