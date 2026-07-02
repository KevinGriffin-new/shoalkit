# Contributing to shoalkit

Thanks for your interest in shoalkit. Bug reports, corrections to the physics,
and small focused pull requests are all welcome.

## Reporting bugs and requesting features

Open an issue: https://github.com/KevinGriffin-new/shoalkit/issues

A good report includes:

- what you ran (the `shoalkit` call, with `H`, `T`, `h`, etc.),
- what you expected and what you got,
- your Python version and shoalkit version (`python -c "import shoalkit; print(shoalkit.__version__)"`).

For a physics discrepancy, a reference (textbook page, paper + equation, or a
known analytic limit) makes the report much faster to act on — shoalkit aims to
reproduce established wave theory, so "this disagrees with source X" is the most
useful framing.

## Development setup

The core library is pure standard library; the optional extras pull in the tools
used for the nonlinear cross-checks, the example animation, and linting.

```bash
git clone https://github.com/KevinGriffin-new/shoalkit
cd shoalkit
python -m pip install -e ".[dev]"     # pytest + raschii + numpy + ruff
```

Optional-dependency groups:

- `test` — pytest only
- `nonlinear` — `raschii` + `numpy`, for the higher-order Stokes / Fenton
  cross-check tests
- `viz` — `numpy` + `matplotlib`, for `examples/drift_animation.py`
- `dev` — everything above plus `ruff`

## Running the tests

```bash
pytest -q
```

`pyproject.toml` puts `src/` on the path, so no `PYTHONPATH` juggling is needed.
The suite includes analytic checks (dispersion, Ursell gating, Stokes drift
limits and identities) and, when `raschii` is installed, cross-checks of the
analytic surface profiles against an independent nonlinear solver. Tests that
need `raschii` skip cleanly when it is absent.

Please add a test for any new behaviour or bug fix. Where possible, anchor it to
something checkable — a closed-form limit, a conservation identity, or agreement
with a cited reference — rather than a hard-coded expected number.

## Style

```bash
ruff check .
```

Keep the core dependency-free: new functionality in the core modules should rely
only on the standard library. If a feature genuinely needs `numpy`/`raschii`,
gate it behind the relevant optional extra and skip its tests when the extra is
absent, following the pattern in `tests/`.

## Pull requests

- Branch from `main`, keep each PR to one logical change.
- Make sure `pytest -q` passes and `ruff check .` is clean; CI runs both on
  Python 3.9–3.12.
- Describe the change and, for anything touching the physics, cite the theory it
  implements or corrects.

## Code of conduct

Be respectful and constructive. Harassment or abusive behaviour is not welcome
in the issue tracker or pull requests.

## License

By contributing, you agree that your contributions are licensed under the
project's [MIT License](LICENSE).
