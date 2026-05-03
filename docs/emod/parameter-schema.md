# Parameter schema

A schema defines all configuration and campaign parameters available in the installed
version of EMOD, for all simulation types. It includes parameter names, data types,
defaults, valid ranges, and short descriptions. Note that the schema does not include
demographics parameters. The schema is a JSON file and can be opened in any text editor.

In most cases, you will not need to work with the schema directly — emodpy-hiv handles
all model configuration through its Python API and uses the schema internally.

If you do need access to the schema, the EMOD executable and its associated schema are
bundled in the `emod_hiv` package, which is installed automatically when you install
emodpy-hiv. You can extract them using the `emod_hiv.bootstrap` module. Add the
following to your project and run it once:

```python
if __name__ == "__main__":
    import emod_hiv.bootstrap as bootstrap
    import pathlib
    bootstrap.setup(pathlib.Path("executables"))
```

This will download and place the EMOD executable and schema files into an
`executables` folder in your current directory.
