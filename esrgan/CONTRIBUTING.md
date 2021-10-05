# Contributing to Real-ESRGAN

We like open-source and want to develop practical algorithms for general image restoration. However, individual strength is limited. So, any kinds of contributions are welcome, such as:

- New features
- New models (your fine-tuned models)
- Bug fixes
- Typo fixes
- Suggestions
- Maintenance
- Documents
- *etc*

## Workflow

1. Fork and pull the latest Real-ESRGAN repository
1. Checkout a new branch (do not use master branch for PRs)
1. Commit your changes
1. Create a PR

**Note**:
1. Please check the code style and linting
    1. The style configuration is specified in [setup.cfg](setup.cfg)
    1. If you use VSCode, the settings are configured in [.vscode/settings.json](.vscode/settings.json)
1. Strongly recommend using `pre-commit hook`. It will check your code style and linting before your commit.
    1. In the root path of project folder, run `pre-commit install`
    1. The pre-commit configuration is listed in [.pre-commit-config.yaml](.pre-commit-config.yaml)
1. Better to [open a discussion](https://github.com/xinntao/Real-ESRGAN/discussions) before large changes.
    1. Welcome to discuss :sunglasses:. I will try my best to join the discussion.

## TODO List

:zero: The most straightforward way of improving model performance is to fine-tune on some specific datasets.

Here are some TODOs:

- [ ] optimize for human faces
- [ ] optimize for texts
- [ ] support controllable restoration strength

:one: There are also [several issues](https://github.com/xinntao/Real-ESRGAN/issues) that require helpers to improve. If you can help, please let me know :smile:

## Contributors

- [AK391](https://github.com/AK391): Integrate RealESRGAN to [Huggingface Spaces](https://huggingface.co/spaces) with [Gradio](https://github.com/gradio-app/gradio). See [Gradio Web Demo](https://huggingface.co/spaces/akhaliq/Real-ESRGAN).
