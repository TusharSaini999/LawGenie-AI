# GitHub Template Configuration for LawGenie-AI Open Source Project

This directory contains the GitHub templates and workflows for the LawGenie-AI project.

## Contents

### `.github/pull_request_template.md`
Standard Pull Request template that guides contributors to provide comprehensive information about their changes.

### `.github/ISSUE_TEMPLATE/`
- **bug_report.md** - Template for reporting bugs
- **feature_request.md** - Template for requesting new features
- **question.md** - Template for asking questions
- **documentation.md** - Template for documentation issues
- **security.md** - Template for security vulnerabilities (for responsible disclosure)
- **config.yml** - Configuration for issue templates

### `.github/workflows/`
- **tests.yml** - Automated testing for Python and Node.js
- **code-quality.yml** - Code quality checks and linting

### `.github/FUNDING.yml`
Configuration for GitHub Sponsors and other funding options.

## How to Use

### Creating an Issue
When creating an issue, GitHub will automatically present the available templates to choose from.

### Creating a Pull Request
Contributors will see the PR template automatically when they create a pull request.

### Viewing Available Templates
All templates are available in the `.github/ISSUE_TEMPLATE/` directory.

## Customization

To customize these templates:
1. Edit the markdown files in `.github/ISSUE_TEMPLATE/`
2. Update the `pull_request_template.md` file
3. Modify the `config.yml` to disable/enable templates or add contact links
4. Update workflows as needed for your CI/CD pipeline

## References
- [GitHub Issue Templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests)
- [GitHub Pull Request Templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository)
- [GitHub Workflows](https://docs.github.com/en/actions)
