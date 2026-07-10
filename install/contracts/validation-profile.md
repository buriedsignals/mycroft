# Mycroft install contract validation profile

The files in this directory are unsigned authoring input until Engine imports them from an immutable Mycroft commit and includes their digest in the signed catalog.

## Supported schema surface

- JSON Schema Draft 2020-12 keywords used by the checked-in schemas only.
- No network access during validation.
- No absolute, `file:`, HTTP(S), or out-of-root `$ref` values. Bundled relative references must remain under `install/contracts/`.
- No contract-supplied regular expressions, executable hooks, shell fragments, environment expansion, arithmetic, or dynamic includes.
- The template grammar has one operation: an object containing exactly `{"$input": "dotted.path"}` substitutes a previously normalized Engine input. All other JSON values are literals.

## Resource limits

- Contract files must be regular non-symlink files below `install/contracts/`.
- Maximum individual file size: 256 KiB.
- Maximum aggregate imported size: 1 MiB.
- Maximum JSON nesting depth: 32.
- Maximum JSON nodes: 20,000.
- Maximum string length: 16 KiB.
- Maximum template substitutions: 256.
- Maximum rendered config size: 256 KiB.

Engine validates these bounds before adding the contract to the signed catalog. Any new schema keyword or template operation requires a contract-version change and shared fixture coverage.
