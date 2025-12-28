# GitHub CI Action: test-spack-package

![Test action](https://github.com/NOAA-EMC/ci-test-spack-package/actions/workflows/test-action.yml/badge.svg)

This repository provides a GitHub Action for building and testing packages
through the [Spack package manager](https://spack.io). It achieves this by
[setting up Spack](https://github.com/spack/setup-spack) and setting up the
modified code to be tested using the `spack develop` command. The code is
installed and tested through the `spack install --test` command, which will
therefore work with any build system providing a `make test` or `make check`
target (see [Spack
documentation](https://spack.readthedocs.io/en/latest/packaging_guide.html)). It
is recommended to include a custom `check()` function in the recipe to ensure
that the appropriate target is run, as the generic test functionality in Spack
does not fail when the `test` and `check` targets do not exist.

This repository supports [NCEPLIBS](https://github.com/NOAA-EMC/NCEPLIBS) CI
workflows.

Features:
- Build caching of dependencies through GitHub Packages (enabled by default)
- Supports compiling and unit testing downstream dependents through Spack to
  enhance code testing
- Supports custom Spack recipes (must be contained within the same repository),
  which allows for packages to be tested that do not exist in the Spack
  repository

To submit bug reports, feature requests, or other code-related issues including
usage questions, please create a [GitHub
issue](https://github.com/NOAA-EMC/ci-test-spack-package/issues). For general
NCEPLIBS inquiries, contact [Alex Richert](mailto:alexander.richert@noaa.gov)
(secondary point of contact [Hang Lei](mailto:hang.lei@noaa.gov)).

### Authors

[Alex Richert](mailto:alexander.richert@noaa.gov)

### Usage

To use this Action, include the following step in your GitHub Actions workflow
for a code to be built and tested as a Spack package:
```
    - name: "Test with Spack"
      uses: NOAA-EMC/ci-test-spack-package@develop
      with:
        package-name: foo
        package-variants: ${{ matrix.variants-to-test }}
        spack-compiler: gcc@11
        cache-secret: ${{ secrets.my-build-cache-secret }}
        custom-recipe: spack/package.py
        spack-ref: v0.21.2
```

See `action.yml` for the full list of available options and their defaults.

In order to use the repo-level caching of compiled packages, `permissions:actions:write`
must be set at the job level (this enables an existing cache to be deleted and
overwritten).

## Disclaimer

The United States Department of Commerce (DOC) GitHub project code is provided
on an "as is" basis and the user assumes responsibility for its use. DOC has
relinquished control of the information and no longer has responsibility to
protect the integrity, confidentiality, or availability of the information. Any
claims against the Department of Commerce stemming from the use of its GitHub
project will be governed by all applicable Federal law. Any reference to
specific commercial products, processes, or services by service mark, trademark,
manufacturer, or otherwise, does not constitute or imply their endorsement,
recommendation or favoring by the Department of Commerce. The Department of
Commerce seal and logo, or the seal and logo of a DOC bureau, shall not be used
in any manner to imply endorsement of any commercial product or activity by DOC
or the United States Government.
