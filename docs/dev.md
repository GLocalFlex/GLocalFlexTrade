# Development

## Poetry

    export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring

## Docs

Publish docs to GitHub Pages:

    mike deploy -r github --push --update-aliases v0.2 latest
