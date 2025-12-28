# Contributing Guide

Thank you for your interest in contributing to this project! This document provides guidelines and the process for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Pull Requests](#pull-requests)
- [Development Standards](#development-standards)
  - [Code Style](#code-style)
  - [Commits](#commits)
  - [Testing](#testing)
- [Review Process](#review-process)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and welcoming environment for all contributors.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with the following information:

1. **Clear problem description**: Explain what is happening and what you expected to happen.
2. **Steps to reproduce**: Provide detailed steps to reproduce the bug.
3. **Expected behavior**: Describe what should happen instead of the bug.
4. **Environment**:
   - Node.js version
   - AWS SAM CLI version
   - Operating system
   - AWS Region (if relevant)
5. **Relevant logs**: If there are errors in the logs, include them (make sure to sanitize sensitive information).
6. **Screenshots**: Include them if relevant.

**Bug Report Template:**

```markdown
## Bug Description
[Clear and concise description of the bug]

## Steps to Reproduce
1. ...
2. ...
3. ...

## Expected Behavior
[What should happen]

## Environment
- Node.js: [version]
- AWS SAM CLI: [version]
- OS: [operating system]
- AWS Region: [region]

## Logs
[Relevant logs, sanitized]
```

### Suggesting Enhancements

Enhancement suggestions are welcome. When creating an issue for an enhancement:

1. **Clear description**: Explain the proposed enhancement and why it would be useful.
2. **Use case**: Describe the use case or problem it would solve.
3. **Alternatives considered**: If you've considered other solutions, mention them.
4. **Additional information**: Any other relevant information.

**Enhancement Issue Template:**

```markdown
## Enhancement Description
[Clear description of the proposed enhancement]

## Use Case
[What problem it solves or what functionality it adds]

## Alternatives Considered
[Other solutions you considered]

## Additional Information
[Any other relevant information]
```

### Pull Requests

1. **Fork the repository** and clone it locally.
2. **Create a branch** for your feature or fix:
   ```sh
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-fix-description
   ```
3. **Make your changes** following the [development standards](#development-standards).
4. **Test your changes** locally.
5. **Commit your changes** with descriptive messages (see [Commits](#commits)).
6. **Push to your fork**:
   ```sh
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request** on GitHub with:
   - Clear description of the changes
   - Reference to the related issue (if applicable)
   - Screenshots or examples (if applicable)

## Development Standards

### Code Style

- **Language**: All code and comments must be in English.
- **Node.js**: Use Node.js 22.x (LTS).
- **Format**: Follow standard JavaScript/Node.js conventions.
- **Environment Variables**: All variables must have default values and be documented.
- **AWS Resource Names**: Follow the standards defined in the project rules:
  - Use `AWS::StackName` for resource names
  - Format: `<environment>-<project>-<functionality>`
  - All lowercase, no accents or special characters

### Commits

Use clear and descriptive commit messages:

**Format:**
```
<type>(<scope>): <short description>

<optional detailed description>

<optional issue references>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting changes (do not affect functionality)
- `refactor`: Code refactoring
- `test`: Add or modify tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(logging): add log sanitization feature

Adds ENABLE_SANITIZATION environment variable to control
sensitive data redaction in logs. Defaults to true for security.

Closes #123
```

```
fix(sanitization): prevent redaction of numeric counters

Fixes issue where numeric fields like keysEvaluated were being
redacted. Now only string values matching sensitive patterns are redacted.
```

### Testing

Before submitting a PR:

1. **Test locally**:
   ```sh
   sam build
   sam local invoke RenewAppSyncApiKeyFunction
   ```

2. **Validate the template**:
   ```sh
   sam validate
   ```

3. **Check linting** (if configured):
   ```sh
   npm run lint
   ```

4. **Test the deployment** in a development environment before merging.

### Code Structure

- **Lambda Functions**: Located in `src/renew-appsync-api-key/`
- **Templates**: `template.yaml` in the root
- **Documentation**: `README.md` in the root

### Environment Variables

All environment variables must:
- Have a default value
- Be documented in `template.yaml` with comments
- Be documented in `README.md`
- Use UPPERCASE names with SNAKE_CASE

## Review Process

1. **Automatic review**: PRs go through automatic checks (if configured).
2. **Code review**: At least one maintainer will review your PR.
3. **Feedback**: There may be change requests. Please respond to comments.
4. **Approval**: Once approved, a maintainer will merge the PR.

### PR Checklist

Before requesting review, make sure:

- [ ] Code follows project standards
- [ ] Comments are in English
- [ ] Environment variables have default values
- [ ] Code has been tested locally
- [ ] Documentation has been updated (if applicable)
- [ ] Commits have descriptive messages
- [ ] No sensitive information in code or logs
- [ ] SAM template is valid

## Questions

If you have questions about how to contribute, you can:
- Open an issue with the `question` label
- Contact the project maintainers

## Acknowledgments

Thank you for contributing to this project! Your help is very valuable.
