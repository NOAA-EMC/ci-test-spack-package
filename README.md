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

## Authors

[Alex Richert](mailto:alexander.richert@noaa.gov)

## Usage

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

<!-- action-docs-inputs source="action.yml" -->
### Inputs

| name | description | required | default |
| --- | --- | --- | --- |
| `package-name` | <p>Spack package name to be tested (no version number or variants)</p> | `true` | `""` |
| `package-version` | <p>Version of Spack package to be tested</p> | `false` | `develop` |
| `package-variants` | <p>Variants to apply to package spec</p> | `false` | `""` |
| `custom-recipe` | <p>Path to custom recipe for package to be tested, relative to repo root</p> | `false` | `none` |
| `dependents-to-test` | <p>Spack packages to also run unit tests for (space-delimited list with variants)</p> | `false` | `""` |
| `use-common-build-cache` | <p>Use common GitHub Packages binary mirror</p> | `false` | `true` |
| `upload-artifacts` | <p>Upload certain logs on job failure (options: always, never, on-failure)</p> | `false` | `on-failure` |
| `repo-dir` | <p>Directory containing modified code to be tested (default is to download automatically)</p> | `false` | `auto` |
| `spack-ref` | <p>Spack tag/branch/commit to use</p> | `false` | `develop` |
| `cpu-target` | <p>Spack CPU target</p> | `false` | `x86_64` |
| `spack-externals` | <p>External packages for Spack to try to use</p> | `false` | `""` |
| `spack-compiler` | <p>Set spec for Spack compiler (e.g., "gcc@12")</p> | `false` | `gcc` |
| `parallel-jobs` | <p>Set number of Spack parallel install jobs ("spack install -j/--jobs")</p> | `false` | `2` |
| `spack-root` | <p>Spack root directory</p> | `false` | `spack-root` |
| `cache-secret` | <p>Secret for build cache</p> | `false` | `""` |
| `unique-id` | <p>Unique ID for artifact name</p> | `false` | `""` |
| `use-repo-cache` | <p>Enable repo-level caching</p> | `false` | `true` |
| `repo-cache-key-suffix` | <p>String to append to repo-level cache key</p> | `false` | `1` |
| `repo-save-key-suffix` | <p>Save a repo-level cache entry different from the restored one</p> | `false` | `""` |
| `cache-spack-lock` | <p>Cache spack.lock to speed up concretization</p> | `false` | `true` |
| `test-package-load` | <p>Run "spack load <package-name>" to verify setup<em>run</em>environment() does not fail</p> | `false` | `true` |
| `spack-test-flag` | <p>Flag to use for enabling install-time testing (argument to <code>spack install</code>)</p> | `false` | `--test root` |
| `save-repo-cache` | <p>Save repo cache (use-repo-cache must be true)</p> | `false` | `true` |
| `dependencies-only` | <p>Only install the requested spec's dependencies</p> | `false` | `false` |
| `package-only` | <p>Only install the requested spec (no deps; only useful for CI testing)</p> | `false` | `false` |
| `no-cached-roots` | <p>Don't install from build-cached packages for root specs</p> | `false` | `true` |
<!-- action-docs-inputs source="action.yml" -->

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
