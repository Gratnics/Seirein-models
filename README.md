# Seirein-models

A curated catalog of image, embedding, speech-input, and speech models, built and maintained as part of [Seirein](https://github.com/Gratnics/Seirein) by the same creator.

This repository tracks non-text models across providers and APIs. Text-generation models are intentionally excluded; local model families and unbounded host catalogs are also excluded. The catalog is a curated API model list with structured, sourced metadata for choosing and integrating models.

The combined catalog is published at:

```
https://raw.githubusercontent.com/Gratnics/Seirein-models/main/catalog.json
```

## What's here

- **`models/<category>/<Provider>/<model>.toml`** — one TOML file per model, grouped by modality and provider. This is the source of truth; edit these files to add or update a model.
- **`catalog.json`** — every model TOML file combined into a category-keyed JSON object, generated from `models/`. Regenerate it after any change under `models/`.
- **`scripts/build_catalog.py`** — the build script that combines `models/<category>/*/*.toml` into `catalog.json`.

Categories are `image`, `embedding`, `speech-input` (audio-to-text), and `speech` (text-to-audio). The `_category` and `_source_file` fields in each JSON entry make the generated catalog self-describing and traceable.

## Providers covered

The provider set follows the Seirein AI Manager design: OpenAI, Google, Black Forest Labs, Stability AI, Ideogram, Recraft, xAI, ByteDance, Amazon Bedrock, Luma AI, Fal AI, Replicate, Fireworks AI, Together AI, DeepInfra, Vercel AI Gateway, ComfyUI, Cohere, Voyage AI, Mistral AI, OpenAI Compatible, ElevenLabs, Cartesia, Deepgram, Fish Audio, AssemblyAI, Groq, Google Vertex AI, Azure OpenAI, Gladia, Rev.ai, and OpenRouter where it already exists in the image catalog.

## Model entry schema

Each model TOML file has the following common sections:

| Section | Fields |
|---|---|
| `[model]` | `name`, `display_name`, `family`, `provider`, `release_date`, `commercial_use` |
| `[resolution]` | `max`, `min`, `arbitrary_resolution`, `aspect_ratio_control` |
| `[input]` | `file_upload`, `max_input_context`, `prompt_format` |
| `[settings]` | `has_level_settings`, `level_param_values` |
| `[output]` | `batch_supported` |
| `[pricing]` | `input`, `output` |
| `[sources]` | `urls` (list of URLs the entry's data was sourced from) |

Embedding and speech entries use the same `[model]`, `[pricing]`, and `[sources]` sections and add a compact `[capabilities]` and `[limits]` section where the provider documents those facts. Image entries retain the richer resolution/input/settings/output schema shown below.

`name` is the model's API identifier (the string you pass to the provider's API — often a raw slug or version-tagged id). `display_name` is the model's official, human-readable product name as the maker itself brands it (e.g. `name = "flux-2-pro"` / `display_name = "FLUX.2 [pro]"`). The two frequently differ; always cite `display_name` when referring to a model in prose.

Example (`models/image/OpenAI/gpt-image-2.toml`, abridged — `...` marks values shortened for this README; the real file lists every source URL in full):

```toml
[model]
name = "gpt-image-2"
display_name = "GPT Image 2"
family = "GPT Image"
provider = "OpenAI"
release_date = "2026-04-21"
commercial_use = "Customer owns Output per Business/API Service Terms; commercial use allowed; Output may not be used to develop competing AI models"

[resolution]
max = "3840x2160 (max edge 3840px, up to 8,294,400 total px)"
min = "655,360 total px min; edges multiples of 16"
arbitrary_resolution = true
aspect_ratio_control = true

[input]
file_upload = true
max_input_context = "32,000 characters"
prompt_format = "natural_language"

[settings]
has_level_settings = true
level_param_values = "quality: 'low'|'medium'|'high'|'auto' (default auto); moderation: 'low'|'auto'; input_fidelity not adjustable (always high)"

[output]
batch_supported = true

[pricing]
input = "Text $5.00/1M tok ($1.25 cached); Image $8.00/1M tok ($2.00 cached); ..."
output = "$30.00/1M image output tokens (standard); $15.00/1M (Batch)"

[sources]
urls = ["https://developers.openai.com/api/docs/models/gpt-image-2", "..."]
```

Every claim in an entry should be traceable to a URL in its `[sources]` list.

## Building the catalog

Requires Python 3.11+ (for the stdlib `tomllib`), or `tomli` on older Python.

```bash
python3 scripts/build_catalog.py
```

This rebuilds `catalog.json` from scratch out of the current `models/<category>/*/*.toml` files, so added, edited, or removed models are reflected automatically. Options:

```bash
python3 scripts/build_catalog.py --models-dir models --out catalog.json --indent 2
```

## Adding or updating a model

1. Add or edit a `models/<category>/<Provider>/<model-name>.toml` file following the schema above. The category must be one of `image`, `embedding`, `speech-input`, or `speech`, and `[model].provider` must match its parent folder name.
2. Cite every field you fill in with a source URL under `[sources].urls`.
3. Run `python3 scripts/build_catalog.py` to regenerate `catalog.json` and commit it alongside the TOML change. CI fails if `catalog.json` is out of date.

## About Seirein

[Seirein](https://github.com/Gratnics/Seirein) is a companion project by the same author. This catalog feeds Seirein's model selection, but is intended to be usable as a standalone reference by any project that needs current, sourced data on image generation model capabilities and pricing.

## License

MIT — see [LICENSE](LICENSE).
